from datetime import datetime

from app.services.pdf.assets import font_data_urls
from app.services.pdf.formatters import format_plain_currency


def build_assessment_report_context(
    report_data: dict[str, object],
) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    filters = report_data.get("filters") or {}
    items = report_data.get("items") or []

    filter_items: list[str] = []

    def add_filter(label: str, value: object) -> None:
        if value is None:
            return
        text = str(value).strip()
        if text:
            filter_items.append(f"{label}: {text}")

    add_filter("ສົກຮຽນ", filters.get("academic_year_name"))
    add_filter("ຮອບປະເມີນ", filters.get("evaluation_round_name"))
    add_filter("ວິຊາ", filters.get("subject_name"))
    add_filter("ລະດັບ", filters.get("level_name"))
    add_filter("ອັນດັບ", filters.get("ranking"))

    rank_one = sum(1 for item in items if item.get("ranking") == 1)
    rank_two = sum(1 for item in items if item.get("ranking") == 2)
    rank_three = sum(1 for item in items if item.get("ranking") == 3)
    total_prize = sum(float(item.get("prize") or 0) for item in items)

    prepared_items = []
    for index, item in enumerate(items, start=1):
        prepared_items.append(
            {
                **item,
                "index": index,
                "score_display": f"{float(item.get('score') or 0):.2f}",
                "prize_display": format_plain_currency(float(item.get("prize") or 0))
                if item.get("prize")
                else "-",
            }
        )

    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_count": report_data.get("total_count", 0),
        "rank_one": rank_one,
        "rank_two": rank_two,
        "rank_three": rank_three,
        "total_prize": format_plain_currency(total_prize),
        "items": prepared_items,
        "filter_items": filter_items,
    }