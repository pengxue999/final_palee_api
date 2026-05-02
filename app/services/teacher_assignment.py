from sqlalchemy.orm import Session, joinedload
from app.models.teacher_assignment import TeacherAssignment
from app.models.subject_detail import SubjectDetail
from app.schemas.teacher_assignment import (
    TeacherAssignmentBatchCreate,
    TeacherAssignmentCreate,
    TeacherAssignmentUpdate,
)
from app.configs.exceptions import ConflictException, NotFoundException, ValidationException
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


def _get_next_assignment_number(db: Session) -> int:
    last = (
        db.query(TeacherAssignment)
        .order_by(
            func.length(TeacherAssignment.assignment_id).desc(),
            TeacherAssignment.assignment_id.desc()
        )
        .first()
    )
    if not last:
        return 1

    last_id = last.assignment_id
    if last_id.startswith("TA") and last_id[2:].isdigit():
        return int(last_id[2:]) + 1
    return 1


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


def _find_duplicate_assignment(
    db: Session,
    teacher_id: str,
    subject_detail_id: str,
    academic_id: str,
    exclude_assignment_id: str | None = None,
):
    query = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher_id,
        TeacherAssignment.subject_detail_id == subject_detail_id,
        TeacherAssignment.academic_id == academic_id,
    )
    if exclude_assignment_id:
        query = query.filter(TeacherAssignment.assignment_id != exclude_assignment_id)
    return query.first()


def create(db: Session, data: TeacherAssignmentCreate):
    duplicate = _find_duplicate_assignment(
        db,
        data.teacher_id,
        data.subject_detail_id,
        data.academic_id,
    )
    if duplicate:
        raise ConflictException("ອາຈານຄົນນີ້ຖືກມອບໝາຍວິຊາ/ລະດັບນີ້ໃນສົກຮຽນນີ້ແລ້ວ")

    assignment_id = _generate_assignment_id(db)
    obj = TeacherAssignment(assignment_id=assignment_id, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return get_by_id(db, obj.assignment_id)


def create_many(db: Session, data: TeacherAssignmentBatchCreate):
    if not data.assignments:
        raise ValidationException("ກະລຸນາເລືອກວິຊາ/ລະດັບຢ່າງນ້ອຍ 1 ລາຍການ")

    subject_detail_ids = [item.subject_detail_id for item in data.assignments]
    duplicate_subject_ids = {
        subject_detail_id
        for subject_detail_id in subject_detail_ids
        if subject_detail_ids.count(subject_detail_id) > 1
    }
    if duplicate_subject_ids:
        raise ConflictException("ມີວິຊາ/ລະດັບຊ້ຳກັນໃນລາຍການທີ່ກຳລັງບັນທຶກ")

    for item in data.assignments:
        duplicate = _find_duplicate_assignment(
            db,
            data.teacher_id,
            item.subject_detail_id,
            data.academic_id,
        )
        if duplicate:
            raise ConflictException("ມີບາງລາຍການຖືກມອບໝາຍແລ້ວໃນສົກຮຽນນີ້")

    next_number = _get_next_assignment_number(db)
    created_ids = []

    for index, item in enumerate(data.assignments):
        assignment_id = f"TA{next_number + index:03d}"
        obj = TeacherAssignment(
            assignment_id=assignment_id,
            teacher_id=data.teacher_id,
            subject_detail_id=item.subject_detail_id,
            academic_id=data.academic_id,
            hourly_rate=item.hourly_rate,
        )
        db.add(obj)
        created_ids.append(assignment_id)

    db.commit()

    return _query_with_relations(db).filter(
        TeacherAssignment.assignment_id.in_(created_ids)
    ).all()


def update(db: Session, assignment_id: str, data: TeacherAssignmentUpdate):
    obj = get_by_id(db, assignment_id)

    next_teacher_id = data.teacher_id or obj.teacher_id
    next_subject_detail_id = data.subject_detail_id or obj.subject_detail_id
    next_academic_id = data.academic_id or obj.academic_id

    duplicate = _find_duplicate_assignment(
        db,
        next_teacher_id,
        next_subject_detail_id,
        next_academic_id,
        exclude_assignment_id=assignment_id,
    )
    if duplicate:
        raise ConflictException("ອາຈານຄົນນີ້ຖືກມອບໝາຍວິຊາ/ລະດັບນີ້ໃນສົກຮຽນນີ້ແລ້ວ")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return get_by_id(db, assignment_id)


def delete(db: Session, assignment_id: str):
    obj = get_by_id(db, assignment_id)
    db.delete(obj)
    db.commit()
