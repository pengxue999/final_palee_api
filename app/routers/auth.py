from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from app.configs.database import get_db
from app.configs.security import verify_password, create_access_token
from app.configs.exceptions import BaseAPIException
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["ການເຂົ້າສູ່ລະບົບ"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_name == data.user_name).first()

    if not user or not verify_password(data.user_password, user.user_password):
        raise BaseAPIException(
            code="UNAUTHORIZED",
            message="ຊື່ຜູ້ໃຊ້ ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ",
            status_code=401,
        )

    token = create_access_token({
        "sub": str(user.user_id),
        "user_name": user.user_name,
        "role": user.role,
    })

    teacher_id = user.user_name if str(user.role).upper() == 'TEACHER' else None

    return TokenResponse(
        access_token=token,
        user_id=user.user_id,
        user_name=user.user_name,
        role=user.role,
        teacher_id=teacher_id,
    )
