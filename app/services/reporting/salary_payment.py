from typing import Any, Dict, Optional

from openpyxl import Workbook
from sqlalchemy.orm import Session, joinedload

from app.models.salary_payment import SalaryPayment
from app.services.reporting.common import (
    apply_excel_title,
    create_csv_writer,
    create_excel_theme,
    current_timestamp,
    finalize_csv_export,
    finalize_workbook_export,
    format_report_currency,
    format_report_date,
    format_report_datetime,
    resolve_teacher_name,
    set_excel_column_widths,
    write_excel_key_value_rows,
    write_excel_table_headers,
    write_excel_table_rows,
)


def _month_name(month: Optional[int]) -> Optional[str]:
    month_names = {
        1: "ມັງກອນ",
        2: "ກຸມພາ",
        3: "ມີນາ",
        4: "ເມສາ",
        5: "ພຶດສະພາ",
        6: "ມິຖຸນາ",
        7: "ກໍລະກົດ",
        8: "ສິງຫາ",
        9: "ກັນຍາ",
        10: "ຕຸລາ",
        11: "ພະຈິກ",
        12: "ທັນວາ",
    }
    if month is None:
        return None
    return month_names.get(month, str(month))


def get_salary_payment_report(
    db: Session,
    month: Optional[int] = None,
    teacher_id: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    query = db.query(SalaryPayment).options(
        joinedload(SalaryPayment.teacher),
        joinedload(SalaryPayment.user),
    )

    if month is not None:
        query = query.filter(SalaryPayment.month == month)
    if teacher_id:
        query = query.filter(SalaryPayment.teacher_id == teacher_id)
    if status:
        query = query.filter(SalaryPayment.status == status)

    payments = query.order_by(
        SalaryPayment.payment_date.desc(),
        SalaryPayment.salary_payment_id.desc(),
    ).all()

    payment_list: list[dict[str, Any]] = []
    for payment in payments:
        teacher_name = "-"
        if payment.teacher:
            teacher_name = (
                f"{payment.teacher.teacher_name} {payment.teacher.teacher_lastname}"
            ).strip()

        user_name = payment.user.user_name if payment.user else "-"
        payment_year = payment.payment_date.year if payment.payment_date else None
        payment_list.append(
            {
                "salary_payment_id": payment.salary_payment_id,
                "teacher_id": payment.teacher_id,
                "teacher_name": teacher_name,
                "month": payment.month,
                "month_name": _month_name(payment.month),
                "year": payment_year,
                "total_amount": float(payment.total_amount or 0),
                "payment_date": (
                    payment.payment_date.strftime("%Y-%m-%d")
                    if payment.payment_date
                    else None
                ),
                "status": payment.status,
                "user_name": user_name,
            }
        )

    total_amount = sum(float(item["total_amount"] or 0) for item in payment_list)
    paid_count = sum(1 for item in payment_list if item["status"] == "ຈ່າຍແລ້ວ")
    pending_count = len(payment_list) - paid_count
    unique_teacher_count = len({item["teacher_id"] for item in payment_list})

    return {
        "filters": {
            "month": month,
            "month_name": _month_name(month),
            "teacher_id": teacher_id,
            "teacher_name": resolve_teacher_name(db, teacher_id),
            "status": status,
        },
        "summary": {
            "total_amount": total_amount,
            "paid_count": paid_count,
            "pending_count": pending_count,
            "unique_teacher_count": unique_teacher_count,
        },
        "total_count": len(payment_list),
        "payments": payment_list,
    }


def export_salary_payment_report(
    db: Session,
    month: Optional[int] = None,
    teacher_id: Optional[str] = None,
    status: Optional[str] = None,
    format: str = "excel",
) -> Dict[str, Any]:
    report_data = get_salary_payment_report(
        db,
        month=month,
        teacher_id=teacher_id,
        status=status,
    )
    payments = report_data["payments"]
    summary = report_data["summary"]
    normalized_format = format.lower()

    headers = [
        "ລະຫັດ",
        "ອາຈານ",
        "ເດືອນ",
        "ປີ",
        "ຈຳນວນເງິນ",
        "ວັນທີຈ່າຍ",
        "ສະຖານະ",
        "ຜູ້ບັນທຶກ",
    ]

    if normalized_format == "csv":
        output, writer = create_csv_writer()
        writer.writerow(headers)

        for payment in payments:
            writer.writerow(
                [
                    payment["salary_payment_id"],
                    payment["teacher_name"],
                    payment["month_name"] or "-",
                    payment["year"] or "-",
                    payment["total_amount"],
                    format_report_date(payment["payment_date"]),
                    payment["status"] or "-",
                    payment["user_name"] or "-",
                ]
            )

        filename = f"salary_payment_report_{current_timestamp()}.csv"
        return finalize_csv_export(
            output,
            filename=filename,
            total_records=len(payments),
        )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "SalaryReport"
    theme = create_excel_theme(
        title_color="7C3AED",
        header_color="EDE9FE",
        summary_color="F5F3FF",
    )

    apply_excel_title(
        sheet,
        title="ລາຍງານເບີກຈ່າຍເງິນສອນ",
        from_column=1,
        to_column=len(headers),
        theme=theme,
    )
    write_excel_key_value_rows(
        sheet,
        rows=[
            ("ວັນທີສ້າງ", format_report_datetime()),
            ("ເດືອນ", report_data["filters"].get("month_name") or "ທັງໝົດ"),
            ("ອາຈານ", report_data["filters"].get("teacher_name") or "ທັງໝົດ"),
            ("ສະຖານະ", report_data["filters"].get("status") or "ທັງໝົດ"),
            ("ຈຳນວນລາຍການ", report_data["total_count"]),
            ("ຈ່າຍແລ້ວ", summary["paid_count"]),
            ("ຄ້າງຈ່າຍ", summary["pending_count"]),
            (
                "ຈຳນວນເງິນລວມ",
                format_report_currency(summary["total_amount"]),
            ),
        ],
        start_row=3,
        theme=theme,
    )

    header_row = 12
    write_excel_table_headers(sheet, headers=headers, row_index=header_row, theme=theme)
    write_excel_table_rows(
        sheet,
        rows=[
            [
                payment["salary_payment_id"],
                payment["teacher_name"],
                payment["month_name"] or "-",
                payment["year"] or "-",
                payment["total_amount"],
                format_report_date(payment["payment_date"]),
                payment["status"] or "-",
                payment["user_name"] or "-",
            ]
            for payment in payments
        ],
        start_row=header_row + 1,
        theme=theme,
    )

    sheet.freeze_panes = f"A{header_row + 1}"
    sheet.auto_filter.ref = (
        f"A{header_row}:H{max(header_row, header_row + len(payments))}"
    )
    set_excel_column_widths(
        sheet,
        {
            1: 18,
            2: 26,
            3: 14,
            4: 10,
            5: 18,
            6: 16,
            7: 14,
            8: 18,
        },
    )

    filename = f"salary_payment_report_{current_timestamp()}.xlsx"
    return finalize_workbook_export(
        workbook,
        filename=filename,
        total_records=len(payments),
    )