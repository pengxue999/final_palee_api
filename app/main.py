from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.configs.database import engine, Base, test_connection
from app.configs.exceptions import BaseAPIException, api_exception_handler
from app.routers import auth
from app.routers import (
    province,
    district,
    academic_years,
    subject_category,
    subject,
    level,
    subject_detail,
    fee,
    discount,
    user,
    teacher,
    teacher_assignment,
    teaching_log,
    salary_payment,
    student,
    registration,
    registration_detail,
    tuition_payment,
    evaluation,
    evaluation_detail,
    expense_category,
    expense,
    income,
    donor,
    unit,
    donation,
    dashboard,
    reports,
)

Base.metadata.create_all(bind=engine)

test_connection()

app = FastAPI(
    title="Palee API",
    description="ລະບົບບໍລິຫານໂຮງຮຽນ Palee System",
    version="1.0.0",
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "code": "BAD_REQUEST",
            "messages": "Validation error",
            "data": jsonable_encoder(exc.errors()),
        },
    )


@app.exception_handler(BaseAPIException)
async def custom_api_exception_handler(request: Request, exc: BaseAPIException):
    return await api_exception_handler(request, exc)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "messages": "Internal server error",
            "data": None,
        },
    )


app.include_router(auth.router)
app.include_router(province.router)
app.include_router(district.router)
app.include_router(academic_years.router)
app.include_router(subject_category.router)
app.include_router(subject.router)
app.include_router(level.router)
app.include_router(subject_detail.router)
app.include_router(fee.router)
app.include_router(discount.router)
app.include_router(user.router)
app.include_router(teacher.router)
app.include_router(teacher_assignment.router)
app.include_router(teaching_log.router)
app.include_router(salary_payment.router)
app.include_router(student.router)
app.include_router(registration.router)
app.include_router(registration_detail.router)
app.include_router(tuition_payment.router)
app.include_router(evaluation.router)
app.include_router(evaluation_detail.router)
app.include_router(expense_category.router)
app.include_router(expense.router)
app.include_router(income.router)
app.include_router(donor.router)
app.include_router(unit.router)
app.include_router(donation.router)
app.include_router(dashboard.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {"code": "SUCCESSFULLY", "messages": "Palee API is running", "data": None}

main = app
