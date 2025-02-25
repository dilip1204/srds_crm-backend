from fastapi import FastAPI
from routers import student
from routers import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow React frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include authentication routes
app.include_router(auth.auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(student.router)

@app.get("/test")
def read_root():
    return {"message": "srds crm base is working!"}
