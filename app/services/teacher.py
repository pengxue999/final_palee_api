from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.teaching_log import TeachingLog
from app.schemas.teacher import TeacherCreate, TeacherUpdate
from app.schemas.teacher_assignment import TeacherAssignmentCreate, TeacherAssignmentUpdate
from app.schemas.teaching_log import TeachingLogCreate, TeachingLogUpdate
from app.configs.exceptions import ConflictException, NotFoundException
from app.utils.foreign_key_helper import safe_delete_with_constraint_check

def _generate_teacher_id(db: Session) -> str:
    last_teacher = (
        db.query(Teacher)
        .order_by(
            func.length(Teacher.teacher_id).desc(),
            Teacher.teacher_id.desc()
        )
        .first()
    )
    if not last_teacher:
        return "TC001"
    last_id = last_teacher.teacher_id
    if last_id.startswith("TC") and last_id[2:].isdigit():
        num = int(last_id[2:]) + 1
        return f"TC{num:03d}"
    return "TC001"
def get_all_teachers(db: Session):
    return db.query(Teacher).all()


def get_teacher(db: Session, teacher_id: str) -> Teacher:
    obj = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນອາຈານ")
    return obj


def create_teacher(db: Session, data: TeacherCreate):
    teacher_id= _generate_teacher_id(db)
    obj = Teacher(teacher_id=teacher_id, **data.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ເບີໂທລະສັບນີ້ '{data.teacher_contact}' ມີຢູ່ແລ້ວ")


def update_teacher(db: Session, teacher_id: str, data: TeacherUpdate):
    obj = get_teacher(db, teacher_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ເບີໂທລະສັບນີ້ '{data.teacher_contact}' ມີຢູ່ແລ້ວ")


def delete_teacher(db: Session, teacher_id: str):
    obj = get_teacher(db, teacher_id)
    safe_delete_with_constraint_check(db, obj, "teacher")

