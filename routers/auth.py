from fastapi import APIRouter, HTTPException, Depends, Request
from models.user import UserRegister, UserLogin, TokenResponse
from database import db
from passlib.context import CryptContext
import jwt
import datetime
from fastapi.security import OAuth2PasswordBearer

# Token storage for blacklisting (Replace with Redis for production)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
blacklisted_tokens = set()

# Secret Key for JWT (Change this in production)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

auth_router = APIRouter()

# In-memory user database (replace with MongoDB)
users_collection = db["users"]

# Helper function to create JWT Token
def create_jwt_token(data: dict):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    data.update({"exp": expiration})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


@auth_router.post("/register")
async def register_user(user: UserRegister):
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before storing
    hashed_password = pwd_context.hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password
    await users_collection.insert_one(user_data)
    return {"message": "User registered successfully"}


@auth_router.post("/login", response_model=TokenResponse)
async def login_user(user: UserLogin):
    # Find user in database
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT token
    token = create_jwt_token({"sub": db_user["email"]})
    return {"access_token": token, "token_type": "bearer"}


@auth_router.get("/protected-route")
async def protected_route():
    return {"message": "You are authenticated"}


@auth_router.post("/logout")
async def logout_user(request: Request):
    """
    Blacklist the user's token, effectively logging them out.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    token = auth_header.split("Bearer ")[1]
    blacklisted_tokens.add(token)

    return {"message": "Logged out successfully"}

# Middleware function to check if token is blacklisted
async def verify_token_blacklist(token: str = Depends(oauth2_scheme)):
    if token in blacklisted_tokens:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")
    return token

async def verify_token(token: str = Depends(oauth2_scheme)):
    if token in blacklisted_tokens:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Contains user info (email)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

