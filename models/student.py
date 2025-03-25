from enum import Enum
from pydantic import BaseModel, EmailStr, Field, root_validator
from typing import List, Optional
from datetime import datetime

class PaymentStatusEnum(str, Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"

class Payment(BaseModel):
    payment_id: str = None #To be Auto generated
    transaction_id : str = None #UPI Id
    amount: float = Field(gt=0, description="Payment amount should be greater than 0")
    date: datetime
    status: PaymentStatusEnum

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
    HEAVY = "Heavy"
    ELITE = "Elite"
    FAST_TRACK = "Fast Track"
    CUSTOM = "Custom"
    RC_NAME_TRANSFER = "Rc name transfer"
    INSURANCE_RENEWAL = "Insurance renewal"
    CONDUCTOR_LICENSE_RENEWAL = "Conductor License Renewal"
    FANCY_NUMBER = "Fancy Number"
    OWN_CAR_DRIVING = "Own Car Driving"

# Define a dictionary for Plan Prices
PLAN_PRICES = {
    PlanEnum.BASIC: 5000.0,
    PlanEnum.STANDARD: 7000.0,
    PlanEnum.PREMIUM: 9000.0,
    PlanEnum.ADVANCED: 11000.0,
    PlanEnum.HEAVY: 10000.0,
    PlanEnum.ELITE: 11000.0,
    PlanEnum.FAST_TRACK: 12000.0,
    PlanEnum.CUSTOM: 7000.0,
    PlanEnum.RC_NAME_TRANSFER: 2000.0,
    PlanEnum.INSURANCE_RENEWAL: 1200.0,
    PlanEnum.CONDUCTOR_LICENSE_RENEWAL: 3000.0,
    PlanEnum.FANCY_NUMBER: 11000.0,
    PlanEnum.OWN_CAR_DRIVING: 7000.0
}


class StatusEnum(str, Enum):
    PROCESS_STARTED = "Process Started"
    PROCESS_FAILED = "Process failed"
    PROCESS_STALLED = "Process stalled"
    PROCESS_COMPLETED = "Process completed"

class Student(BaseModel):
    id: str = None
    name: str
    mobile_number: str
    application_number : str
    email: EmailStr
    aadhar_number: str
    registered_date: datetime
    plan: PlanEnum
    total_amount: float = 0.0
    paid_amount: float = 0.0
    balance: float = 0.0
    status: StatusEnum
    full_payment_status:PaymentStatusEnum
    payments: List[Payment] = []
    lessons: List[Lesson] = []

class Config:
    populate_by_name = True
    arbitrary_types_allowed = True
    json_encoders = {
        datetime: lambda v: v.isoformat()
    }

@root_validator(pre=True, allow_reuse=True)
def calculate_totals(cls, values):
    """ Auto-calculate total amount & balance at instance creation """
    plan = values.get("plan")
    if plan:
        values["total_amount"] = PLAN_PRICES.get(plan, 0)
        values["balance"] = values["total_amount"] - values.get("paid_amount", 0)
    return values

class Config:
    populate_by_name = True
    arbitrary_types_allowed = True
    json_encoders = {
        datetime: lambda v: v.isoformat()
    }

 # Auto-assign values when creating an instance
def __init__(self, **data):
    super().__init__(**data)
    self.calculate_totals()