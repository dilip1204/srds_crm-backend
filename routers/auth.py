from fastapi import APIRouter, HTTPException, Depends
from models.user import UserRegister, UserLogin, TokenResponse
from database import db
from passlib.context import CryptContext
import jwt
import datetime

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
async def protected_route(token: str = Depends(create_jwt_token)):
    return {"message": "You are authenticated"}
