from django.contrib.auth import get_user_model

User = get_user_model()

email = "admin@minara.com"
phone_number = "0000000000" # Using a placeholder valid phone number
password = "adminpassword"

if not User.objects.filter(email=email).exists():
    try:
        User.objects.create_superuser(email=email, phone_number=phone_number, password=password)
        print(f"Superuser {email} created successfully.")
    except Exception as e:
        print(f"Error creating superuser: {e}")
else:
    print(f"Superuser {email} already exists.")

