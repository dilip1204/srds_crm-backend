from fastapi import APIRouter, HTTPException
from models.student import Student, Payment, Lesson
from database import db
from bson import ObjectId

router = APIRouter()


@router.post("/students/", response_model= Student, tags=["Students"])
async def create_student(student: Student):
    student_dict = student.model_dump(exclude={"id"})
    student_dict["_id"] = str(ObjectId())
    for payment in student_dict["payments"]:
        if payment.get("payment_id") is None:
            payment["payment_id"] = str(ObjectId())
    
    for lesson in student_dict["lessons"]:
        if lesson.get("lesson_id") is None:
            lesson["lesson_id"] = str(ObjectId())
    
    await db.students.insert_one(student_dict)
    student_dict["id"] = student_dict.pop("_id")

    student_dict["payments"] = [dict(payment) for payment in student_dict["payments"]]
    student_dict["lessons"] = [dict(lesson) for lesson in student_dict["lessons"]]
    
    return Student(**student_dict).model_dump()


@router.get("/students", tags=["Students"])
async def get_students():
    students = await db.students.find().to_list(100)
    return students

@router.get("/search-student-mobile", response_model= Student, tags=["Students"])
async def search_student_mobile(mobile_number : str):
    student = await db.students.find_one({"mobile_number":mobile_number})
    
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found for give mobile number, Kindly check and retry again")
    
    student["id"] = str(student.pop("_id"))

    student["payments"] = [Payment(**payment) for payment in student.get("payments",[])]
    student["lessons"] = [Lesson(**lesson) for lesson in student.get("lessons",[])]

    return Student(**student)


@router.get("/search-student-by-aadhar", response_model= Student, tags=["Students"])
async def search_student_by_aadhar(aadhar_number : str):
    student = await db.students.find_one({"aadhar_number":aadhar_number})
    
    if student is None:
        raise HTTPException(status_code=404, detail="Student not for give Aadhar number, Kindly check and retry again")
    
    student["id"] = str(student.pop("_id"))

    student["payments"] = [Payment(**payment) for payment in student.get("payments",[])]
    student["lessons"] = [Lesson(**lesson) for lesson in student.get("lessons",[])]

    return Student(**student)




