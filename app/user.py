import os
import jwt
import bcrypt
import psycopg2
from flask import Flask, request, jsonify
from firebase_admin import credentials, auth, initialize_app
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection configuration
db_config = {
    "user": "",
    "password": "",
    "host": "",
    "port": "",
    "database": "",
    "sslmode": ""
}

# Initialize Firebase Admin SDK
firebase_cred = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
}
initialize_app(credentials.Certificate(firebase_cred))

app = Flask(__name__)

# Utility function to get a database connection
def get_db_connection():
    return psycopg2.connect(**db_config)

# Utility to generate JWT tokens
def generate_token(user_id):
    return jwt.encode({"id": user_id}, os.getenv("JWT_SECRET"), algorithm="HS256")

@app.route('/google-signin', methods=['POST'])
def google_signin():
    try:
        id_token = request.json.get('idToken')
        if not id_token:
            return jsonify({"error": "ID token is required"}), 400

        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token.get("email")
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
                
                if not user:
                    # Create user in database
                    cur.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", 
                                (email, decoded_token.get("name")))
                    user_id = cur.fetchone()[0]
                else:
                    user_id = user[0]  # Assuming user ID is the first column

        token = generate_token(user_id)
        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route('/register', methods=['POST'])
def register():
    try:
        email = request.json.get('email')
        password = request.json.get('password')
        name = request.json.get('name')
        company = request.json.get('company')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (email, password, name, company) VALUES (%s, %s, %s, %s) RETURNING id",
                            (email, hashed_password, name, company))
                conn.commit()
                rows_affected = cur.rowcount

        return jsonify({"rowsAffected": rows_affected}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.json.get('email')
        password = request.json.get('password')

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
                user = cur.fetchone()

                if not user or not bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
                    return jsonify({"error": "Invalid credentials"}), 401

                token = generate_token(user[0])
                return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/profile', methods=['GET'])
def profile():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid or missing authorization header"}), 401

        token = auth_header.split(' ')[1]
        decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (decoded['id'],))
                user = cur.fetchone()

                if not user:
                    return jsonify({"error": "User not found"}), 404

        return jsonify({
            "id": user[0], "email": user[1], "name": user[2], "company": user[3]
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

