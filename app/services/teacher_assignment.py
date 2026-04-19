from sqlalchemy.orm import Session, joinedload
from app.models.teacher_assignment import TeacherAssignment
from app.models.subject_detail import SubjectDetail
from app.schemas.teacher_assignment import TeacherAssignmentCreate, TeacherAssignmentUpdate
from app.configs.exceptions import NotFoundException
from sqlalchemy import func


def _generate_assignment_id(db: Session) -> str:
    last = (
        db.query(TeacherAssignment)
        .order_by(
            func.length(TeacherAssignment.assignment_id).desc(),
            TeacherAssignment.assignment_id.desc()
        )
        .first()
    )
    if not last:
        return "TA001"
    last_id = last.assignment_id
    if last_id.startswith("TA") and last_id[2:].isdigit():
        num = int(last_id[2:]) + 1
        return f"TA{num:03d}"
    return "TA001"


def _query_with_relations(db: Session):
    return db.query(TeacherAssignment).options(
        joinedload(TeacherAssignment.teacher),
        joinedload(TeacherAssignment.subject_detail).joinedload(SubjectDetail.subject),
        joinedload(TeacherAssignment.subject_detail).joinedload(SubjectDetail.level),
        joinedload(TeacherAssignment.academic_year),
    )


def get_all(db: Session):
    return _query_with_relations(db).all()


def get_by_teacher(db: Session, teacher_id: str):
    return _query_with_relations(db).filter(
        TeacherAssignment.teacher_id == teacher_id
    ).all()


def get_by_id(db: Session, assignment_id: str):
    obj = _query_with_relations(db).filter(
        TeacherAssignment.assignment_id == assignment_id
    ).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນການສອນຂອງອາຈານ")
    return obj


def create(db: Session, data: TeacherAssignmentCreate):
    assignment_id = _generate_assignment_id(db)
    obj = TeacherAssignment(assignment_id=assignment_id, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return get_by_id(db, obj.assignment_id)


def update(db: Session, assignment_id: str, data: TeacherAssignmentUpdate):
    obj = get_by_id(db, assignment_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return get_by_id(db, assignment_id)


def delete(db: Session, assignment_id: str):
    obj = get_by_id(db, assignment_id)
    db.delete(obj)
    db.commit()
