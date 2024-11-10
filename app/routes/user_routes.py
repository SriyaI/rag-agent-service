from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from firebase_admin import auth
from db import get_db_connection
from auth_utils import generate_token
import bcrypt
import jwt
import os

router = APIRouter()

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    company: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

@router.post('/users/google-signin')
async def google_signin(request: Request):
    data = await request.json()
    id_token = data.get("idToken")
    if not id_token:
        raise HTTPException(status_code=400, detail="ID token is required")
    decoded_token = auth.verify_id_token(id_token["token"])
    email = decoded_token.get("email")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if not user:
                cur.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id",
                            (email, decoded_token.get("name")))
                user_id = cur.fetchone()[0]
            else:
                user_id = user[0]
    token = generate_token(user_id)
    return {"token": token}

@router.post('/users/register')
async def register(user: UserRegisterRequest):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (email, password, name, company) 
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (user.email, hashed_password, user.name, user.company))
            conn.commit()
            rows_affected = cur.rowcount
    return {"rowsAffected": rows_affected}

@router.post('/users/login')
async def login(user: UserLoginRequest):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, password FROM users WHERE email = %s", (user.email,))
            db_user = cur.fetchone()
            if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user[1].encode('utf-8')):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            token = generate_token(db_user[0])
            return {"token": token}

@router.get('/users/profile')
async def profile(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid or missing authorization header")
    token = auth_header.split(" ")[1]
    decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, name, company FROM users WHERE id = %s", (decoded['id'],))
            user = cur.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user[0],
        "email": user[1],
        "name": user[2],
        "company": user[3]
    }
