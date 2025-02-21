from fastapi import FastAPI
from routers import student
from routers import auth

app = FastAPI()
# Include authentication routes
app.include_router(auth.auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(student.router)

@app.get("/test")
def read_root():
    return {"message": "srds crm base is working!"}
