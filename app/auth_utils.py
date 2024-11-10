import jwt
import os

def generate_token(user_id):
    return jwt.encode({"id": user_id}, os.getenv("JWT_SECRET"), algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
