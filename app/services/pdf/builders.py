from app.schemas.registration import RegistrationReceiptRequest
from app.schemas.salary_payment import SalaryPaymentReceiptRequest
from app.schemas.tuition_payment import (
    TuitionPaymentHistoryReportRequest,
    TuitionPaymentReceiptRequest,
)
from app.models.donation import Donation
from app.services.pdf.assets import render_template
from app.services.pdf.contexts.donation_certificate import (
    build_donation_certificate_context,
)
from app.services.pdf.contexts.donation_report import build_donation_report_context
from app.services.pdf.contexts.assessment_report import build_assessment_report_context
from app.services.pdf.contexts.finance_report import build_finance_report_context
from app.services.pdf.contexts.popular_subject_level_report import (
    build_popular_subject_level_report_context,
)
from app.services.pdf.contexts.popular_subjects_report import (
    build_popular_subjects_report_context,
)
from app.services.pdf.contexts.registration import build_registration_context
from app.services.pdf.contexts.salary_payment import build_salary_payment_context
from app.services.pdf.contexts.salary_payment_report import (
    build_salary_payment_report_context,
)
from app.services.pdf.contexts.student_report import build_student_report_context
from app.services.pdf.contexts.teacher_attendance_report import (
    build_teacher_attendance_report_context,
)
from app.services.pdf.contexts.tuition_payment_history_report import (
    build_tuition_payment_history_report_context,
)
from app.services.pdf.contexts.tuition_payment import build_tuition_payment_context
from app.services.pdf.engine import render_pdf_document


def build_registration_receipt_pdf(data: RegistrationReceiptRequest) -> bytes:
    html = render_template("registration_receipt.html", build_registration_context(data))
    return render_pdf_document(
        html,
        viewport_width=874,
        viewport_height=1240,
    )


def build_donation_certificate_pdf(donation: Donation) -> bytes:
    html = render_template(
        "donation_certificate.html",
        build_donation_certificate_context(donation),
    )
    return render_pdf_document(
        html,
        viewport_width=1754,
        viewport_height=1240,
    )


def build_tuition_payment_receipt_pdf(data: TuitionPaymentReceiptRequest) -> bytes:
    html = render_template(
        "tuition_payment_receipt.html",
        build_tuition_payment_context(data),
    )
    return render_pdf_document(
        html,
        viewport_width=874,
        viewport_height=1240,
    )


def build_tuition_payment_history_report_pdf(
    data: TuitionPaymentHistoryReportRequest,
) -> bytes:
    html = render_template(
        "tuition_payment_history_report.html",
        build_tuition_payment_history_report_context(data),
    )
    footer_template = """
        <div style="width:100%;padding:0 14mm 2mm 14mm;font-size:9px;
          color:#6b7280;font-family:'Noto Sans Lao','Segoe UI',sans-serif;
          display:flex;justify-content:space-between;align-items:center;
          border-top:1px solid #e5e7eb;box-sizing:border-box;">
          <span>ສະຫຼຸບປະຫວັດການຈ່າຍຄ່າຮຽນ</span>
          <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>
    """
    return render_pdf_document(
        html,
        viewport_width=1754,
        viewport_height=1240,
        margin_top="0mm",
        margin_right="0mm",
        margin_bottom="14mm",
        margin_left="0mm",
        footer_template=footer_template,
    )


def build_salary_payment_receipt_pdf(data: SalaryPaymentReceiptRequest) -> bytes:
    html = render_template(
        "salary_payment_receipt.html",
        build_salary_payment_context(data),
    )
    return render_pdf_document(
        html,
        viewport_width=874,
        viewport_height=1240,
    )


def build_salary_payment_report_pdf(report_data: dict[str, object]) -> bytes:
    html = render_template(
        "salary_payment_report.html",
        build_salary_payment_report_context(report_data),
    )
    footer_template = """
                <div style="width:100%;padding:0 20mm 2mm 20mm;font-size:9px;
                    box-sizing:border-box;
          color:#6b7280;font-family:'Noto Sans Lao','Segoe UI',sans-serif;
          display:flex;justify-content:space-between;align-items:center;
          border-top:1px solid #e5e7eb;">
          <span>ລາຍງານເບີກຈ່າຍເງິນສອນ</span>
          <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>
    """
    return render_pdf_document(
        html,
        viewport_width=1122,
        viewport_height=794,
        margin_top="4mm",
        margin_right="0mm",
        margin_bottom="14mm",
        margin_left="0mm",
        footer_template=footer_template,
    )


def build_student_report_pdf(report_data: dict[str, object]) -> bytes:
    html = render_template("student_report.html", build_student_report_context(report_data))
    return render_pdf_document(
        html,
        viewport_width=1754,
        viewport_height=1240,
    )


def build_assessment_report_pdf(report_data: dict[str, object]) -> bytes:
    html = render_template(
        "assessment_report.html",
        build_assessment_report_context(report_data),
    )
    footer_template = """
                <div style="width:100%;padding:0 16mm 2mm 16mm;font-size:9px;
                    box-sizing:border-box;
          color:#6b7280;font-family:'Noto Sans Lao','Segoe UI',sans-serif;
          display:flex;justify-content:space-between;align-items:center;
          border-top:1px solid #e5e7eb;">
          <span>ລາຍງານຜົນການຮຽນ</span>
          <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>
    """
    return render_pdf_document(
        html,
        viewport_width=1754,
        viewport_height=1240,
        margin_top="4mm",
        margin_right="0mm",
        margin_bottom="14mm",
        margin_left="0mm",
        footer_template=footer_template,
    )


def build_donation_report_pdf(report_data: dict[str, object]) -> bytes:
    html = render_template(
        "donation_report.html",
        build_donation_report_context(report_data),
    )
    footer_template = """
                <div style="width:100%;padding:0 16mm 2mm 16mm;font-size:9px;
                    box-sizing:border-box;
          color:#6b7280;font-family:'Noto Sans Lao','Segoe UI',sans-serif;
          display:flex;justify-content:space-between;align-items:center;
          border-top:1px solid #e5e7eb;">
          <span>ລາຍງານການບໍລິຈາກ</span>
          <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>
    """
    return render_pdf_document(
        html,
        viewport_width=1754,
        viewport_height=1240,
        margin_top="4mm",
        margin_right="0mm",
        margin_bottom="14mm",
        margin_left="0mm",
        footer_template=footer_template,
    )


def build_teacher_attendance_report_pdf(report_data: dict[str, object]) -> bytes:
    html = render_template(
        "teacher_attendance_report.html",
        build_teacher_attendance_report_context(report_data),
    )
    footer_template = """
                <div style="width:100%;padding:0 20mm 2mm 20mm;font-size:9px;
                    box-sizing:border-box;
          color:#6b7280;font-family:'Noto Sans Lao','Segoe UI',sans-serif;
          display:flex;justify-content:space-between;align-items:center;
          border-top:1px solid #e5e7eb;">
          <span>ລາຍງານການຂື້ນສອນຂອງອາຈານ</span>
          <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>
    """
    return render_pdf_document(
        html,
        viewport_width=1122,
        viewport_height=794,
        margin_top="4mm",
        margin_right="0mm",
        margin_bottom="14mm",
        margin_left="0mm",
        footer_template=footer_template,
    )


def build_popular_subjects_report_pdf(report_data: dict[str, object]) -> bytes:
    html = render_template(
        "popular_subjects_report.html",
        build_popular_subjects_report_context(report_data),
    )
    footer_template = """
                <div style="width:100%;padding:0 16mm 2mm 16mm;font-size:9px;
                    box-sizing:border-box;
          color:#6b7280;font-family:'Noto Sans Lao','Segoe UI',sans-serif;
          display:flex;justify-content:space-between;align-items:center;
          border-top:1px solid #e5e7eb;">
          <span>ລາຍງານວິຊາຍອດນິຍົມ</span>
          <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>
    """
    return render_pdf_document(
        html,
        viewport_width=1754,
        viewport_height=1240,
        margin_top="4mm",
        margin_right="0mm",
        margin_bottom="14mm",
        margin_left="0mm",
        footer_template=footer_template,
    )


def build_popular_subject_level_report_pdf(report_data: dict[str, object]) -> bytes:
    html = render_template(
        "popular_subject_level_report.html",
        build_popular_subject_level_report_context(report_data),
    )
    footer_template = """
                <div style="width:100%;padding:0 16mm 2mm 16mm;font-size:9px;
                    box-sizing:border-box;
          color:#6b7280;font-family:'Noto Sans Lao','Segoe UI',sans-serif;
          display:flex;justify-content:space-between;align-items:center;
          border-top:1px solid #e5e7eb;">
          <span>ລາຍຊື່ນັກຮຽນຕາມວິຊາ/ລະດັບ</span>
          <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>
    """
    return render_pdf_document(
        html,
        viewport_width=874,
        viewport_height=1240,
        margin_top="4mm",
        margin_right="0mm",
        margin_bottom="14mm",
        margin_left="0mm",
        footer_template=footer_template,
    )


def build_finance_report_pdf(
    report_data: dict[str, object],
    *,
    tab: str = "overview",
) -> bytes:
    html = render_template(
        "finance_report.html",
        build_finance_report_context(report_data, tab=tab),
    )
    footer_template = """
                <div style="width:100%;padding:0 20mm 2mm 20mm;font-size:9px;
                    box-sizing:border-box;
          color:#6b7280;font-family:'Noto Sans Lao','Segoe UI',sans-serif;
          display:flex;justify-content:space-between;align-items:center;
          border-top:1px solid #e5e7eb;">
          <span>ລາຍງານການເງິນ</span>
          <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>
    """
    return render_pdf_document(
        html,
        viewport_width=1122,
        viewport_height=794,
        margin_top="4mm",
        margin_right="0mm",
        margin_bottom="14mm",
        margin_left="0mm",
        footer_template=footer_template,
    )