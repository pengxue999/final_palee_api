from datetime import datetime

from app.services.pdf.assets import font_data_urls
from app.services.pdf.formatters import format_finance_currency


def build_donation_report_context(report_data: dict[str, object]) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    filters = report_data.get("filters") or {}
    summary = report_data.get("summary") or {}
    donations = report_data.get("donations") or []
    categories = summary.get("categories") or {}

    filter_items: list[str] = []

    def add_filter(label: str, value: object) -> None:
        if value is None:
            return
        text = str(value).strip()
        if text:
            filter_items.append(f"{label}: {text}")

    add_filter("ປີ", filters.get("year"))
    add_filter("ຜູ້ບໍລິຈາກ", filters.get("donor_name"))
    add_filter("ປະເພດ", filters.get("donation_category_name"))

    category_items = [
        {"name": name, "count": count}
        for name, count in sorted(categories.items(), key=lambda item: item[1], reverse=True)
    ]

    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "filter_items": filter_items,
        "total_count": summary.get("total_count", 0),
        "category_count": summary.get("category_count", 0),
        "total_amount": format_finance_currency(float(summary.get("total_amount") or 0)),
        "categories": category_items,
        "donations": donations,
    }