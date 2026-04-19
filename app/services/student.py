from sqlalchemy import and_, func
from sqlalchemy.orm import Session
import time
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.configs.exceptions import NotFoundException, ConflictException
from app.utils.foreign_key_helper import safe_delete_with_constraint_check


def _generate_student_id(db: Session) -> str:
    """
    ສ້າງ Student ID ໃຫ້ຕໍ່າກວ່າກັນ ກັບ retry logic ເພື່ອປ້ອງກັນ race condition
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # ໃຊ້ FOR UPDATE lock ເພື່ອ lock ແຖວສຸດທ້າຍ
            last_student = (
                db.query(Student)
                .order_by(
                    func.length(Student.student_id).desc(),
                    Student.student_id.desc()
                )
                .with_for_update()  # 🔒 ລັອກກາກບາດ race condition
                .first()
            )
            if not last_student:
                return "ST001"
            last_id = last_student.student_id
            if last_id.startswith("ST") and last_id[2:].isdigit():
                num = int(last_id[2:]) + 1
                return f"ST{num:03d}"
            return "ST001"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))  # exponential backoff
                continue
            raise


def _normalize_text(value: str) -> str:
    return " ".join(value.split())


def _check_duplicate_student(db: Session, data: StudentCreate):
    normalized_name = _normalize_text(data.student_name)
    normalized_lastname = _normalize_text(data.student_lastname)

    duplicate = db.query(Student).filter(
        and_(
            Student.student_contact == data.student_contact,
            func.trim(Student.student_name) == normalized_name,
            func.trim(Student.student_lastname) == normalized_lastname,
            # Student.parents_contact == data.parents_contact,
        )
    ).first()

    if not duplicate:
        return

    duplicate_payload = StudentResponse.model_validate(duplicate).model_dump()

    raise ConflictException(
        message="ຂໍ້ມູນນັກຮຽນນີ້ມີຢູ່ໃນລະບົບແລ້ວ",
        data=duplicate_payload,
    )


def get_all(db: Session):
    return db.query(Student).all()


def get_by_id(db: Session, student_id: str):
    obj = db.query(Student).filter(Student.student_id == student_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນນັກຮຽນ")
    return obj


def create(db: Session, data: StudentCreate):
    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            _check_duplicate_student(db, data)

            # ສ້າງ student ID (ມີລັອກພາຍໃນ transaction)
            student_id = _generate_student_id(db)

            # ສ້າງໂຣຟາຍໃໝ່
            student_data = {
                "student_id": student_id,
                "student_name": data.student_name,
                "student_lastname": data.student_lastname,
                "gender": data.gender,
                "student_contact": data.student_contact,
                "parents_contact": data.parents_contact,
                "school": data.school,
                "district_id": data.district_id,
            }

            obj = Student(**student_data)
            db.add(obj)
            db.commit()  # atomic commit
            db.refresh(obj)
            return obj

        except ConflictException:
            # ຫໍພັກເຕັມ - ບໍ່ຕ້ອງ retry
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            last_error = e
            if attempt < max_retries - 1:
                # retry ກັບ backoff
                time.sleep(0.1 * (attempt + 1))
                continue
            raise



def update(db: Session, student_id: str, data: StudentUpdate):
    """
    ອັບເດດຂໍ້ມູນນັກຮຽນ ກັບ concurrency protection
    """
    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            # Lock ໂຣຟາຍນັກຮຽນ
            obj = db.query(Student).filter(
                Student.student_id == student_id
            ).with_for_update().first()

            if not obj:
                raise NotFoundException("ຂໍ້ມູນນັກຮຽນ")

            for field, value in data.model_dump(exclude_none=True).items():
                setattr(obj, field, value)

            db.commit()
            db.refresh(obj)
            return obj

        except ConflictException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1))
                continue
            raise



def delete(db: Session, student_id: str):
    obj = get_by_id(db, student_id)
    safe_delete_with_constraint_check(db, obj, "student")
