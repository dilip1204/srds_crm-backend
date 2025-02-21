from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer
from models import UserRegister
import jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Token authentication middleware
security = HTTPBearer()

def get_current_user(token: str = Security(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
