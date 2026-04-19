from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import re

from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload

from app.configs.exceptions import ValidationException
from app.enums.academic_status import AcademicStatusEnum
from app.enums.semester import SemesterEnum
from app.models.academic_years import AcademicYear
from app.models.district import District
from app.models.evaluation import Evaluation
from app.models.evaluation_detail import EvaluationDetail
from app.models.fee import Fee
from app.models.level import Level
from app.models.registration import Registration
from app.models.registration_detail import RegistrationDetail
from app.models.student import Student
from app.models.subject import Subject
from app.models.subject_detail import SubjectDetail
from app.schemas.evaluation import (
    AssessmentReportItemResponse,
    EvaluationCreate,
    EvaluationUpdate,
    ScoreEntryLevelResponse,
    ScoreEntrySaveRequest,
    ScoreEntrySubjectResponse,
    ScoreEntrySheetResponse,
    ScoreEntryStudentResponse,
    ScoreEntrySummaryResponse,
    StudentTranscriptItemResponse,
)


def _generate_evaluation_id(db: Session) -> str:
    latest = db.query(Evaluation).order_by(
        func.length(Evaluation.evaluation_id).desc(),
        Evaluation.evaluation_id.desc(),
    ).first()

    if latest and latest.evaluation_id:
        match = re.match(r'EV(\d+)', latest.evaluation_id)
        next_num = int(match.group(1)) + 1 if match else 1
    else:
        next_num = 1

    return f'EV{next_num:04d}'


def _parse_semester(semester: str) -> SemesterEnum:
    aliases = {
        SemesterEnum.SEMESTER_1.value: SemesterEnum.SEMESTER_1,
        SemesterEnum.SEMESTER_2.value: SemesterEnum.SEMESTER_2,
        'semester 1': SemesterEnum.SEMESTER_1,
        'semester_1': SemesterEnum.SEMESTER_1,
        '1': SemesterEnum.SEMESTER_1,
        'ພາກຮຽນ 1': SemesterEnum.SEMESTER_1,
        'ກາງພາກ': SemesterEnum.SEMESTER_1,
        'midterm': SemesterEnum.SEMESTER_1,
        'semester 2': SemesterEnum.SEMESTER_2,
        'semester_2': SemesterEnum.SEMESTER_2,
        '2': SemesterEnum.SEMESTER_2,
        'ພາກຮຽນ 2': SemesterEnum.SEMESTER_2,
        'ທ້າຍພາກ': SemesterEnum.SEMESTER_2,
        'final': SemesterEnum.SEMESTER_2,
    }
    key = str(semester).strip()
    normalized = aliases.get(key) or aliases.get(key.lower())
    if normalized is None:
        raise ValidationException('semester ຕ້ອງເປັນ ກາງພາກ ຫຼື ທ້າຍພາກ')
    return normalized


def _get_active_academic_year(db: Session) -> AcademicYear:
    academic_year = db.query(AcademicYear).filter(
        AcademicYear.status == AcademicStatusEnum.ACTIVE,
    ).first()
    if academic_year is None:
        raise ValidationException('ບໍ່ພົບສົກຮຽນທີ່ກຳລັງດຳເນີນການ')
    return academic_year


def _registered_detail_query(db: Session, academic_id: str, level_id: str):
    return db.query(RegistrationDetail).options(
        joinedload(RegistrationDetail.registration).joinedload(Registration.student),
        joinedload(RegistrationDetail.fee_rel).joinedload(Fee.academic_year),
        joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.subject),
        joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.level),
    ).join(
        Fee, Fee.fee_id == RegistrationDetail.fee_id,
    ).join(
        Registration, Registration.registration_id == RegistrationDetail.registration_id,
    ).join(
        Student, Student.student_id == Registration.student_id,
    ).join(
        SubjectDetail, SubjectDetail.subject_detail_id == Fee.subject_detail_id,
    ).join(
        Subject, Subject.subject_id == SubjectDetail.subject_id,
    ).filter(
        Fee.academic_id == academic_id,
        SubjectDetail.level_id == level_id,
    )


def _registered_detail_query_for_subject(
    db: Session,
    academic_id: str,
    level_id: str,
    subject_detail_id: str,
):
    return _registered_detail_query(db, academic_id, level_id).filter(
        SubjectDetail.subject_detail_id == subject_detail_id,
    )


def _get_registered_details(
    db: Session,
    academic_id: str,
    level_id: str,
) -> list[RegistrationDetail]:
    return _registered_detail_query(db, academic_id, level_id).order_by(
        Subject.subject_name.asc(),
        Student.student_name.asc(),
        Student.student_lastname.asc(),
        Registration.registration_id.asc(),
    ).all()


def _get_registered_details_for_subject(
    db: Session,
    academic_id: str,
    level_id: str,
    subject_detail_id: str,
) -> list[RegistrationDetail]:
    return _registered_detail_query_for_subject(
        db,
        academic_id,
        level_id,
        subject_detail_id,
    ).order_by(
        Student.student_name.asc(),
        Student.student_lastname.asc(),
        Registration.registration_id.asc(),
    ).all()


def _repair_invalid_evaluation_semester(
    db: Session,
    semester: SemesterEnum,
):
    invalid_ids = [
        row[0]
        for row in db.execute(
            text(
                "SELECT evaluation_id FROM evaluation "
                "WHERE semester = '' "
                "ORDER BY evaluation_date DESC, evaluation_id DESC"
            )
        ).fetchall()
    ]

    if len(invalid_ids) != 1:
        return None

    db.execute(
        text(
            "UPDATE evaluation SET semester = :semester "
            "WHERE evaluation_id = :evaluation_id AND semester = ''"
        ),
        {
            'semester': semester.value,
            'evaluation_id': invalid_ids[0],
        },
    )
    db.commit()

    return db.query(Evaluation).filter(
        Evaluation.evaluation_id == invalid_ids[0],
    ).first()


def _get_evaluation(db: Session, semester: SemesterEnum):
    obj = db.query(Evaluation).filter(
        Evaluation.semester == semester,
    ).order_by(
        Evaluation.evaluation_date.desc(),
        Evaluation.evaluation_id.desc(),
    ).first()
    if obj is not None:
        return obj

    return _repair_invalid_evaluation_semester(db, semester)


def _get_or_create_evaluation(
    db: Session,
    semester: SemesterEnum,
    evaluation_date: date,
):
    obj = _get_evaluation(db, semester)
    if obj:
        obj.evaluation_date = evaluation_date
        db.flush()
        return obj

    obj = Evaluation(
        evaluation_id=_generate_evaluation_id(db),
        semester=semester,
        evaluation_date=evaluation_date,
    )
    db.add(obj)
    db.flush()
    return obj


def _quantize_score(score: Decimal) -> Decimal:
    return score.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _normalize_prize(prize: Decimal | str | None) -> Decimal | None:
    if prize is None:
        return None

    if isinstance(prize, Decimal):
        amount = prize
    else:
        cleaned = prize.replace(',', '').strip()
        if not cleaned:
            return None
        amount = Decimal(cleaned)

    if amount < 0:
        raise ValidationException('prize ຕ້ອງບໍ່ຕ່ຳກວ່າ 0')

    return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _prize_for_rank(rank: int, fee_amount: Decimal) -> Decimal | None:
    percentages = {
        1: Decimal('0.50'),
        2: Decimal('0.40'),
        3: Decimal('0.30'),
    }
    percentage = percentages.get(rank)
    if percentage is None:
        return None

    return str((fee_amount * percentage).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def _build_summary(
    students: list[ScoreEntryStudentResponse],
) -> ScoreEntrySummaryResponse:
    entered_scores = [item.score for item in students if item.score is not None]
    total_students = len(students)
    entered_students = len(entered_scores)
    average_score = None
    highest_score = None
    lowest_score = None

    if entered_scores:
        total = sum(entered_scores, Decimal('0'))
        average_score = (total / Decimal(entered_students)).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP,
        )
        highest_score = max(entered_scores)
        lowest_score = min(entered_scores)

    return ScoreEntrySummaryResponse(
        total_students=total_students,
        entered_students=entered_students,
        missing_students=total_students - entered_students,
        highest_score=highest_score,
        lowest_score=lowest_score,
        average_score=average_score,
    )


def _score_map(
    db: Session,
    evaluation_id: str,
    regis_detail_ids: set[int] | None = None,
) -> dict[int, EvaluationDetail]:
    query = db.query(EvaluationDetail).filter(
        EvaluationDetail.evaluation_id == evaluation_id,
    )
    if regis_detail_ids is not None:
        query = query.filter(EvaluationDetail.regis_detail_id.in_(regis_detail_ids))
    return {detail.regis_detail_id: detail for detail in query.all()}


def _delete_evaluation_if_empty(db: Session, evaluation_id: str) -> bool:
    remaining_count = db.query(EvaluationDetail).filter(
        EvaluationDetail.evaluation_id == evaluation_id,
    ).count()

    if remaining_count > 0:
        return False

    evaluation = db.query(Evaluation).filter(
        Evaluation.evaluation_id == evaluation_id,
    ).first()
    if evaluation is None:
        return False

    db.delete(evaluation)
    return True


def _recompute_rankings(db: Session, evaluation_id: str):
    details = db.query(EvaluationDetail).options(
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.fee_rel),
    ).filter(
        EvaluationDetail.evaluation_id == evaluation_id,
    ).all()

    groups: dict[str, list[EvaluationDetail]] = defaultdict(list)
    for detail in details:
        subject_detail_id = detail.registration_detail.fee_rel.subject_detail_id
        groups[subject_detail_id].append(detail)

    for group_items in groups.values():
        ranked_entries = sorted(
            group_items,
            key=lambda item: (-float(item.score), item.regis_detail_id),
        )
        current_rank = 0
        previous_score: Decimal | None = None

        for index, item in enumerate(ranked_entries, start=1):
            if previous_score is None or item.score != previous_score:
                current_rank = index
                previous_score = item.score
            item.ranking = current_rank
            item.prize = _prize_for_rank(current_rank, item.registration_detail.fee_rel.fee)


def _subject_option_query(db: Session, academic_id: str):
    return db.query(Fee).options(
        joinedload(Fee.subject_detail).joinedload(SubjectDetail.subject),
        joinedload(Fee.subject_detail).joinedload(SubjectDetail.level),
    ).join(
        SubjectDetail, SubjectDetail.subject_detail_id == Fee.subject_detail_id,
    ).join(
        Subject, Subject.subject_id == SubjectDetail.subject_id,
    ).filter(
        Fee.academic_id == academic_id,
    ).order_by(
        Subject.subject_name.asc(),
        Subject.subject_id.asc(),
        SubjectDetail.level_id.asc(),
        Fee.subject_detail_id.asc(),
    )


def _level_option_query(db: Session, academic_id: str, subject_id: str):
    return _subject_option_query(db, academic_id).filter(
        SubjectDetail.subject_id == subject_id,
    ).order_by(
        SubjectDetail.level_id.asc(),
        Fee.subject_detail_id.asc(),
    )


def _sort_student_rows(
    students: list[ScoreEntryStudentResponse],
) -> list[ScoreEntryStudentResponse]:
    def _rank_key(item: ScoreEntryStudentResponse):
        return item.ranking if item.ranking is not None else 10_000

    return sorted(
        students,
        key=lambda item: (
            _rank_key(item),
            item.full_name.lower(),
            item.registration_id.lower(),
        ),
    )


def _build_student_rows(
    registrations: list[RegistrationDetail],
    scores_by_regis_detail_id: dict[int, Decimal | None],
    prize_overrides: dict[int, Decimal | None] | None = None,
) -> list[ScoreEntryStudentResponse]:
    grouped_items: dict[str, list[tuple[RegistrationDetail, Decimal]]] = defaultdict(list)
    rows_by_regis_detail_id: dict[int, ScoreEntryStudentResponse] = {}

    for item in registrations:
        registration = item.registration
        student = registration.student
        subject_detail = item.fee_rel.subject_detail
        subject = subject_detail.subject
        full_name = f'{student.student_name} {student.student_lastname}'.strip()
        score = scores_by_regis_detail_id.get(item.regis_detail_id)
        row = ScoreEntryStudentResponse(
            regis_detail_id=item.regis_detail_id,
            registration_id=registration.registration_id,
            student_id=student.student_id,
            student_name=student.student_name,
            student_lastname=student.student_lastname,
            full_name=full_name,
            subject_detail_id=subject_detail.subject_detail_id,
            subject_id=subject.subject_id,
            subject_name=subject.subject_name,
            fee_amount=item.fee_rel.fee,
            score=score,
            ranking=None,
            prize=None,
        )
        rows_by_regis_detail_id[item.regis_detail_id] = row
        if score is not None:
            grouped_items[subject_detail.subject_detail_id].append((item, score))

    for subject_rows in grouped_items.values():
        ranked_rows = sorted(
            subject_rows,
            key=lambda pair: (
                -float(pair[1]),
                pair[0].registration.student.student_name.lower(),
                pair[0].registration.student.student_lastname.lower(),
                pair[0].registration.registration_id.lower(),
            ),
        )

        previous_score: Decimal | None = None
        current_rank = 0
        for index, (item, score) in enumerate(ranked_rows, start=1):
            row = rows_by_regis_detail_id[item.regis_detail_id]
            if previous_score is None or score != previous_score:
                current_rank = index
                previous_score = score

            row.ranking = current_rank
            auto_prize = _prize_for_rank(current_rank, item.fee_rel.fee)
            override = None
            if prize_overrides is not None and item.regis_detail_id in prize_overrides:
                override = prize_overrides[item.regis_detail_id]
            row.prize = override if override is not None else auto_prize

    return _sort_student_rows(list(rows_by_regis_detail_id.values()))


def _build_sheet_response(
    academic_year: AcademicYear,
    semester_enum: SemesterEnum,
    registrations: list[RegistrationDetail],
    students: list[ScoreEntryStudentResponse],
    evaluation: Evaluation | None,
) -> ScoreEntrySheetResponse:
    first_registration = registrations[0]
    subject_detail = first_registration.fee_rel.subject_detail
    subject = subject_detail.subject
    level = subject_detail.level
    return ScoreEntrySheetResponse(
        academic_id=academic_year.academic_id,
        academic_year=academic_year.academic_year,
        semester=semester_enum.value,
        level_id=level.level_id,
        level_name=level.level_name,
        subject_detail_id=subject_detail.subject_detail_id,
        subject_id=subject.subject_id,
        subject_name=subject.subject_name,
        evaluation_id=evaluation.evaluation_id if evaluation else None,
        evaluation_date=evaluation.evaluation_date if evaluation else None,
        summary=_build_summary(students),
        students=students,
    )


def _validated_score_payload(
    registrations: list[RegistrationDetail],
    scores: list,
) -> tuple[dict[int, Decimal | None], dict[int, Decimal | None]]:
    valid_ids = {item.regis_detail_id for item in registrations}
    scores_by_regis_detail_id: dict[int, Decimal | None] = {}
    prize_overrides: dict[int, Decimal | None] = {}

    for row in scores:
        if row.regis_detail_id not in valid_ids:
            raise ValidationException(
                f'regis_detail_id {row.regis_detail_id} ບໍ່ໄດ້ລົງທະບຽນໃນວິຊານີ້'
            )
        scores_by_regis_detail_id[row.regis_detail_id] = (
            _quantize_score(row.score) if row.score is not None else None
        )
        prize_overrides[row.regis_detail_id] = _normalize_prize(row.prize)

    return scores_by_regis_detail_id, prize_overrides


def get_all(db: Session):
    return db.query(Evaluation).all()


def get_by_id(db: Session, evaluation_id: str):
    return db.query(Evaluation).filter(Evaluation.evaluation_id == evaluation_id).first()


def create(db: Session, data: EvaluationCreate):
    obj = Evaluation(
        evaluation_id=_generate_evaluation_id(db),
        semester=_parse_semester(data.semester),
        evaluation_date=data.evaluation_date,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, evaluation_id: str, data: EvaluationUpdate):
    obj = get_by_id(db, evaluation_id)
    if not obj:
        return None
    payload = data.model_dump(exclude_none=True)
    if 'semester' in payload:
        payload['semester'] = _parse_semester(payload['semester'])
    for field, value in payload.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, evaluation_id: str) -> bool:
    obj = get_by_id(db, evaluation_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def get_score_entry_sheet(
    db: Session,
    semester: str,
    level_id: str,
    subject_detail_id: str,
) -> ScoreEntrySheetResponse:
    academic_year = _get_active_academic_year(db)
    semester_enum = _parse_semester(semester)
    registrations = _get_registered_details_for_subject(
        db,
        academic_year.academic_id,
        level_id,
        subject_detail_id,
    )
    if not registrations:
        raise ValidationException('ບໍ່ພົບນັກຮຽນທີ່ລົງທະບຽນໃນວິຊານີ້')

    evaluation = _get_evaluation(db, semester_enum)
    score_values: dict[int, Decimal | None] = {
        item.regis_detail_id: None for item in registrations
    }
    prize_overrides: dict[int, Decimal | None] = {}

    if evaluation:
        detail_map = _score_map(
            db,
            evaluation.evaluation_id,
            {item.regis_detail_id for item in registrations},
        )
        for regis_detail_id, detail in detail_map.items():
            score_values[regis_detail_id] = detail.score
            prize_overrides[regis_detail_id] = _normalize_prize(detail.prize)

    student_rows = _build_student_rows(
        registrations,
        score_values,
        prize_overrides,
    )

    return _build_sheet_response(
        academic_year,
        semester_enum,
        registrations,
        student_rows,
        evaluation,
    )


def get_score_entry_subjects(
    db: Session,
) -> list[ScoreEntrySubjectResponse]:
    academic_year = _get_active_academic_year(db)
    subject_map: dict[str, ScoreEntrySubjectResponse] = {}
    for item in _subject_option_query(db, academic_year.academic_id).all():
        subject = item.subject_detail.subject
        subject_map.setdefault(
            subject.subject_id,
            ScoreEntrySubjectResponse(
                subject_id=subject.subject_id,
                subject_name=subject.subject_name,
            ),
        )
    return list(subject_map.values())


def get_score_entry_levels(
    db: Session,
    subject_id: str,
) -> list[ScoreEntryLevelResponse]:
    academic_year = _get_active_academic_year(db)
    return [
        ScoreEntryLevelResponse(
            subject_detail_id=item.subject_detail.subject_detail_id,
            level_id=item.subject_detail.level.level_id,
            level_name=item.subject_detail.level.level_name,
            fee_amount=item.fee,
        )
        for item in _level_option_query(db, academic_year.academic_id, subject_id).all()
    ]


def preview_score_entry_sheet(
    db: Session,
    data: ScoreEntrySaveRequest,
) -> ScoreEntrySheetResponse:
    academic_year = _get_active_academic_year(db)
    semester_enum = _parse_semester(data.semester)
    registrations = _get_registered_details_for_subject(
        db,
        academic_year.academic_id,
        data.level_id,
        data.subject_detail_id,
    )
    if not registrations:
        raise ValidationException('ບໍ່ພົບນັກຮຽນທີ່ລົງທະບຽນໃນວິຊານີ້')

    scores_by_regis_detail_id, prize_overrides = _validated_score_payload(
        registrations,
        data.scores,
    )
    evaluation = _get_evaluation(db, semester_enum)
    student_rows = _build_student_rows(
        registrations,
        scores_by_regis_detail_id,
        prize_overrides,
    )
    return _build_sheet_response(
        academic_year,
        semester_enum,
        registrations,
        student_rows,
        evaluation,
    )


def save_score_entry_sheet(
    db: Session,
    data: ScoreEntrySaveRequest,
) -> ScoreEntrySheetResponse:
    academic_year = _get_active_academic_year(db)
    semester_enum = _parse_semester(data.semester)
    registrations = _get_registered_details_for_subject(
        db,
        academic_year.academic_id,
        data.level_id,
        data.subject_detail_id,
    )
    valid_registration_details = {
        item.regis_detail_id: item for item in registrations
    }

    if not valid_registration_details:
        raise ValidationException('ບໍ່ພົບນັກຮຽນທີ່ລົງທະບຽນໃນວິຊານີ້')

    _, prize_overrides = _validated_score_payload(registrations, data.scores)

    evaluation = _get_or_create_evaluation(
        db,
        semester_enum,
        data.evaluation_date,
    )
    existing_map = _score_map(db, evaluation.evaluation_id)

    for row in data.scores:
        if row.regis_detail_id not in valid_registration_details:
            raise ValidationException(
                f'regis_detail_id {row.regis_detail_id} ບໍ່ໄດ້ລົງທະບຽນໃນລະດັບນີ້'
            )

        existing = existing_map.get(row.regis_detail_id)
        if row.score is None:
            if existing:
                db.delete(existing)
            continue

        score = _quantize_score(row.score)
        prize = prize_overrides.get(row.regis_detail_id)
        if existing:
            existing.score = score
            existing.prize = prize
        else:
            db.add(
                EvaluationDetail(
                    evaluation_id=evaluation.evaluation_id,
                    regis_detail_id=row.regis_detail_id,
                    score=score,
                    ranking=0,
                    prize=prize,
                )
            )

    db.flush()

    if not _delete_evaluation_if_empty(db, evaluation.evaluation_id):
        _recompute_rankings(db, evaluation.evaluation_id)
        refreshed_map = _score_map(
            db,
            evaluation.evaluation_id,
            set(valid_registration_details.keys()),
        )
        for regis_detail_id, detail in refreshed_map.items():
            if regis_detail_id in prize_overrides and prize_overrides[regis_detail_id] is not None:
                detail.prize = prize_overrides[regis_detail_id]

    db.commit()

    return get_score_entry_sheet(
        db,
        semester=data.semester,
        level_id=data.level_id,
        subject_detail_id=data.subject_detail_id,
    )


def get_assessment_report(
    db: Session,
    academic_id: str | None,
    semester: str,
    evaluation_type: str | None = None,
    subject_id: str | None = None,
    level_id: str | None = None,
    ranking: int | None = None,
) -> list[AssessmentReportItemResponse]:
    semester_value = semester.strip().lower()
    semester_enum = None if semester_value in {'all', 'all_semesters'} else _parse_semester(semester)
    resolved_academic_id = academic_id or _get_active_academic_year(db).academic_id

    query = db.query(EvaluationDetail).options(
        joinedload(EvaluationDetail.evaluation),
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.registration)
        .joinedload(Registration.student)
        .joinedload(Student.district)
        .joinedload(District.province),
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.academic_year),
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.subject),
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.level),
    ).join(
        Evaluation, Evaluation.evaluation_id == EvaluationDetail.evaluation_id,
    ).join(
        RegistrationDetail,
        RegistrationDetail.regis_detail_id == EvaluationDetail.regis_detail_id,
    ).join(
        Registration, Registration.registration_id == RegistrationDetail.registration_id,
    ).join(
        Student, Student.student_id == Registration.student_id,
    ).join(
        Fee, Fee.fee_id == RegistrationDetail.fee_id,
    ).join(
        SubjectDetail, SubjectDetail.subject_detail_id == Fee.subject_detail_id,
    ).filter(
        Fee.academic_id == resolved_academic_id,
    )

    if semester_enum is not None:
        query = query.filter(Evaluation.semester == semester_enum)

    if subject_id:
        query = query.filter(SubjectDetail.subject_id == subject_id)
    if level_id:
        query = query.filter(SubjectDetail.level_id == level_id)
    if ranking:
        query = query.filter(EvaluationDetail.ranking == ranking)

    rows = query.join(
        Subject, Subject.subject_id == SubjectDetail.subject_id,
    ).join(
        Level, Level.level_id == SubjectDetail.level_id,
    ).order_by(
        Subject.subject_name.asc(),
        Level.level_name.asc(),
        EvaluationDetail.ranking.asc(),
        EvaluationDetail.score.desc(),
        Student.student_name.asc(),
        Student.student_lastname.asc(),
    ).all()

    return [
        AssessmentReportItemResponse(
            evaluation_id=row.evaluation_id,
            academic_id=row.registration_detail.fee_rel.academic_id,
            academic_year=getattr(row.registration_detail.fee_rel.academic_year, 'academic_year', None),
            semester=row.evaluation.semester.value,
            evaluation_type=None,
            subject_id=row.registration_detail.fee_rel.subject_detail.subject.subject_id,
            level_id=row.registration_detail.fee_rel.subject_detail.level.level_id,
            student_id=row.registration_detail.registration.student.student_id,
            student_name=row.registration_detail.registration.student.student_name,
            student_lastname=row.registration_detail.registration.student.student_lastname,
            full_name=f"{row.registration_detail.registration.student.student_name} {row.registration_detail.registration.student.student_lastname}".strip(),
            province_name=(
                row.registration_detail.registration.student.district.province.province_name
                if row.registration_detail.registration.student.district
                and row.registration_detail.registration.student.district.province
                else None
            ),
            district_name=(
                row.registration_detail.registration.student.district.district_name
                if row.registration_detail.registration.student.district
                else None
            ),
            subject_name=row.registration_detail.fee_rel.subject_detail.subject.subject_name,
            level_name=row.registration_detail.fee_rel.subject_detail.level.level_name,
            score=row.score,
            ranking=row.ranking,
            prize=row.prize,
        )
        for row in rows
    ]


def get_student_transcript(
    db: Session,
    student_id: str,
    academic_id: str | None = None,
    semester: str | None = None,
    evaluation_type: str | None = None,
) -> list[StudentTranscriptItemResponse]:
    query = db.query(EvaluationDetail).options(
        joinedload(EvaluationDetail.evaluation),
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.registration)
        .joinedload(Registration.student),
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.academic_year),
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.subject),
        joinedload(EvaluationDetail.registration_detail)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.level),
    ).join(
        Evaluation, Evaluation.evaluation_id == EvaluationDetail.evaluation_id,
    ).join(
        RegistrationDetail,
        RegistrationDetail.regis_detail_id == EvaluationDetail.regis_detail_id,
    ).join(
        Registration, Registration.registration_id == RegistrationDetail.registration_id,
    ).join(
        Fee, Fee.fee_id == RegistrationDetail.fee_id,
    ).filter(
        Registration.student_id == student_id,
    )

    if academic_id:
        query = query.filter(Fee.academic_id == academic_id)
    if semester:
        query = query.filter(Evaluation.semester == _parse_semester(semester))

    rows = query.order_by(
        Fee.academic_id.desc(),
        Evaluation.evaluation_date.desc(),
        EvaluationDetail.score.desc(),
    ).all()

    return [
        StudentTranscriptItemResponse(
            evaluation_id=row.evaluation_id,
            academic_id=row.registration_detail.fee_rel.academic_id,
            academic_year=getattr(row.registration_detail.fee_rel.academic_year, 'academic_year', None),
            semester=row.evaluation.semester.value,
            evaluation_type=None,
            subject_name=row.registration_detail.fee_rel.subject_detail.subject.subject_name,
            level_name=row.registration_detail.fee_rel.subject_detail.level.level_name,
            score=row.score,
            ranking=row.ranking,
            prize=row.prize,
        )
        for row in rows
    ]
