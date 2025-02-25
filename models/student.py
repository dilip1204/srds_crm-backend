from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class Payment(BaseModel):
    payment_id: str = None #To be Auto generated
    transaction_id : str = None #UPI Id
    amount: float
    date: datetime
    status: str

class Lesson(BaseModel):
    lesson_id: str = None #To be Auto generated
    instructor_id: str
    date: datetime
    status: str

# Define Enum for Student Plans
class PlanEnum(str, Enum):
    BASIC = "Basic"
    STANDARD = "Standard"
    PREMIUM = "Premium"
    ADVANCED = "Advanced"
    PROFESSIONAL = "Professional"
    ELITE = "Elite"
    FAST_TRACK = "Fast Track"
    WEEKEND = "Weekend"
    NIGHT_CLASSES = "Night Classes"
    CUSTOM = "Custom"
    RC_NAME_TRANSFER = "Rc name transfer"
    INSURANCE_RENEWAL = "Insurance renewal"
    CONDUCTOR_LICENSE_RENEWAL = "Conductor License Renewal"
    FANCY_NUMBER = "Fancy Number"
    OWN_CAR_DRIVING = "Own Car Driving"

class Student(BaseModel):
    id: str = None
    name: str
    mobile_number: str
    application_number : str
    email: EmailStr
    aadhar_number: str
    registered_date: datetime
    plan: PlanEnum
    payments: List[Payment] = []
    lessons: List[Lesson] = []
