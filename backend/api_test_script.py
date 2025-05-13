import requests
import json

BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "email": "testuser@example.com",
    "phone_number": "1234567890",
    "password": "testpassword123",
    "password2": "testpassword123"
}

access_token = None
user_id = None

def print_response(response, action):
    print(f"\n--- {action} ---")
    try:
        print(f"Status Code: {response.status_code}")
        print(f"Response JSON: {response.json()}")
    except requests.exceptions.JSONDecodeError:
        print(f"Response Text: {response.text}")

def register_user():
    global user_id
    print("Attempting to register a new user...")
    response = requests.post(f"{BASE_URL}/users/register/", data=TEST_USER)
    print_response(response, "User Registration")
    if response.status_code == 201:
        print("User registration successful.")
        return True
    elif response.status_code == 400 and response.json().get("email") and "user with this email already exists" in response.json().get("email", [])[0].lower():
        print("User already exists, proceeding to login.")
        return True
    elif response.status_code == 400 and response.json().get("phone_number") and "user with this phone number already exists" in response.json().get("phone_number", [])[0].lower():
        print("User with this phone number already exists, proceeding to login.")
        return True
    else:
        print("User registration failed.")
        return False

def login_user():
    global access_token, user_id
    print("Attempting to log in...")
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    response = requests.post(f"{BASE_URL}/users/login/", data=login_data)
    print_response(response, "User Login")
    if response.status_code == 200:
        access_token = response.json().get("access")
        print(f"Login successful. Access Token: {access_token}")
        headers = {"Authorization": f"Bearer {access_token}"}
        # Try to get user ID from personal profile first
        profile_response = requests.get(f"{BASE_URL}/users/personal-profile/", headers=headers)
        if profile_response.status_code == 200:
            profile_data_json = profile_response.json()
            user_field_from_profile = profile_data_json.get("user")
            if isinstance(user_field_from_profile, int):
                user_id = user_field_from_profile
                print(f"User ID obtained from personal profile (direct ID): {user_id}")
            elif isinstance(user_field_from_profile, dict) and "id" in user_field_from_profile:
                user_id = user_field_from_profile.get("id")
                print(f"User ID obtained from personal profile (nested ID): {user_id}")
            else:
                print(f"User ID in personal profile response is in an unexpected format: {user_field_from_profile}")
                user_id = None
        else:
            print(f"Failed to fetch personal profile to get user ID. Status: {profile_response.status_code}")
            # Fallback: try to get user ID from professional profile /me endpoint
            prof_profile_response = requests.get(f"{BASE_URL}/professional/profiles/professional/me/", headers=headers) 
            if prof_profile_response.status_code == 200:
                prof_profile_data_json = prof_profile_response.json()
                user_field_from_prof_profile = prof_profile_data_json.get("user")
                if isinstance(user_field_from_prof_profile, int):
                    user_id = user_field_from_prof_profile
                    print(f"User ID obtained from professional profile /me/ (direct ID): {user_id}")
                elif isinstance(user_field_from_prof_profile, dict) and "id" in user_field_from_prof_profile:
                    user_id = user_field_from_prof_profile.get("id")
                    print(f"User ID obtained from professional profile /me/ (nested ID): {user_id}")
                else:
                    print(f"User ID in professional profile /me/ response is in an unexpected format: {user_field_from_prof_profile}")
                    user_id = None
            else:
                print(f"Could not obtain user ID after login. Personal profile response: {profile_response.status_code}, Professional profile /me/ response: {prof_profile_response.status_code}")
        return True
    else:
        print("Login failed.")
        return False

def create_community():
    if not access_token:
        print("No access token. Skipping create community.")
        return None
    print("Attempting to create a community...")
    headers = {"Authorization": f"Bearer {access_token}"}
    community_data = {
        "name": "Test Community",
        "description": "A community for testing purposes.",
        "is_private": False,
        "requires_approval": False
    }
    response = requests.post(f"{BASE_URL}/personal/communities/", headers=headers, json=community_data)
    print_response(response, "Create Community")
    if response.status_code == 201:
        print("Community created successfully.")
        return response.json().get("id")
    else:
        print(f"Failed to create community. Status: {response.status_code}. Attempting to find existing...")
        list_response = requests.get(f"{BASE_URL}/personal/communities/?name=Test Community", headers=headers)
        if list_response.status_code == 200 and list_response.json():
            communities = list_response.json()
            if isinstance(communities, list) and len(communities) > 0:
                 existing_community = next((c for c in communities if c["name"] == "Test Community"), None)
                 if existing_community:
                    print("Found existing community by name.")
                    return existing_community["id"]
        print("Could not find existing community either.")
        return None

def create_post(community_id):
    if not access_token or not community_id:
        print("No access token or community ID. Skipping create post.")
        return None
    print(f"Attempting to create a post in community {community_id}...")
    headers = {"Authorization": f"Bearer {access_token}"}
    post_data = {
        "title": "My Test Post",
        "content": "This is the content of my test post.",
        "community": community_id
    }
    response = requests.post(f"{BASE_URL}/personal/communities/{community_id}/posts/", headers=headers, json=post_data)
    print_response(response, "Create Post")
    if response.status_code == 201:
        print("Post created successfully.")
        return response.json().get("id")
    else:
        print("Failed to create post.")
        return None

def update_personal_profile():
    if not access_token:
        print("No access token. Skipping update personal profile.")
        return
    print("Attempting to update personal profile...")
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_data = {
        "full_name": "Test User Full Name Updated",
        "bio": "This is an updated test bio."
    }
    response = requests.put(f"{BASE_URL}/users/personal-profile/", headers=headers, json=profile_data)
    print_response(response, "Update Personal Profile")
    if response.status_code == 200:
        print("Personal profile updated successfully.")
    else:
        print("Failed to update personal profile.")

def update_professional_profile():
    if not access_token:
        print("No access token. Skipping update professional profile.")
        return
    print("Attempting to update professional profile (detailed)...")
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_data = {
        "headline": "Updated Test Professional Headline",
        "summary": "This is an updated test summary for professional profile.",
        "work_experience": [{"title": "Senior Test Engineer", "company": "TestCorp Inc"}],
        "education": [{"degree": "MSc Test", "school": "Test University Advanced"}]
    }
    response = requests.put(f"{BASE_URL}/professional/profiles/professional/me/update/", headers=headers, json=profile_data)
    print_response(response, "Update Detailed Professional Profile")
    if response.status_code == 200:
        print("Detailed professional profile updated successfully.")
    else:
        print("Failed to update detailed professional profile.")

def create_business_profile():
    if not access_token:
        print("No access token. Skipping create business profile.")
        return None
    print("Attempting to create a business profile...")
    headers = {"Authorization": f"Bearer {access_token}"}
    business_data = {
        "company_name": "Test Business Inc. Unique",
        "industry": "Advanced Technology",
        "company_size": "11-50 employees",
        "is_startup": False
    }
    response = requests.post(f"{BASE_URL}/professional/profiles/business/", headers=headers, json=business_data)
    print_response(response, "Create Business Profile")
    if response.status_code == 201:
        print("Business profile created successfully.")
        return response.json().get("id")
    else:
        print(f"Failed to create business profile. Status: {response.status_code}. Attempting to find existing...")
        list_response = requests.get(f"{BASE_URL}/professional/profiles/business/?company_name=Test Business Inc. Unique", headers=headers)
        if list_response.status_code == 200 and list_response.json():
            profiles = list_response.json()
            if isinstance(profiles, list) and len(profiles) > 0:
                print("Found existing business profile by name.")
                return profiles[0]["id"]
        print("Could not find existing business profile either.")
        return None

def create_job_listing(business_profile_id):
    if not access_token or not business_profile_id:
        print("No access token or business profile ID. Skipping create job listing.")
        return None
    print(f"Attempting to create a job listing for business {business_profile_id}...")
    headers = {"Authorization": f"Bearer {access_token}"}
    job_data = {
        "title": "Senior Test Software Engineer",
        "description": "Looking for an experienced test software engineer.",
        "location": "Hybrid",
        "employment_type": "FULL_TIME",
        "posted_by_business_id": business_profile_id
    }
    response = requests.post(f"{BASE_URL}/professional/jobs/listings/", headers=headers, json=job_data)
    print_response(response, "Create Job Listing")
    if response.status_code == 201:
        print("Job listing created successfully.")
        return response.json().get("id")
    else:
        print("Failed to create job listing.")
        return None

def apply_for_job(job_listing_id):
    if not access_token or not job_listing_id:
        print("No access token or job listing ID. Skipping apply for job.")
        return
    print(f"Attempting to apply for job {job_listing_id}...")
    headers = {"Authorization": f"Bearer {access_token}"}
    application_data = {
        "cover_letter": "I am very interested in this senior test position."
    }
    response = requests.post(f"{BASE_URL}/professional/jobs/listings/{job_listing_id}/apply/", headers=headers, json=application_data)
    print_response(response, "Apply for Job")
    if response.status_code == 201:
        print("Successfully applied for the job.")
    elif response.status_code == 400 and response.json().get("detail", "").startswith("You have already applied"):
        print("Already applied for this job.")
    else:
        print("Failed to apply for the job.")

def get_or_create_direct_chat(other_user_id_to_chat_with):
    if not access_token or not other_user_id_to_chat_with:
        print("No access token or other_user_id. Skipping get/create direct chat.")
        return None
    print(f"Attempting to get or create direct chat with user {other_user_id_to_chat_with}...")
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"other_user_id": other_user_id_to_chat_with}
    response = requests.post(f"{BASE_URL}/chat/direct/", headers=headers, json=data)
    print_response(response, "Get or Create Direct Chat")
    if response.status_code in [200, 201]:
        print("Direct chat room obtained/created successfully.")
        return response.json().get("id")
    else:
        print("Failed to get or create direct chat room.")
        return None

if __name__ == "__main__":
    if register_user():
        if login_user():
            update_personal_profile()
            update_professional_profile()
            community_id = create_community()
            if community_id:
                create_post(community_id)
            business_id = create_business_profile()
            if business_id:
                job_id = create_job_listing(business_id)
                if job_id:
                    apply_for_job(job_id)
            if user_id:
                admin_user_id = 1 
                if user_id == admin_user_id:
                    print("Skipping self-chat test as current user is admin.")
                else:
                    get_or_create_direct_chat(admin_user_id)
            else:
                print("Skipping chat test as current user ID could not be obtained.")
            print("\n--- API Test Script Completed ---")
        else:
            print("Login failed. Aborting further tests.")
    else:
        print("Registration failed or user already exists and login will be attempted. If login fails, script aborts.")

