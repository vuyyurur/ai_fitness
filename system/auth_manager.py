""" import firebase_admin
from firebase_admin import credentials, auth, firestore

# Initialize Firebase Admin
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()

def signup_user(email, password, display_name=None):
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name or email.split('@')[0]
        )
        print(f"✅ Successfully created user: {user.uid}")

        # Optionally store user profile in Firestore
        db.collection("users").document(user.uid).set({
            "email": email,
            "display_name": display_name or email.split('@')[0],
            "created_at": firestore.SERVER_TIMESTAMP
        })

        return user.uid
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

def login_user(email, password):
    # firebase-admin does NOT support login/password auth client-side.
    # Use Firebase Authentication via REST API or a frontend (e.g. PyQt login form).
    print("❌ Login with email/password is not supported via firebase-admin.")
    print("➡️ Use Pyrebase or REST API for client-side login if needed.")
    return None

def get_user_data(uid):
    try:
        doc = db.collection("users").document(uid).get()
        if doc.exists:
            return doc.to_dict()
        else:
            print("⚠️ No such user.")
            return None
    except Exception as e:
        print(f"❌ Error fetching user data: {e}")
        return None
 """
import firebase_admin
from firebase_admin import credentials, auth as admin_auth, firestore
import pyrebase
import requests
from system.firebase_config import firebase_config  # This should contain the Pyrebase config

# Initialize Firebase Admin SDK (for signup + Firestore)
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize Pyrebase Auth (for client-side login)
firebase = pyrebase.initialize_app(firebase_config)
pyre_auth = firebase.auth()

# ✅ Signup user (firebase-admin + Firestore)
def signup_user(email, password, display_name=None):
    try:
        user = admin_auth.create_user(
            email=email,
            password=password,
            display_name=display_name or email.split('@')[0]
        )
        print(f"✅ Successfully created user: {user.uid}")

        # Store in Firestore
        db.collection("users").document(user.uid).set({
            "email": email,
            "display_name": display_name or email.split('@')[0],
            "created_at": firestore.SERVER_TIMESTAMP
        })

        return user.uid
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

# ✅ Login user (REST API via Pyrebase)
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
        print("✅ Login successful!")
        return data  # Includes idToken, refreshToken, localId, etc.
    except requests.exceptions.HTTPError as e:
        error = e.response.json()
        print(f"❌ Login failed: {error['error']['message']}")
        return None

# Optional: Fetch user data from Firestore
def get_user_data(uid):
    try:
        doc = db.collection("users").document(uid).get()
        if doc.exists:
            return doc.to_dict()
        else:
            print("⚠️ No such user.")
            return None
    except Exception as e:
        print(f"❌ Error fetching user data: {e}")
        return None

