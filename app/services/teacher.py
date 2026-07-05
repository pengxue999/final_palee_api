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


def _check_duplicate_name(
    db: Session,
    teacher_name: str,
    teacher_lastname: str,
    exclude_id: str | None = None,
):
    query = db.query(Teacher).filter(
        Teacher.teacher_name == teacher_name,
        Teacher.teacher_lastname == teacher_lastname,
    )
    if exclude_id is not None:
        query = query.filter(Teacher.teacher_id != exclude_id)
    if query.first():
        raise ConflictException(
            f"ອາຈານຊື່ '{teacher_name} {teacher_lastname}' ມີຢູ່ແລ້ວ"
        )


def get_all_teachers(db: Session):
    return db.query(Teacher).all()


def get_teacher(db: Session, teacher_id: str) -> Teacher:
    obj = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນອາຈານ")
    return obj


def create_teacher(db: Session, data: TeacherCreate):
    _check_duplicate_name(db, data.teacher_name, data.teacher_lastname)
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
    if data.teacher_name is not None or data.teacher_lastname is not None:
        _check_duplicate_name(
            db,
            data.teacher_name if data.teacher_name is not None else obj.teacher_name,
            data.teacher_lastname if data.teacher_lastname is not None else obj.teacher_lastname,
            exclude_id=teacher_id,
        )
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

