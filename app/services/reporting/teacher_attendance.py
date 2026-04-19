from typing import Any, Dict, Optional

from openpyxl import Workbook

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.subject_detail import SubjectDetail
from app.models.teacher_assignment import TeacherAssignment
from app.models.teaching_log import TeachingLog
from app.services.reporting.common import (
    apply_excel_title,
    create_csv_writer,
    create_excel_theme,
    current_timestamp,
    finalize_workbook_export,
    finalize_csv_export,
    format_report_currency,
    format_report_date,
    format_report_datetime,
    set_excel_column_widths,
    write_excel_key_value_rows,
    write_excel_table_headers,
    write_excel_table_rows,
    resolve_academic_year_name,
    resolve_teacher_name,
)


def get_teacher_attendance_report(
    db: Session,
    academic_id: Optional[str] = None,
    month: Optional[str] = None,
    status: Optional[str] = None,
    teacher_id: Optional[str] = None,
) -> Dict[str, Any]:
    query = db.query(TeachingLog).options(
        joinedload(TeachingLog.assignment).joinedload(TeacherAssignment.teacher),
        joinedload(TeachingLog.assignment)
        .joinedload(TeacherAssignment.subject_detail)
        .joinedload(SubjectDetail.subject),
        joinedload(TeachingLog.assignment)
        .joinedload(TeacherAssignment.subject_detail)
        .joinedload(SubjectDetail.level),
        joinedload(TeachingLog.assignment).joinedload(TeacherAssignment.academic_year),
        joinedload(TeachingLog.substitute_assignment).joinedload(TeacherAssignment.teacher),
        joinedload(TeachingLog.substitute_assignment)
        .joinedload(TeacherAssignment.subject_detail)
        .joinedload(SubjectDetail.subject),
    )

    needs_assignment_join = academic_id is not None or teacher_id is not None
    if needs_assignment_join:
        query = query.join(
            TeacherAssignment,
            TeachingLog.assignment_id == TeacherAssignment.assignment_id,
        )

        if academic_id:
            query = query.filter(TeacherAssignment.academic_id == academic_id)
        if teacher_id:
            query = query.filter(TeacherAssignment.teacher_id == teacher_id)

    if status:
        query = query.filter(TeachingLog.status == status)

    if month:
        year, month_number = month.split("-")
        query = query.filter(
            func.extract("year", TeachingLog.teaching_date) == int(year),
            func.extract("month", TeachingLog.teaching_date) == int(month_number),
        )

    logs = query.order_by(TeachingLog.teaching_date.desc()).all()

    log_list = []
    for log in logs:
        assignment = log.assignment
        teacher = assignment.teacher if assignment else None
        subject_detail = assignment.subject_detail if assignment else None
        level = subject_detail.level if subject_detail else None
        academic_year = assignment.academic_year if assignment else None

        is_substitute = log.substitute_for_assignment_id is not None
        substitute_teacher = None
        substitute_subject = None
        if is_substitute and log.substitute_assignment:
            substitute_teacher = log.substitute_assignment.teacher
            substitute_subject = log.substitute_assignment.subject_detail

        hourly = float(log.hourly) if log.hourly else 0
        hourly_rate = (
            float(assignment.hourly_rate)
            if assignment and assignment.hourly_rate
            else 0
        )
        total_amount = hourly * hourly_rate

        log_list.append(
            {
                "teaching_log_id": log.teaching_log_id,
                "teacher_id": teacher.teacher_id if teacher else None,
                "teacher_name": teacher.teacher_name if teacher else None,
                "teacher_lastname": teacher.teacher_lastname if teacher else None,
                "full_name": (
                    f"{teacher.teacher_name} {teacher.teacher_lastname}"
                    if teacher
                    else None
                ),
                "subject_name": (
                    subject_detail.subject.subject_name
                    if subject_detail and subject_detail.subject
                    else None
                ),
                "level_name": level.level_name if level else None,
                "academic_year": academic_year.academic_year if academic_year else None,
                "teaching_date": (
                    log.teaching_date.strftime("%Y-%m-%d") if log.teaching_date else None
                ),
                "status": log.status,
                "hourly": hourly,
                "hourly_rate": hourly_rate,
                "total_amount": total_amount,
                "remark": log.remark,
                "is_substitute": is_substitute,
                "substitute_for_teacher_name": (
                    substitute_teacher.teacher_name if substitute_teacher else None
                ),
                "substitute_for_teacher_lastname": (
                    substitute_teacher.teacher_lastname if substitute_teacher else None
                ),
                "substitute_for_subject_name": (
                    substitute_subject.subject.subject_name
                    if substitute_subject and substitute_subject.subject
                    else None
                ),
            }
        )

    return {
        "filters": {
            "academic_id": academic_id,
            "academic_year_name": resolve_academic_year_name(db, academic_id),
            "month": month,
            "status": status,
            "teacher_id": teacher_id,
            "teacher_name": resolve_teacher_name(db, teacher_id),
        },
        "total_count": len(log_list),
        "logs": log_list,
    }


def export_teacher_attendance_report(
    db: Session,
    academic_id: Optional[str] = None,
    month: Optional[str] = None,
    status: Optional[str] = None,
    teacher_id: Optional[str] = None,
    format: str = "excel",
) -> Dict[str, Any]:
    report_data = get_teacher_attendance_report(
        db,
        academic_id=academic_id,
        month=month,
        status=status,
        teacher_id=teacher_id,
    )
    logs = report_data["logs"]
    normalized_format = format.lower()

    taught_count = len([log for log in logs if log["status"] == "ຂຶ້ນສອນ"])
    absent_count = len([log for log in logs if log["status"] == "ຂາດສອນ"])
    total_hours = sum(float(log["hourly"] or 0) for log in logs if log["status"] == "ຂຶ້ນສອນ")
    total_amount = sum(float(log["total_amount"] or 0) for log in logs if log["status"] == "ຂຶ້ນສອນ")

    headers = [
        "ອາຈານ",
        "ວິຊາ",
        "ລະດັບ",
        "ສົກຮຽນ",
        "ວັນທີສອນ",
        "ສະຖານະ",
        "ຊົ່ວໂມງ",
        "ຄ່າສອນ/ຊມ",
        "ຈຳນວນເງິນ",
        "ໝາຍເຫດ",
        "ອາຈານທີ່ໃຫ້ສອນແທນ",
        "ວິຊາທີ່ໃຫ້ສອນແທນ",
    ]

    if normalized_format == "csv":
        output, writer = create_csv_writer()
        writer.writerow(headers)

        for log in logs:
            writer.writerow(
                [
                    log["full_name"] or "",
                    log["subject_name"] or (log["substitute_for_subject_name"] or ""),
                    log["level_name"] or "",
                    log["academic_year"] or "",
                    format_report_date(log["teaching_date"]),
                    log["status"] or "",
                    log["hourly"],
                    log["hourly_rate"],
                    log["total_amount"],
                    log["remark"] or "",
                    (
                        f"{log['substitute_for_teacher_name'] or ''} {log['substitute_for_teacher_lastname'] or ''}".strip()
                        if log["substitute_for_teacher_name"]
                        else ""
                    ),
                    log["substitute_for_subject_name"] or "",
                ]
            )

        teacher_part = teacher_id or "ທັງໝົດ"
        filename = f"ລາຍງານການເຂົ້າສອນ_{teacher_part}.csv"
        return finalize_csv_export(output, filename=filename, total_records=len(logs))

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance"
    theme = create_excel_theme(title_color="0F766E", header_color="CCFBF1", summary_color="F0FDFA")

    apply_excel_title(
        sheet,
        title="ລາຍງານການຂື້ນສອນຂອງອາຈານ",
        from_column=1,
        to_column=len(headers),
        theme=theme,
    )
    write_excel_key_value_rows(
        sheet,
        rows=[
            ("ວັນທີສ້າງ", format_report_datetime()),
            ("ສົກຮຽນ", report_data["filters"].get("academic_year_name") or "ທັງໝົດ"),
            ("ເດືອນ", report_data["filters"].get("month") or "ທັງໝົດ"),
            ("ສະຖານະ", report_data["filters"].get("status") or "ທັງໝົດ"),
            ("ອາຈານ", report_data["filters"].get("teacher_name") or "ທັງໝົດ"),
            ("ຈຳນວນຂຶ້ນສອນ", taught_count),
            ("ຈຳນວນຂາດສອນ", absent_count),
            ("ຊົ່ວໂມງລວມ", total_hours),
            ("ຈຳນວນເງິນລວມ", format_report_currency(total_amount)),
        ],
        start_row=3,
        theme=theme,
    )

    header_row = 13
    write_excel_table_headers(sheet, headers=headers, row_index=header_row, theme=theme)
    write_excel_table_rows(
        sheet,
        rows=[
            [
                log["full_name"] or "-",
                log["subject_name"] or (log["substitute_for_subject_name"] or "-"),
                log["level_name"] or "-",
                log["academic_year"] or "-",
                format_report_date(log["teaching_date"]),
                log["status"] or "-",
                log["hourly"],
                log["hourly_rate"],
                log["total_amount"],
                log["remark"] or "-",
                (
                    f"{log['substitute_for_teacher_name'] or ''} {log['substitute_for_teacher_lastname'] or ''}".strip()
                    if log["substitute_for_teacher_name"]
                    else "-"
                ),
                log["substitute_for_subject_name"] or "-",
            ]
            for log in logs
        ],
        start_row=header_row + 1,
        theme=theme,
    )

    sheet.freeze_panes = f"A{header_row + 1}"
    sheet.auto_filter.ref = (
        f"A{header_row}:L{max(header_row, header_row + len(logs))}"
    )
    set_excel_column_widths(
        sheet,
        {
            1: 26,
            2: 22,
            3: 14,
            4: 16,
            5: 14,
            6: 12,
            7: 12,
            8: 14,
            9: 16,
            10: 24,
            11: 24,
            12: 24,
        },
    )

    filename = f"teacher_attendance_report_{current_timestamp()}.xlsx"
    return finalize_workbook_export(workbook, filename=filename, total_records=len(logs))