from typing import List
from fastapi import APIRouter, HTTPException, Depends
from models.student import PlanEnum, Student, Payment, Lesson
from database import db
from bson import ObjectId
from routers.auth import verify_token


router = APIRouter()


@router.post("/students/", response_model= Student, tags=["Students"])
async def create_student(student: Student, token: dict = Depends(verify_token)):
    student_dict = student.model_dump(exclude={"id"})
    student_dict["_id"] = str(ObjectId())
    student_dict["plan"] = student.plan.value 

    for payment in student_dict["payments"]:
        if payment.get("payment_id") is None:
            payment["payment_id"] = str(ObjectId())
                
    for lesson in student_dict["lessons"]:
        if lesson.get("lesson_id") is None:
            lesson["lesson_id"] = lesson.get("lesson_id")
    
    await db.students.insert_one(student_dict)
    student_dict["id"] = student_dict.pop("_id")

    student_dict["payments"] = [dict(payment) for payment in student_dict["payments"]]
    student_dict["lessons"] = [dict(lesson) for lesson in student_dict["lessons"]]
    
    return Student(**student_dict).model_dump()


@router.get("/students", tags=["Students"])
async def get_students(verify_token):
    students = await db.students.find().to_list(100)
    return students

@router.get("/search-student-mobile/{mobile_number}", response_model= Student, tags=["Students"])
async def search_student_mobile(mobile_number : str, token: dict = Depends(verify_token)):
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
    
    student["id"] = str(student.pop("_id"))

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


