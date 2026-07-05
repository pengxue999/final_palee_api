from typing import Any, Dict, Optional

from openpyxl import Workbook

from sqlalchemy.orm import Session, joinedload

from app.enums.registration_status import RegistrationStatusEnum
from app.models.district import District
from app.models.fee import Fee
from app.models.level import Level
from app.models.registration import Registration
from app.models.registration_detail import RegistrationDetail
from app.models.student import Student
from app.models.subject import Subject
from app.models.subject_detail import SubjectDetail
from app.services.reporting.common import (
    apply_excel_title,
    create_csv_writer,
    create_excel_theme,
    current_timestamp,
    finalize_workbook_export,
    finalize_csv_export,
    format_report_datetime,
    set_excel_column_widths,
    write_excel_key_value_rows,
    write_excel_table_headers,
    write_excel_table_rows,
    resolve_academic_year_name,
)
from app.utils.enum_localization import (
    localize_gender,
    localize_registration_status,
)


_VALID_STATUSES = [
    RegistrationStatusEnum.PAID,
    RegistrationStatusEnum.UNPAID,
    RegistrationStatusEnum.PARTIAL,
]


def _normalize_statuses(status: Optional[str]) -> list[str]:
    if not status:
        return []

    raw = str(status).strip().upper()
    if raw in {"ALL", "*"}:
        return []
    if raw == "PAID_PARTIAL":
        return [
            RegistrationStatusEnum.PAID.value,
            RegistrationStatusEnum.PARTIAL.value,
        ]

    valid_values = {item.value for item in _VALID_STATUSES}
    result: list[str] = []
    for part in raw.split(","):
        token = part.strip()
        if "." in token:
            token = token.split(".")[-1].strip()
        if token in valid_values and token not in result:
            result.append(token)
    return result


def _resolve_subject_name(db: Session, subject_id: Optional[str]) -> Optional[str]:
    if not subject_id:
        return None
    subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    return subject.subject_name if subject else None


def _resolve_level_name(db: Session, level_id: Optional[str]) -> Optional[str]:
    if not level_id:
        return None
    level = db.query(Level).filter(Level.level_id == level_id).first()
    return level.level_name if level else None


def get_registration_report(
    db: Session,
    academic_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    level_id: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    normalized_statuses = _normalize_statuses(status)

    def apply_scope_filters(query):
        if academic_id or subject_id or level_id:
            query = (
                query.join(
                    RegistrationDetail,
                    Registration.registration_id
                    == RegistrationDetail.registration_id,
                )
                .join(Fee, RegistrationDetail.fee_id == Fee.fee_id)
                .join(
                    SubjectDetail,
                    Fee.subject_detail_id == SubjectDetail.subject_detail_id,
                )
            )
            if academic_id:
                query = query.filter(Fee.academic_id == academic_id)
            if subject_id:
                query = query.filter(SubjectDetail.subject_id == subject_id)
            if level_id:
                query = query.filter(SubjectDetail.level_id == level_id)
            query = query.distinct()
        return query

    status_counts = {item.value: 0 for item in _VALID_STATUSES}
    scope_registrations = apply_scope_filters(db.query(Registration)).all()
    for registration in scope_registrations:
        status_value = (
            registration.status.value
            if registration.status is not None
            else None
        )
        if status_value in status_counts:
            status_counts[status_value] += 1

    query = apply_scope_filters(
        db.query(Registration).options(
            joinedload(Registration.student)
            .joinedload(Student.district)
            .joinedload(District.province),
        )
    )

    if normalized_statuses:
        query = query.filter(
            Registration.status.in_(
                [RegistrationStatusEnum(value) for value in normalized_statuses]
            )
        )

    registrations = query.order_by(Registration.registration_date.desc()).all()

    registration_list = []
    for registration in registrations:
        student = registration.student
        district = student.district if student else None
        province = district.province if district else None
        status_value = (
            registration.status.value
            if registration.status is not None
            else None
        )

        registration_list.append(
            {
                "registration_id": registration.registration_id,
                "student_id": student.student_id if student else None,
                "full_name": (
                    f"{student.student_name} {student.student_lastname}"
                    if student
                    else None
                ),
                "gender": localize_gender(student.gender) if student else None,
                "school": student.school if student else None,
                "district_name": district.district_name if district else None,
                "province_name": province.province_name if province else None,
                "status": status_value,
                "status_label": localize_registration_status(status_value),
            }
        )

    status_label = " + ".join(
        localize_registration_status(value) for value in normalized_statuses
    )

    return {
        "filters": {
            "academic_id": academic_id,
            "academic_year_name": resolve_academic_year_name(db, academic_id),
            "subject_id": subject_id,
            "subject_name": _resolve_subject_name(db, subject_id),
            "level_id": level_id,
            "level_name": _resolve_level_name(db, level_id),
            "status": ",".join(normalized_statuses) if normalized_statuses else None,
            "status_label": status_label or None,
        },
        "total_count": len(registration_list),
        "summary": {
            "total": len(scope_registrations),
            "paid": status_counts[RegistrationStatusEnum.PAID.value],
            "unpaid": status_counts[RegistrationStatusEnum.UNPAID.value],
            "partial": status_counts[RegistrationStatusEnum.PARTIAL.value],
        },
        "registrations": registration_list,
    }


def export_registration_report(
    db: Session,
    academic_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    level_id: Optional[str] = None,
    status: Optional[str] = None,
    format: str = "excel",
) -> Dict[str, Any]:
    report_data = get_registration_report(
        db,
        academic_id=academic_id,
        subject_id=subject_id,
        level_id=level_id,
        status=status,
    )

    registrations = report_data["registrations"]
    normalized_format = format.lower()

    headers = [
        "ລະຫັດການລົງທະບຽນ",
        "ລະຫັດນັກຮຽນ",
        "ຊື່-ນາມສະກຸນ",
        "ເພດ",
        "ໂຮງຮຽນ",
        "ເມືອງ",
        "ແຂວງ",
        "ສະຖານະ",
    ]

    def row_values(registration: Dict[str, Any]) -> list:
        return [
            registration["registration_id"],
            registration["student_id"] or "-",
            registration["full_name"] or "-",
            registration["gender"] or "-",
            registration["school"] or "-",
            registration["district_name"] or "-",
            registration["province_name"] or "-",
            registration["status_label"] or "-",
        ]

    if normalized_format == "csv":
        output, writer = create_csv_writer()
        writer.writerow(headers)
        for registration in registrations:
            writer.writerow(row_values(registration))

        filename = f"registration_report_{current_timestamp()}.csv"
        return finalize_csv_export(
            output, filename=filename, total_records=len(registrations)
        )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Registrations"
    theme = create_excel_theme()

    apply_excel_title(
        sheet,
        title="ລາຍງານການລົງທະບຽນ",
        from_column=1,
        to_column=len(headers),
        theme=theme,
    )

    summary = report_data["summary"]
    write_excel_key_value_rows(
        sheet,
        rows=[
            ("ວັນທີສ້າງ", format_report_datetime()),
            ("ສົກຮຽນ", report_data["filters"].get("academic_year_name") or "ທັງໝົດ"),
            ("ວິຊາ", report_data["filters"].get("subject_name") or "ທັງໝົດ"),
            ("ລະດັບ/ຊັ້ນຮຽນ", report_data["filters"].get("level_name") or "ທັງໝົດ"),
            ("ສະຖານະການຊຳລະ", report_data["filters"].get("status_label") or "ທັງໝົດ"),
            ("ທັງໝົດ", summary["total"]),
            ("ຈ່າຍແລ້ວ", summary["paid"]),
            ("ຈ່າຍບາງສ່ວນ", summary["partial"]),
            ("ຍັງບໍ່ທັນຈ່າຍ", summary["unpaid"]),
        ],
        start_row=3,
        theme=theme,
    )

    header_row = 14
    write_excel_table_headers(sheet, headers=headers, row_index=header_row, theme=theme)
    write_excel_table_rows(
        sheet,
        rows=[row_values(registration) for registration in registrations],
        start_row=header_row + 1,
        theme=theme,
    )

    sheet.freeze_panes = f"A{header_row + 1}"
    sheet.auto_filter.ref = (
        f"A{header_row}:H{max(header_row, header_row + len(registrations))}"
    )
    set_excel_column_widths(
        sheet,
        {
            1: 18,
            2: 16,
            3: 26,
            4: 10,
            5: 24,
            6: 16,
            7: 16,
            8: 16,
        },
    )

    filename = f"registration_report_{current_timestamp()}.xlsx"
    return finalize_workbook_export(
        workbook, filename=filename, total_records=len(registrations)
    )
