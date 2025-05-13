# Minara Backend MVP - README

## 1. Project Overview

Minara is a social application with two main components: Minara Personal and Minara Professional. This backend MVP implements the core functionalities for both, providing a RESTful API for client applications (like the planned iOS app) to interact with.

The backend is built using Python and the Django framework, with Django REST Framework for API development. It uses SQLite for the database in this MVP phase for ease of setup and development.

## 2. Features Implemented

### Minara Personal

*   **User Management:**
    *   User registration (email, phone number, password).
    *   User login (email, password) with JWT authentication.
    *   Personal profile creation and updates (full name, bio).
*   **Communities Function (akin to Reddit - Partial Implementation):**
    *   Models for Communities, Posts, Comments, Votes, and Community Creation Requests are in place.
    *   API endpoints for listing and retrieving communities are available.
    *   **Known Issue:** Creating new communities currently results in a 500 Internal Server Error. This needs further investigation.
    *   Joining/leaving communities, posting, and commenting functionalities are designed but may be affected by the creation issue.
*   **Chat Function (akin to WhatsApp - Backend Foundation):**
    *   Django Channels is integrated for WebSocket support.
    *   Models for Chat Rooms (Direct Messages) and Messages are defined.
    *   API endpoint to get or create a direct chat room between two users.
    *   Real-time message exchange via WebSockets is set up (consumers defined).
*   **Home Page / Personal Feed (akin to Instagram - Backend Foundation):**
    *   Users can create personal posts (text-based for MVP, image support can be added).
    *   Users can follow/unfollow other users.
    *   API endpoint to retrieve a feed of posts from users they follow.

### Minara Professional

*   **Professional Profiles (akin to LinkedIn - Basics):**
    *   Users have a professional profile linked to their main account.
    *   Can store headline, summary, work experience, education.
    *   API endpoints for retrieving and updating the user's own professional profile.
    *   Business Profiles can be created and managed by users.
*   **Job Board (akin to LinkedIn - Basics):**
    *   Businesses (via Business Profiles) can post job listings (title, description, location, employment type).
    *   Users can view job listings.
    *   Users can apply for jobs ("Easy Apply" style with a cover letter).
*   **Status Indicators (Referrals, Mentor/Mentee, Startup/VC - Model Fields):**
    *   Fields for these statuses are present in the `ProfessionalProfile` and `BusinessProfile` models.
    *   API exposure for updating/filtering by these is basic and can be expanded.
*   **Business Segment (Funding - Basic Models):**
    *   Models for `FundingOpportunity` (posted by VCs/Businesses) and `FundingRequest` (posted by Startups) are defined.
    *   Basic API endpoints for CRUD operations on these are available.
*   **Professional Feed (Basic Model):**
    *   A `ProfessionalFeedPost` model exists for professional content sharing.
    *   Basic API endpoints for CRUD operations are available.

## 3. Technology Stack

*   **Backend Framework:** Django & Django REST Framework
*   **Programming Language:** Python
*   **Database:** SQLite (for MVP development)
*   **Real-time Communication:** Django Channels & Daphne (for WebSockets)
*   **Authentication:** JWT (JSON Web Tokens) via `djangorestframework-simplejwt`
*   **Dependencies:** See `requirements.txt`

## 4. Setup and Installation

1.  **Prerequisites:**
    *   Python 3.11+ (as used in the development environment)
    *   `pip` (Python package installer)

2.  **Clone/Download the Backend Code:**
    *   Extract the provided `minara_backend.zip` to a directory of your choice.

3.  **Navigate to the Backend Directory:**
    ```bash
    cd path/to/your/minara_app/backend
    ```

4.  **Create a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

5.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Apply Database Migrations:**
    ```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```

7.  **Create a Superuser (Optional, for Admin Panel Access & Testing):**
    ```bash
    python3 manage.py createsuperuser
    ```
    Follow the prompts to create an admin user.

## 5. Running the Backend Server

Once setup is complete, you can run the Django development server:

```bash
python3 manage.py runserver 0.0.0.0:8000
```

The backend API will then be accessible at `http://localhost:8000/api/`.
The Django admin panel will be at `http://localhost:8000/admin/` (if superuser created).

For WebSocket connections (chat), the ASGI server (Daphne) will handle requests. The `runserver` command with Django Channels automatically uses Daphne in development.

## 6. API Endpoint Overview

Key API endpoints are structured under `/api/`:

*   `/api/users/register/`
*   `/api/users/login/`
*   `/api/users/personal-profile/`
*   `/api/personal/communities/`
*   `/api/personal/communities/{id}/posts/`
*   `/api/chat/direct/` (for creating/getting direct message rooms)
*   `/api/professional/profiles/professional/me/`
*   `/api/professional/profiles/business/`
*   `/api/professional/jobs/listings/`
*   `/api/professional/jobs/listings/{id}/apply/`

Detailed URL patterns can be found in the `urls.py` files within each app (`users`, `personal_app`, `chat_app`, `professional_app`) and the main `minara_backend/urls.py`.

## 7. Known Limitations & Issues (MVP)

*   **Community Creation:** Creating new communities via the API (`POST /api/personal/communities/`) currently results in a 500 Internal Server Error. This is the most significant known issue.
*   **Personal Profile Update:** The API test script indicated a failure when attempting to update the personal profile (`PUT /api/users/personal-profile/`). While the endpoint exists, the update operation might not be fully functional or the test script had an issue.
*   **User ID in Profile Responses:** The `user` field in some profile-related API responses (e.g., personal profile) returns a direct integer ID, while in others it might be a nested object. Client applications should be prepared to handle this. The test script was adjusted for the direct ID case for personal profiles.
*   **Limited Test Coverage:** While an API test script (`api_test_script.py`) was used for basic validation, comprehensive unit and integration tests are not yet implemented.
*   **iOS Frontend:** The iOS frontend development was not started as part of this backend-focused MVP delivery.
*   **Error Handling & Validation:** Error handling and input validation are at a basic level and can be significantly enhanced.
*   **Scalability & Production Readiness:** The current setup (SQLite, development server settings) is for MVP development and not production-ready. For production, transitioning to PostgreSQL, using a production-grade ASGI/WSGI server (like Gunicorn + Daphne/Uvicorn), and adjusting Django settings (e.g., `DEBUG=False`) would be necessary.
*   **Security:** Security considerations (e.g., rate limiting, advanced permissions, input sanitization beyond Django/DRF defaults) are basic for this MVP.

Please refer to `KNOWN_ISSUES.md` for a more focused list of active issues.

## 8. Project Structure (Backend)

```
minara_app/
└── backend/
    ├── minara_backend/  # Main Django project settings, ASGI/WSGI, root URLs
    ├── users/           # User registration, login, core profiles
    ├── personal_app/    # Communities, personal posts, feed (Minara Personal)
    ├── chat_app/        # Chat rooms, messages, WebSocket consumers
    ├── professional_app/ # Professional profiles, jobs, funding (Minara Professional)
    ├── manage.py        # Django management script
    ├── requirements.txt # Python dependencies
    ├── api_test_script.py # Basic API test script
    ├── create_superuser.py # Script to create superuser (used during dev)
    └── db.sqlite3       # SQLite database file (created after migrations)
```

This README provides a starting point for understanding and running the Minara backend MVP.

