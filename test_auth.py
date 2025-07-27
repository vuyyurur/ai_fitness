from system.auth_manager import signup_user

email = "your_test2_email@example.com"
password = "2yourStrongPassword123"
display_name = "Revanth2"

uid = signup_user(email, password, display_name)

if uid:
    print(f" User created successfully with UID: {uid}")
else:
    print("Failed to create user.")
