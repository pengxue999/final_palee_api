from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.configs.response import success_response
from app.services import reports as svc
from app.services import receipt_pdf as receipt_pdf_svc
from app.services import evaluation as evaluation_svc
from typing import Optional

router = APIRouter(prefix="/reports", tags=["ລາຍງານ"])


@router.get("/assessment-results")
def get_assessment_results_report(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    semester: str = Query(..., description="ກາງພາກ ຫຼື ທ້າຍພາກ"),
    evaluation_type: Optional[str] = Query(None, description="Midterm ຫຼື Final (optional)"),
    subject_id: Optional[str] = Query(None, description="ລະຫັດວິຊາ (optional)"),
    level_id: Optional[str] = Query(None, description="ລະຫັດລະດັບ (optional)"),
    ranking: Optional[int] = Query(None, description="ອັນດັບ 1, 2, 3 (optional)"),
    db: Session = Depends(get_db),
):
    result = evaluation_svc.get_assessment_report(
        db,
        academic_id=academic_id,
        semester=semester,
        evaluation_type=evaluation_type,
        subject_id=subject_id,
        level_id=level_id,
        ranking=ranking,
    )
    return success_response(result, "ດຶງລາຍງານຜົນການຮຽນສຳເລັດ")


@router.get("/assessment-results/export")
def export_assessment_results_report(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    semester: str = Query(..., description="ກາງພາກ ຫຼື ທ້າຍພາກ"),
    subject_id: Optional[str] = Query(None, description="ລະຫັດວິຊາ (optional)"),
    level_id: Optional[str] = Query(None, description="ລະຫັດລະດັບ (optional)"),
    ranking: Optional[int] = Query(None, description="ອັນດັບ 1, 2, 3 (optional)"),
    format: str = Query("excel", description="ຮູບແບບໄຟລ໌: csv ຫຼື excel"),
    db: Session = Depends(get_db),
):
    result = svc.export_assessment_report(
        db,
        academic_id=academic_id,
        semester=semester,
        subject_id=subject_id,
        level_id=level_id,
        ranking=ranking,
        format=format,
    )
    return success_response(result, "Export ລາຍງານຜົນການຮຽນສຳເລັດ")


@router.get("/assessment-results/report-pdf")
def assessment_results_report_pdf(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    semester: str = Query(..., description="ກາງພາກ ຫຼື ທ້າຍພາກ"),
    subject_id: Optional[str] = Query(None, description="ລະຫັດວິຊາ (optional)"),
    level_id: Optional[str] = Query(None, description="ລະຫັດລະດັບ (optional)"),
    ranking: Optional[int] = Query(None, description="ອັນດັບ 1, 2, 3 (optional)"),
    db: Session = Depends(get_db),
):
    report_data = svc.get_assessment_report_data(
        db,
        academic_id=academic_id,
        semester=semester,
        subject_id=subject_id,
        level_id=level_id,
        ranking=ranking,
    )
    pdf_bytes = receipt_pdf_svc.build_assessment_report_pdf(report_data)
    filename = "assessment_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/students/{student_id}/transcript")
def get_student_transcript(
    student_id: str,
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    semester: Optional[str] = Query(None, description="ກາງພາກ ຫຼື ທ້າຍພາກ (optional)"),
    evaluation_type: Optional[str] = Query(None, description="Midterm ຫຼື Final (optional)"),
    db: Session = Depends(get_db),
):
    result = evaluation_svc.get_student_transcript(
        db,
        student_id=student_id,
        academic_id=academic_id,
        semester=semester,
        evaluation_type=evaluation_type,
    )
    return success_response(result, "ດຶງ transcript ນັກຮຽນສຳເລັດ")


@router.get("/students")
def get_student_report(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    province_id: Optional[int] = Query(None, description="ລະຫັດແຂວງ (optional)"),
    district_id: Optional[int] = Query(None, description="ລະຫັດເມືອງ (optional)"),
    scholarship: Optional[str] = Query(None, description="ສະຖານະທຶນ: 'ໄດ້ຮັບທຶນ' ຫຼື 'ບໍ່ໄດ້ຮັບທຶນ' (optional)"),
    gender: Optional[str] = Query(None, description="ເພດ: 'ຊາຍ' ຫຼື 'ຍິງ' (optional)"),
    db: Session = Depends(get_db)
):
    """
    ລາຍງານຂໍ້ມູນນັກຮຽນຕາມເງື່ອນໄຂຕ່າງໆ

    - academic_id: ກັ່ນຕອງຕາມສົກຮຽນ
    - province_id: ກັ່ນຕອງຕາມແຂວງ
    - district_id: ກັ່ນຕອງຕາມເມືອງ
    - scholarship: ກັ່ນຕອງຕາມສະຖານະທຶນ
    - gender: ກັ່ນຕອງຕາມເພດ
    """
    result = svc.get_student_report(
        db,
        academic_id=academic_id,
        province_id=province_id,
        district_id=district_id,
        scholarship=scholarship,
        gender=gender
    )
    return success_response(result, "ດຶງຂໍ້ມູນລາຍງານນັກຮຽນສຳເລັດ")


@router.get("/students/export")
def export_student_report(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    province_id: Optional[int] = Query(None, description="ລະຫັດແຂວງ (optional)"),
    district_id: Optional[int] = Query(None, description="ລະຫັດເມືອງ (optional)"),
    scholarship: Optional[str] = Query(None, description="ສະຖານະທຶນ (optional)"),
    gender: Optional[str] = Query(None, description="ເພດ (optional)"),
    format: str = Query("excel", description="ຮູບແບບໄຟລ໌: csv ຫຼື excel"),
    db: Session = Depends(get_db)
):
    """
    Export ຂໍ້ມູນນັກຮຽນເປັນ CSV ຫຼື Excel
    """
    result = svc.export_student_report(
        db,
        academic_id=academic_id,
        province_id=province_id,
        district_id=district_id,
        scholarship=scholarship,
        gender=gender,
        format=format
    )
    return success_response(result, "Export ຂໍ້ມູນສຳເລັດ")


@router.get("/students/report-pdf")
def student_report_pdf(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    province_id: Optional[int] = Query(None, description="ລະຫັດແຂວງ (optional)"),
    district_id: Optional[int] = Query(None, description="ລະຫັດເມືອງ (optional)"),
    scholarship: Optional[str] = Query(None, description="ສະຖານະທຶນ (optional)"),
    gender: Optional[str] = Query(None, description="ເພດ (optional)"),
    db: Session = Depends(get_db)
):
    report_data = svc.get_student_report(
        db,
        academic_id=academic_id,
        province_id=province_id,
        district_id=district_id,
        scholarship=scholarship,
        gender=gender,
    )
    pdf_bytes = receipt_pdf_svc.build_student_report_pdf(report_data)
    filename = "student_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/students/summary")
def get_student_summary(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    db: Session = Depends(get_db)
):
    """
    ສະຫຼຸບຂໍ້ມູນນັກຮຽນຕາມຫົວຂໍ້ຕ່າງໆ

    - ຈຳນວນນັກຮຽນທັງໝົດ
    - ແຍກຕາມເພດ
    - ແຍກຕາມທຶນ
    - ແຍກຕາມແຂວງ/ເມືອງ
    """
    result = svc.get_student_summary(db, academic_id=academic_id)
    return success_response(result, "ດຶງຂໍ້ມູນສະຫຼຸບນັກຮຽນສຳເລັດ")


@router.get("/teacher-attendance")
def get_teacher_attendance_report(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    month: Optional[str] = Query(None, description="ເດືອນ (YYYY-MM) (optional)"),
    status: Optional[str] = Query(None, description="ສະຖານະ: 'ຂຶ້ນສອນ' ຫຼື 'ຂາດສອນ' (optional)"),
    teacher_id: Optional[str] = Query(None, description="ລະຫັດອາຈານ (optional)"),
    db: Session = Depends(get_db)
):
    """
    ລາຍງານຂໍ້ມູນການເຂົ້າສອນຂອງອາຈານ

    - academic_id: ກັ່ນຕອງຕາມສົກຮຽນ
    - month: ກັ່ນຕອງຕາມເດືອນ (YYYY-MM)
    - status: ກັ່ນຕອງຕາມສະຖານະ (ຂຶ້ນສອນ/ຂາດສອນ)
    - teacher_id: ກັ່ນຕອງຕາມອາຈານ
    """
    result = svc.get_teacher_attendance_report(
        db,
        academic_id=academic_id,
        month=month,
        status=status,
        teacher_id=teacher_id
    )
    return success_response(result, "ດຶງຂໍ້ມູນລາຍງານການເຂົ້າສອນສຳເລັດ")


@router.get("/teacher-attendance/export")
def export_teacher_attendance_report(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    month: Optional[str] = Query(None, description="ເດືອນ (YYYY-MM) (optional)"),
    status: Optional[str] = Query(None, description="ສະຖານະ (optional)"),
    teacher_id: Optional[str] = Query(None, description="ລະຫັດອາຈານ (optional)"),
    format: str = Query("excel", description="ຮູບແບບໄຟລ໌: csv ຫຼື excel"),
    db: Session = Depends(get_db)
):
    """
    Export ຂໍ້ມູນການເຂົ້າສອນຂອງອາຈານເປັນ CSV ຫຼື Excel
    """
    result = svc.export_teacher_attendance_report(
        db,
        academic_id=academic_id,
        month=month,
        status=status,
        teacher_id=teacher_id,
        format=format
    )
    return success_response(result, "Export ຂໍ້ມູນສຳເລັດ")


@router.get("/teacher-attendance/report-pdf")
def teacher_attendance_report_pdf(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    month: Optional[str] = Query(None, description="ເດືອນ (YYYY-MM) (optional)"),
    status: Optional[str] = Query(None, description="ສະຖານະ (optional)"),
    teacher_id: Optional[str] = Query(None, description="ລະຫັດອາຈານ (optional)"),
    db: Session = Depends(get_db)
):
    report_data = svc.get_teacher_attendance_report(
        db,
        academic_id=academic_id,
        month=month,
        status=status,
        teacher_id=teacher_id,
    )
    pdf_bytes = receipt_pdf_svc.build_teacher_attendance_report_pdf(report_data)
    filename = "teacher_attendance_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/salary-payments")
def get_salary_payment_report(
    month: Optional[int] = Query(None, description="ເດືອນ 1-12 (optional)"),
    teacher_id: Optional[str] = Query(None, description="ລະຫັດອາຈານ (optional)"),
    status: Optional[str] = Query(None, description="ສະຖານະການຈ່າຍ (optional)"),
    db: Session = Depends(get_db)
):
    result = svc.get_salary_payment_report(
        db,
        month=month,
        teacher_id=teacher_id,
        status=status,
    )
    return success_response(result, "ດຶງຂໍ້ມູນລາຍງານເບີກຈ່າຍເງິນສອນສຳເລັດ")


@router.get("/salary-payments/export")
def export_salary_payment_report(
    month: Optional[int] = Query(None, description="ເດືອນ 1-12 (optional)"),
    teacher_id: Optional[str] = Query(None, description="ລະຫັດອາຈານ (optional)"),
    status: Optional[str] = Query(None, description="ສະຖານະການຈ່າຍ (optional)"),
    format: str = Query("excel", description="ຮູບແບບໄຟລ໌: csv ຫຼື excel"),
    db: Session = Depends(get_db)
):
    result = svc.export_salary_payment_report(
        db,
        month=month,
        teacher_id=teacher_id,
        status=status,
        format=format,
    )
    return success_response(result, "Export ລາຍງານເບີກຈ່າຍເງິນສອນສຳເລັດ")


@router.get("/salary-payments/report-pdf")
def salary_payment_report_pdf(
    month: Optional[int] = Query(None, description="ເດືອນ 1-12 (optional)"),
    teacher_id: Optional[str] = Query(None, description="ລະຫັດອາຈານ (optional)"),
    status: Optional[str] = Query(None, description="ສະຖານະການຈ່າຍ (optional)"),
    db: Session = Depends(get_db)
):
    report_data = svc.get_salary_payment_report(
        db,
        month=month,
        teacher_id=teacher_id,
        status=status,
    )
    pdf_bytes = receipt_pdf_svc.build_salary_payment_report_pdf(report_data)
    filename = "salary_payment_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/finance")
def get_finance_report(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    year: Optional[int] = Query(None, description="ປີ (YYYY) (optional)"),
    db: Session = Depends(get_db)
):
    """
    ລາຍງານຂໍ້ມູນການເງິນ (ລາຍຮັບ, ລາຍຈ່າຍ, ແລະ ຍອດເຫຼືອ)

    - academic_id: ກັ່ນຕອງຕາມສົກຮຽນ
    - year: ກັ່ນຕອງຕາມປີ (ສຳລັບ graph ລາຍຮັບ-ລາຍຈ່າຍ)
    """
    result = svc.get_finance_report(
        db,
        academic_id=academic_id,
        year=year
    )
    return success_response(result, "ດຶງຂໍ້ມູນລາຍງານການເງິນສຳເລັດ")


@router.get("/finance/export")
def export_finance_report(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    year: Optional[int] = Query(None, description="ປີ (YYYY) (optional)"),
    tab: str = Query("overview", description="tab: overview, income, expense"),
    format: str = Query("excel", description="ຮູບແບບໄຟລ໌: csv ຫຼື excel"),
    db: Session = Depends(get_db)
):
    """
    Export ຂໍ້ມູນລາຍງານການເງິນເປັນ CSV ຫຼື Excel
    """
    result = svc.export_finance_report(
        db,
        academic_id=academic_id,
        year=year,
        tab=tab,
        format=format
    )
    return success_response(result, "Export ຂໍ້ມູນສຳເລັດ")


@router.get("/finance/report-pdf")
def finance_report_pdf(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    year: Optional[int] = Query(None, description="ປີ (YYYY) (optional)"),
    tab: str = Query("overview", description="tab: overview, income, expense"),
    db: Session = Depends(get_db)
):
    report_data = svc.get_finance_report(
        db,
        academic_id=academic_id,
        year=year,
    )
    pdf_bytes = receipt_pdf_svc.build_finance_report_pdf(report_data, tab=tab)
    filename = f"finance_report_{tab}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/popular-subjects")
def get_popular_subjects_report(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    db: Session = Depends(get_db)
):
    """
    ລາຍງານວິຊາທີ່ນັກຮຽນມັກຮຽນຫຼາຍທີ່ສຸດ (Popular Subjects Report)

    - academic_id: ກັ່ນຕອງຕາມສົກຮຽນ
    - ສະແດງສະຖິຕິວິຊາທີ່ນັກຮຽນລົງທະບຽນຫຼາຍທີ່ສຸດ
    - ລວມທັງ: ຊື່ວິຊາ, ໝວດວິຊາ, ລະດັບ, ຈຳນວນນັກຮຽນ, ເປີເຊັນ
    """
    result = svc.get_popular_subjects_report(
        db,
        academic_id=academic_id
    )
    return success_response(result, "ດຶງຂໍ້ມູນວິຊາຍອດນິຍົມສຳເລັດ")


@router.get("/popular-subjects/export")
def export_popular_subjects_report(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    format: str = Query("excel", description="ຮູບແບບໄຟລ໌: csv ຫຼື excel"),
    db: Session = Depends(get_db)
):
    result = svc.export_popular_subjects_report(
        db,
        academic_id=academic_id,
        format=format,
    )
    return success_response(result, "Export ລາຍງານວິຊາຍອດນິຍົມສຳເລັດ")


@router.get("/popular-subjects/report-pdf")
def popular_subjects_report_pdf(
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    db: Session = Depends(get_db)
):
    report_data = svc.get_popular_subjects_report(
        db,
        academic_id=academic_id,
    )
    pdf_bytes = receipt_pdf_svc.build_popular_subjects_report_pdf(report_data)
    filename = "popular_subjects_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/popular-subjects/level-detail/export")
def export_popular_subject_level_detail_report(
    subject_name: str = Query(..., description="ຊື່ວິຊາ"),
    level_name: str = Query(..., description="ລະດັບ/ຊັ້ນ"),
    subject_category: Optional[str] = Query(None, description="ໝວດວິຊາ (optional)"),
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    format: str = Query("excel", description="ຮູບແບບໄຟລ໌: csv ຫຼື excel"),
    db: Session = Depends(get_db)
):
    result = svc.export_popular_subject_level_detail_report(
        db,
        subject_name=subject_name,
        level_name=level_name,
        subject_category=subject_category,
        academic_id=academic_id,
        format=format,
    )
    return success_response(result, "Export ລາຍຊື່ນັກຮຽນຕາມວິຊາ/ລະດັບສຳເລັດ")


@router.get("/popular-subjects/level-detail/report-pdf")
def popular_subject_level_detail_report_pdf(
    subject_name: str = Query(..., description="ຊື່ວິຊາ"),
    level_name: str = Query(..., description="ລະດັບ/ຊັ້ນ"),
    subject_category: Optional[str] = Query(None, description="ໝວດວິຊາ (optional)"),
    academic_id: Optional[str] = Query(None, description="ລະຫັດສົກຮຽນ (optional)"),
    db: Session = Depends(get_db)
):
    report_data = svc.get_popular_subject_level_detail_report(
        db,
        subject_name=subject_name,
        level_name=level_name,
        subject_category=subject_category,
        academic_id=academic_id,
    )
    pdf_bytes = receipt_pdf_svc.build_popular_subject_level_report_pdf(report_data)
    filename = "popular_subject_level_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/donations/export")
def export_donation_report(
    donor_id: Optional[str] = Query(None, description="ລະຫັດຜູ້ບໍລິຈາກ (optional)"),
    donation_category: Optional[str] = Query(None, description="ປະເພດການບໍລິຈາກ (optional)"),
    year: Optional[int] = Query(None, description="ປີ (YYYY) (optional)"),
    format: str = Query("excel", description="ຮູບແບບໄຟລ໌: csv ຫຼື excel"),
    db: Session = Depends(get_db)
):
    result = svc.export_donation_report(
        db,
        donor_id=donor_id,
        donation_category=donation_category,
        year=year,
        format=format,
    )
    return success_response(result, "Export ລາຍງານການບໍລິຈາກສຳເລັດ")


@router.get("/donations/report-pdf")
def donation_report_pdf(
    donor_id: Optional[str] = Query(None, description="ລະຫັດຜູ້ບໍລິຈາກ (optional)"),
    donation_category: Optional[str] = Query(None, description="ປະເພດການບໍລິຈາກ (optional)"),
    year: Optional[int] = Query(None, description="ປີ (YYYY) (optional)"),
    db: Session = Depends(get_db)
):
    report_data = svc.get_donation_report(
        db,
        donor_id=donor_id,
        donation_category=donation_category,
        year=year,
    )
    pdf_bytes = receipt_pdf_svc.build_donation_report_pdf(report_data)
    filename = "donation_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
