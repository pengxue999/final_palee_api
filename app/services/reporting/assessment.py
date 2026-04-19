from typing import Any, Dict, Optional

from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.enums.semester import SemesterEnum
from app.services import evaluation as evaluation_svc
from app.services.reporting.common import (
    apply_excel_title,
    create_csv_writer,
    create_excel_theme,
    current_timestamp,
    finalize_csv_export,
    finalize_workbook_export,
    format_report_currency,
    format_report_datetime,
    resolve_academic_year_name,
    set_excel_column_widths,
    write_excel_key_value_rows,
    write_excel_table_headers,
    write_excel_table_rows,
)


def _round_label(semester: str) -> str:
    if semester.lower() in {'all', 'all_semesters'}:
        return "ທັງໝົດ"
    if semester == 'Semester 1':
        return "ກາງພາກ"
    if semester == 'Semester 2':
        return "ທ້າຍພາກ"
    if semester == SemesterEnum.SEMESTER_1.value:
        return "ກາງພາກ"
    if semester == SemesterEnum.SEMESTER_2.value:
        return "ທ້າຍພາກ"
    return semester


def get_assessment_report_data(
    db: Session,
    *,
    academic_id: Optional[str],
    semester: str,
    subject_id: Optional[str] = None,
    level_id: Optional[str] = None,
    ranking: Optional[int] = None,
) -> Dict[str, Any]:
    items = evaluation_svc.get_assessment_report(
        db,
        academic_id=academic_id,
        semester=semester,
        subject_id=subject_id,
        level_id=level_id,
        ranking=ranking,
    )

    resolved_academic_id = academic_id
    if items:
        resolved_academic_id = items[0].academic_id

    return {
        "filters": {
            "academic_id": resolved_academic_id,
            "academic_year_name": resolve_academic_year_name(db, resolved_academic_id),
            "semester": semester,
            "evaluation_round_name": _round_label(semester),
            "subject_id": subject_id,
            "subject_name": items[0].subject_name if subject_id and items else None,
            "level_id": level_id,
            "level_name": items[0].level_name if level_id and items else None,
            "ranking": ranking,
        },
        "total_count": len(items),
        "items": [item.model_dump() for item in items],
    }


def export_assessment_report(
    db: Session,
    *,
    academic_id: Optional[str],
    semester: str,
    subject_id: Optional[str] = None,
    level_id: Optional[str] = None,
    ranking: Optional[int] = None,
    format: str = "excel",
) -> Dict[str, Any]:
    report_data = get_assessment_report_data(
        db,
        academic_id=academic_id,
        semester=semester,
        subject_id=subject_id,
        level_id=level_id,
        ranking=ranking,
    )
    items = report_data["items"]
    normalized_format = format.lower()

    headers = [
        "ລະຫັດນັກຮຽນ",
        "ນັກຮຽນ",
        "ແຂວງ",
        "ເມືອງ",
        "ວິຊາ",
        "ລະດັບ",
        "ຮອບປະເມີນ",
        "ຄະແນນ",
        "ອັນດັບ",
        "ລາງວັນ",
    ]

    if normalized_format == "csv":
        output, writer = create_csv_writer()
        writer.writerow(headers)
        for item in items:
            writer.writerow(
                [
                    item["student_id"],
                    item["full_name"],
                    item.get("province_name") or "-",
                    item.get("district_name") or "-",
                    item["subject_name"],
                    item["level_name"],
                    _round_label(item["semester"]),
                    item["score"],
                    item["ranking"],
                    item["prize"] or "-",
                ]
            )

        return finalize_csv_export(
            output,
            filename=f"assessment_report_{current_timestamp()}.csv",
            total_records=len(items),
        )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Assessment"
    theme = create_excel_theme(title_color="0F766E", header_color="CCFBF1", summary_color="F0FDFA")

    apply_excel_title(
        sheet,
        title="ລາຍງານຜົນການຮຽນ",
        from_column=1,
        to_column=len(headers),
        theme=theme,
    )

    filters = report_data["filters"]
    write_excel_key_value_rows(
        sheet,
        rows=[
            ("ວັນທີສ້າງ", format_report_datetime()),
            ("ສົກຮຽນ", filters.get("academic_year_name") or "ປັດຈຸບັນ"),
            ("ຮອບປະເມີນ", filters.get("evaluation_round_name") or "-"),
            ("ວິຊາ", filters.get("subject_name") or "ທັງໝົດ"),
            ("ລະດັບ", filters.get("level_name") or "ທັງໝົດ"),
            ("ອັນດັບ", filters.get("ranking") or "ທັງໝົດ"),
            ("ຈຳນວນລາຍການ", report_data["total_count"]),
        ],
        start_row=3,
        theme=theme,
    )

    header_row = 11
    write_excel_table_headers(sheet, headers=headers, row_index=header_row, theme=theme)
    write_excel_table_rows(
        sheet,
        rows=[
            [
                item["student_id"],
                item["full_name"],
                item.get("province_name") or "-",
                item.get("district_name") or "-",
                item["subject_name"],
                item["level_name"],
                _round_label(item["semester"]),
                item["score"],
                item["ranking"],
                format_report_currency(item["prize"], suffix="ກີບ") if item["prize"] else "-",
            ]
            for item in items
        ],
        start_row=header_row + 1,
        theme=theme,
    )

    sheet.freeze_panes = f"A{header_row + 1}"
    sheet.auto_filter.ref = f"A{header_row}:J{max(header_row, header_row + len(items))}"
    set_excel_column_widths(
        sheet,
        {1: 16, 2: 24, 3: 18, 4: 18, 5: 22, 6: 14, 7: 16, 8: 12, 9: 10, 10: 16},
    )

    return finalize_workbook_export(
        workbook,
        filename=f"assessment_report_{current_timestamp()}.xlsx",
        total_records=len(items),
    )