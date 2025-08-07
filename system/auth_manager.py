
import firebase_admin
from firebase_admin import credentials, auth as admin_auth, firestore
import pyrebase
import requests
from system.firebase_config import firebase_config  # This should contain the Pyrebase config

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

firebase = pyrebase.initialize_app(firebase_config)
pyre_auth = firebase.auth()

def signup_user(email, password, display_name=None):
    try:
        user = admin_auth.create_user(
            email=email,
            password=password,
            display_name=display_name or email.split('@')[0]
        )
        print(f"Successfully created user: {user.uid}")

        # Store in Firestore
        db.collection("users").document(user.uid).set({
            "email": email,
            "display_name": display_name or email.split('@')[0],
            "created_at": firestore.SERVER_TIMESTAMP
        })

        return user.uid
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_config['apiKey']}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print("Login successful!")
        return data 
    except requests.exceptions.HTTPError as e:
        error = e.response.json()
        print(f"Login failed: {error['error']['message']}")
        return None

def get_user_data(uid):
    try:
        doc = db.collection("users").document(uid).get()
        if doc.exists:
            return doc.to_dict()
        else:
            print("No such user.")
            return None
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return None

