import firebase_admin
from firebase_admin import credentials, firestore

try:
    app = firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate('/Users/revanthvuyyuru/Desktop/fitness_tracker/serviceAccountKey.json')
    app = firebase_admin.initialize_app(cred)

db = firestore.client(app)
