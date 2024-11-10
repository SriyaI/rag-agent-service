import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    cred = credentials.Certificate('./creds.json')
    firebase_admin.initialize_app(cred)