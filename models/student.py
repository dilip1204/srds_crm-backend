from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class Payment(BaseModel):
    payment_id: Optional[str] = None
    amount: float
    date: datetime
    status: str

class Lesson(BaseModel):
    lesson_id: Optional[str] = None
    instructor_id: str
    date: datetime
    status: str

class Student(BaseModel):
    id: str = None
    name: str
    mobile_number: str
    email: EmailStr
    aadhar_number: str
    registered_date: datetime
    payments: List[Payment] = []
    lessons: List[Lesson] = []
