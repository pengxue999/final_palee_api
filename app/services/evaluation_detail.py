from sqlalchemy.orm import Session, joinedload

from app.configs.exceptions import NotFoundException
from app.models.evaluation import Evaluation
from app.models.evaluation_detail import EvaluationDetail
from app.models.fee import Fee
from app.models.registration import Registration
from app.models.registration_detail import RegistrationDetail
from app.models.subject_detail import SubjectDetail
from app.schemas.evaluation_detail import EvaluationDetailCreate, EvaluationDetailUpdate
from app.services import evaluation as evaluation_svc


def _base_query(db: Session):
    return db.query(EvaluationDetail).options(
        joinedload(EvaluationDetail.evaluation),
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.registration)
        .joinedload(Registration.student),
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.subject),
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.level),
    )


def get_all(db: Session):
    return _base_query(db).all()


def get_by_id(db: Session, eval_detail_id: int):
    obj = _base_query(db).filter(EvaluationDetail.eval_detail_id == eval_detail_id).first()
    if not obj:
        raise NotFoundException('ຂໍ້ມູນລາຍລະອຽດການປະເມີນ')
    return obj


def create(db: Session, data: EvaluationDetailCreate):
    obj = EvaluationDetail(**data.model_dump())
    db.add(obj)
    db.flush()
    evaluation_svc._recompute_rankings(db, obj.evaluation_id)
    db.commit()
    db.expire_all()
    return get_by_id(db, obj.eval_detail_id)


def update(db: Session, eval_detail_id: int, data: EvaluationDetailUpdate):
    obj = get_by_id(db, eval_detail_id)
    updates = data.model_dump(exclude_none=True)
    old_evaluation_id = obj.evaluation_id

    for field, value in updates.items():
        setattr(obj, field, value)

    db.flush()
    evaluation_svc._recompute_rankings(db, obj.evaluation_id)
    if old_evaluation_id != obj.evaluation_id:
        if not evaluation_svc._delete_evaluation_if_empty(db, old_evaluation_id):
            evaluation_svc._recompute_rankings(db, old_evaluation_id)

    db.commit()
    db.expire_all()
    return get_by_id(db, obj.eval_detail_id)


def delete(db: Session, eval_detail_id: int):
    obj = get_by_id(db, eval_detail_id)
    evaluation_id = obj.evaluation_id
    db.delete(obj)
    db.flush()

    if not evaluation_svc._delete_evaluation_if_empty(db, evaluation_id):
        evaluation_svc._recompute_rankings(db, evaluation_id)

    db.commit()
