import sys
from typing import List
from fastapi import APIRouter, HTTPException, Depends # type: ignore
from models.student import PlanEnum, Student, Payment, Lesson, PlanEnum, PLAN_PRICES, PaymentStatusEnum
from database import db
from bson import ObjectId
from routers.auth import verify_token
import logging
from fastapi.security import OAuth2PasswordBearer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


@router.post("/students/", response_model= Student, tags=["Students"])
async def create_student(student: Student, token: dict = Depends(verify_token)):
    student_dict = student.model_dump(exclude={"id"})
    student_dict["_id"] = str(ObjectId())
    # Get the plan details and amount
    student_dict["total_amount"] = PLAN_PRICES.get(student.plan, 0)
    paid_amount = sum(payment["amount"] for payment in student_dict["payments"])
    student_dict["paid_amount"] = paid_amount
    student_dict["balance"] = student_dict["total_amount"] - paid_amount

    for payment in student_dict["payments"]:
        if "payment_id" not in payment or payment["payment_id"] is None:
            payment["payment_id"] = str(ObjectId())

    # Auto-generate Lesson IDs
    for lesson in student_dict["lessons"]:
        if "lesson_id" not in lesson or lesson["lesson_id"] is None:
            lesson["lesson_id"] = str(ObjectId())

    await db.students.insert_one(student_dict)
    student_dict["id"] = student_dict.pop("_id")

    student_dict["payments"] = [dict(payments) for payments in student_dict["payments"]]
    student_dict["lessons"] = [dict(lesson) for lesson in student_dict["lessons"]]
    
    return Student(**student_dict).model_dump()


@router.get("/getAllStudents", tags=["Students"])
async def get_students(current_user: dict = Depends(verify_token)):  # ✅ Explicitly accept `current_user`
    students = await db.students.find().to_list(100)
    return students

@router.get("/search-student-mobile/{mobile_number}", response_model= Student, tags=["Students"])
async def search_student_mobile(mobile_number : str):
    student = await db.students.find_one({"mobile_number":mobile_number})
    
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found for give mobile number, Kindly check and retry again")
    
    student["id"] = str(student.pop("_id"))

    student["payments"] = [Payment(**payment) for payment in student.get("payments",[])]
    student["lessons"] = [Lesson(**lesson) for lesson in student.get("lessons",[])]

    return Student(**student)


@router.get("/search-student-by-aadhar/{aadhar_number}", response_model= Student, tags=["Students"])
async def search_student_by_aadhar(aadhar_number : str, token: dict = Depends(verify_token)):
    student = await db.students.find_one({"aadhar_number":aadhar_number})
    
    if student is None:
        raise HTTPException(status_code=404, detail="Student not for give Aadhar number, Kindly check and retry again")
    
    student["payments"] = [Payment(**payment) for payment in student.get("payments",[])]
    student["lessons"] = [Lesson(**lesson) for lesson in student.get("lessons",[])]

    return Student(**student)

@router.get("/students/by-plan/{plan}", response_model=List[Student])
async def get_students_by_plan(plan: PlanEnum, token: dict = Depends(verify_token)):
    students = await db.students.find({"plan": plan.value}).to_list(None)
    return [Student(**student) for student in students]

@router.put("/students/application-number/{application_number}", response_model=Student, tags=["Students"])
async def update_student_by_application_number(application_number: str, updated_student: Student):
    print(f"Received Application Number: {application_number}")
    application_number = str(application_number).strip()
    student = await db.students.find_one({"application_number": application_number})
    print("Student Found:", student)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    updated_student_dict = updated_student.model_dump(exclude={"id"})

    result = await db.students.update_one(
        {"application_number": application_number},
        {"$set": updated_student_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student with the given application number not found")

    student = await db.students.find_one({"application_number": application_number})
    student["id"] = str(student.pop("_id"))

    return Student(**student)



@router.delete("/students/mobile-number/{mobile_number}", tags=["Students"])
async def delete_student_by_mobile_number(mobile_number: str):
    print(f"Received mobile_number: {mobile_number}")
    mobile_number = str(mobile_number).strip()
    student = await db.students.find_one({"mobile_number": mobile_number})
    print("Student Found:", student)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    result = await db.students.delete_one({"mobile_number": mobile_number})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student with this mobile number not found")

    return {"message": f"Student with mobile number {mobile_number} deleted successfully"}



@router.delete("/students/application-number/{application_number}", tags=["Students"])
async def delete_student_by_mobile_number(application_number: str):
    print(f"Received application_number: {application_number}")
    application_number = str(application_number).strip()
    student = await db.students.find_one({"application_number": application_number})
    print("Student Found:", student)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    result = await db.students.delete_one({"application_number": application_number})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student with this application number not found")

    return {"message": f"Student with mobile number {application_number} deleted successfully"}

@router.post("/students/{application_number}/payment", tags=["Payments"])
async def create_payment(application_number: str, payment: Payment, token: dict = Depends(verify_token)):
    student = await db.students.find_one({"application_number": application_number})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    current_paid_amount = student.get("paid_amount", 0)
    total_amount = student.get("total_amount", 0)
    if current_paid_amount >= total_amount:
        raise HTTPException(status_code=400, detail="Full payment already made. No further payments required.")

    # Generate unique payment_id
    payment.payment_id = str(ObjectId())

    # Correctly update the payments list
    updated_payments = student.get("payments", [])  # Ensure it's a list
    updated_payments.append(payment.dict())  # Append new payment

    # ✅ Fix: Use `updated_payments` to calculate new paid amount
    new_paid_amount = sum(p["amount"] for p in updated_payments)
    new_balance = student["total_amount"] - new_paid_amount

    # ✅ Update Full Payment Status based on balance
    full_payment_status = PaymentStatusEnum.COMPLETED if new_balance == 0 else PaymentStatusEnum.PENDING

    # ✅ Fix: Actually update the student record
    update_result = await db.students.update_one(
        {"application_number": application_number},
        {
            "$set": {
                "payments": updated_payments,  # Store new payments
                "paid_amount": new_paid_amount,
                "balance": new_balance,
                "full_payment_status": full_payment_status
            }
        }
    )
   
    # ✅ Debug: Ensure update was successful
    if update_result.modified_count == 0:
        print("⚠️ WARNING: No document was updated. Check query conditions.")
    else:
        print("✅ Student record updated successfully!")

    # Fetch the updated student record to confirm changes
    updated_student = await db.students.find_one({"application_number": application_number})
    
    return {
        "message": "Payment added successfully",
        "new_paid_amount": updated_student["paid_amount"],
        "new_balance": updated_student["balance"],
        "payment_status": updated_student["full_payment_status"],
        "payment": payment.dict()
    }

