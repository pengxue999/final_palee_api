import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.configs.database import engine, Base, test_connection
from app.services.pdf.engine import shutdown_engines, warmup_engine
from app.configs.exceptions import BaseAPIException, api_exception_handler
from app.configs.security import get_current_user
from app.routers import auth
from app.routers import public
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
    donation_category,
    donation,
    dashboard,
    reports,
)

Base.metadata.create_all(bind=engine)

test_connection()

@asynccontextmanager
async def lifespan(_: FastAPI):
    # warm-up browser ໄວ້ກ່ອນ (ໃນ background) ໃຫ້ໃບບິນທຳອິດໄວ ບໍ່ຕ້ອງລໍ launch.
    threading.Thread(target=warmup_engine, name="pdf-warmup", daemon=True).start()
    yield
    # ປິດ browser ທີ່ໃຊ້ສ້າງ PDF ທັງໝົດ ຕอນ shutdown.
    shutdown_engines()


app = FastAPI(
    title="Palee API",
    description=" Palee Elite Training Center",
    version="1.0.0",
    redirect_slashes=False,
    lifespan=lifespan,
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


# /auth ເປີດໄວ້ສາທາລະນະ (ບໍ່ຕ້ອງ login ກ່ອນ ຈຶ່ງຈະ login ໄດ້)
app.include_router(auth.router)

# /public ເປີດໄວ້ສາທາລະນະ ສຳລັບ web portfolio (ນັກຮຽນເບິ່ງຂໍ້ມູນ ແລະ ລົງທະບຽນ ໂດຍບໍ່ຕ້ອງ login)
app.include_router(public.router)

# router ທີ່ເຫຼືອທັງໝົດ ຕ້ອງ login (ມີ token ທີ່ຖືກຕ້ອງ) ກ່ອນຈຶ່ງເຂົ້າເຖິງໄດ້
protected = [Depends(get_current_user)]
app.include_router(province.router, dependencies=protected)
app.include_router(district.router, dependencies=protected)
app.include_router(academic_years.router, dependencies=protected)
app.include_router(subject_category.router, dependencies=protected)
app.include_router(subject.router, dependencies=protected)
app.include_router(level.router, dependencies=protected)
app.include_router(subject_detail.router, dependencies=protected)
app.include_router(fee.router, dependencies=protected)
app.include_router(discount.router, dependencies=protected)
app.include_router(user.router, dependencies=protected)
app.include_router(teacher.router, dependencies=protected)
app.include_router(teacher_assignment.router, dependencies=protected)
app.include_router(teaching_log.router, dependencies=protected)
app.include_router(salary_payment.router, dependencies=protected)
app.include_router(student.router, dependencies=protected)
app.include_router(registration.router, dependencies=protected)
app.include_router(registration_detail.router, dependencies=protected)
app.include_router(tuition_payment.router, dependencies=protected)
app.include_router(evaluation.router, dependencies=protected)
app.include_router(evaluation_detail.router, dependencies=protected)
app.include_router(expense_category.router, dependencies=protected)
app.include_router(expense.router, dependencies=protected)
app.include_router(income.router, dependencies=protected)
app.include_router(donor.router, dependencies=protected)
app.include_router(donation_category.router, dependencies=protected)
app.include_router(donation.router, dependencies=protected)
app.include_router(dashboard.router, dependencies=protected)
app.include_router(reports.router, dependencies=protected)


@app.get("/")
def root():
    return {"code": "SUCCESSFULLY", "messages": "Palee API is running", "data": None}

main = app
