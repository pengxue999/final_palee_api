from typing import Any, Dict, Optional

from openpyxl import Workbook

from sqlalchemy.orm import Session, joinedload

from app.enums.scholarship import ScholarshipEnum
from app.models.district import District
from app.models.fee import Fee
from app.models.province import Province
from app.models.registration import Registration
from app.models.registration_detail import RegistrationDetail
from app.models.student import Student
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
    resolve_district_name,
    resolve_province_name,
)


_VALID_GENDERS = ["MALE", "FEMALE"]
_VALID_SCHOLARSHIPS = [
    ScholarshipEnum.SCHOLARSHIP,
    ScholarshipEnum.NO_SCHOLARSHIP,
]


def get_student_report(
    db: Session,
    academic_id: Optional[str] = None,
    province_id: Optional[int] = None,
    district_id: Optional[int] = None,
    scholarship: Optional[str] = None,
    gender: Optional[str] = None,
) -> Dict[str, Any]:
    query = db.query(Student).options(
        joinedload(Student.district).joinedload(District.province),
    )

    if gender:
        query = query.filter(Student.gender == gender)

    if district_id:
        query = query.filter(Student.district_id == district_id)
    elif province_id:
        query = query.join(District).filter(District.province_id == province_id)

    if academic_id or scholarship:
        query = (
            query.join(Registration, Student.student_id == Registration.student_id)
            .join(
                RegistrationDetail,
                Registration.registration_id == RegistrationDetail.registration_id,
            )
            .join(Fee, RegistrationDetail.fee_id == Fee.fee_id)
        )

        if academic_id:
            query = query.filter(Fee.academic_id == academic_id)

        if scholarship:
            scholarship_enum = ScholarshipEnum(scholarship)
            query = query.filter(RegistrationDetail.scholarship == scholarship_enum)

        query = query.distinct()

    students = query.all()

    student_list = []
    for student in students:
        student_scholarship = None
        if academic_id:
            reg_detail = (
                db.query(RegistrationDetail)
                .join(
                    Registration,
                    RegistrationDetail.registration_id == Registration.registration_id,
                )
                .join(Fee, RegistrationDetail.fee_id == Fee.fee_id)
                .filter(
                    Registration.student_id == student.student_id,
                    Fee.academic_id == academic_id,
                )
                .first()
            )
            if reg_detail:
                student_scholarship = reg_detail.scholarship.value

        student_list.append(
            {
                "student_id": student.student_id,
                "student_name": student.student_name,
                "student_lastname": student.student_lastname,
                "full_name": f"{student.student_name} {student.student_lastname}",
                "gender": student.gender,
                "student_contact": student.student_contact,
                "parents_contact": student.parents_contact,
                "school": student.school,
                "district_name": student.district.district_name if student.district else None,
                "province_name": (
                    student.district.province.province_name
                    if student.district and student.district.province
                    else None
                ),
                "scholarship_status": student_scholarship,
            }
        )

    return {
        "filters": {
            "academic_id": academic_id,
            "academic_year_name": resolve_academic_year_name(db, academic_id),
            "province_id": province_id,
            "province_name": resolve_province_name(db, province_id),
            "district_id": district_id,
            "district_name": resolve_district_name(db, district_id),
            "scholarship": scholarship,
            "gender": gender,
        },
        "total_count": len(student_list),
        "students": student_list,
    }


def export_student_report(
    db: Session,
    academic_id: Optional[str] = None,
    province_id: Optional[int] = None,
    district_id: Optional[int] = None,
    scholarship: Optional[str] = None,
    gender: Optional[str] = None,
    format: str = "excel",
) -> Dict[str, Any]:
    report_data = get_student_report(
        db,
        academic_id=academic_id,
        province_id=province_id,
        district_id=district_id,
        scholarship=scholarship,
        gender=gender,
    )

    students = report_data["students"]
    normalized_format = format.lower()

    headers = [
        "ລະຫັດນັກຮຽນ",
        "ຊື່",
        "ນາມສະກຸນ",
        "ເພດ",
        "ເບີຕິດຕໍ່",
        "ເບີຜູ້ປົກຄອງ",
        "ໂຮງຮຽນ",
        "ແຂວງ",
        "ເມືອງ",
        "ສະຖານະທຶນ",
    ]

    if normalized_format == "csv":
        output, writer = create_csv_writer()
        writer.writerow(headers)

        for student in students:
            writer.writerow(
                [
                    student["student_id"],
                    student["student_name"],
                    student["student_lastname"],
                    student["gender"],
                    student["student_contact"],
                    student["parents_contact"],
                    student["school"],
                    student["province_name"] or "",
                    student["district_name"] or "",
                    student["scholarship_status"] or "-",
                ]
            )

        filters_desc = []
        if academic_id:
            filters_desc.append(f"academic_{academic_id}")
        if province_id:
            filters_desc.append(f"province_{province_id}")
        if scholarship:
            filters_desc.append(f"scholarship_{scholarship}")

        filter_str = "_".join(filters_desc) if filters_desc else "ທັງໝົດ"
        filename = f"ລາຍງານນັກຮຽນ_{filter_str}.csv"
        return finalize_csv_export(output, filename=filename, total_records=len(students))

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Students"
    theme = create_excel_theme()

    apply_excel_title(
        sheet,
        title="ລາຍງານນັກຮຽນ",
        from_column=1,
        to_column=len(headers),
        theme=theme,
    )

    write_excel_key_value_rows(
        sheet,
        rows=[
            ("ວັນທີສ້າງ", format_report_datetime()),
            ("ສົກຮຽນ", report_data["filters"].get("academic_year_name") or "ທັງໝົດ"),
            ("ແຂວງ", report_data["filters"].get("province_name") or "ທັງໝົດ"),
            ("ເມືອງ", report_data["filters"].get("district_name") or "ທັງໝົດ"),
            ("ເພດ", report_data["filters"].get("gender") or "ທັງໝົດ"),
            ("ສະຖານະທຶນ", report_data["filters"].get("scholarship") or "ທັງໝົດ"),
            ("ຈຳນວນນັກຮຽນ", report_data["total_count"]),
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
                student["student_id"],
                student["student_name"],
                student["student_lastname"],
                student["gender"],
                student["student_contact"],
                student["parents_contact"],
                student["school"],
                student["province_name"] or "-",
                student["district_name"] or "-",
                student["scholarship_status"] or "-",
            ]
            for student in students
        ],
        start_row=header_row + 1,
        theme=theme,
    )

    sheet.freeze_panes = f"A{header_row + 1}"
    sheet.auto_filter.ref = f"A{header_row}:K{max(header_row, header_row + len(students))}"
    set_excel_column_widths(
        sheet,
        {
            1: 16,
            2: 18,
            3: 18,
            4: 10,
            5: 18,
            6: 20,
            7: 24,
            8: 16,
            9: 16,
            10: 18,
        },
    )

    filename = f"student_report_{current_timestamp()}.xlsx"
    return finalize_workbook_export(workbook, filename=filename, total_records=len(students))


def get_student_summary(
    db: Session,
    academic_id: Optional[str] = None,
) -> Dict[str, Any]:
    base_query = db.query(Student)

    if academic_id:
        base_query = (
            base_query.join(Registration, Student.student_id == Registration.student_id)
            .join(
                RegistrationDetail,
                Registration.registration_id == RegistrationDetail.registration_id,
            )
            .join(Fee, RegistrationDetail.fee_id == Fee.fee_id)
            .filter(Fee.academic_id == academic_id)
            .distinct()
        )

    total_students = base_query.count()

    gender_stats = {}
    for gender_name in _VALID_GENDERS:
        gender_stats[gender_name] = base_query.filter(Student.gender == gender_name).count()

    scholarship_stats = {}
    if academic_id:
        for scholarship_status in _VALID_SCHOLARSHIPS:
            count = (
                db.query(Student)
                .join(Registration, Student.student_id == Registration.student_id)
                .join(
                    RegistrationDetail,
                    Registration.registration_id == RegistrationDetail.registration_id,
                )
                .join(Fee, RegistrationDetail.fee_id == Fee.fee_id)
                .filter(
                    Fee.academic_id == academic_id,
                    RegistrationDetail.scholarship == scholarship_status,
                )
                .distinct()
                .count()
            )
            scholarship_stats[scholarship_status.value] = count
    else:
        scholarship_stats = {
            ScholarshipEnum.SCHOLARSHIP.value: 0,
            ScholarshipEnum.NO_SCHOLARSHIP.value: 0,
        }

    province_stats = {}
    for province in db.query(Province).all():
        count = base_query.join(District).filter(District.province_id == province.province_id).count()
        if count > 0:
            province_stats[province.province_name] = count

    district_stats = {}
    for district in db.query(District).all():
        count = base_query.filter(Student.district_id == district.district_id).count()
        if count > 0:
            district_stats[district.district_name] = count

    district_stats = dict(
        sorted(district_stats.items(), key=lambda item: item[1], reverse=True)[:10]
    )

    return {
        "total_students": total_students,
        "by_gender": gender_stats,
        "by_scholarship": scholarship_stats,
        "by_province": province_stats,
        "by_district": district_stats,
    }