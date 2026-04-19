from datetime import datetime

from app.services.pdf.assets import font_data_urls
from app.services.pdf.charts import (
    build_conic_gradient,
    build_donut_svg,
    build_yearly_chart_items,
    build_yearly_chart_svg,
)
from app.services.pdf.formatters import (
    format_finance_currency,
    format_plain_currency,
    format_report_date_text,
)


def build_finance_report_context(
    report_data: dict[str, object],
    *,
    tab: str,
) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    filters = report_data.get("filters") or {}
    summary = report_data.get("summary") or {}
    income_breakdown = report_data.get("income_breakdown") or []
    expense_breakdown = report_data.get("expense_breakdown") or []
    yearly_comparison = report_data.get("yearly_comparison") or []
    incomes = report_data.get("incomes") or []
    expenses = report_data.get("expenses") or []

    normalized_tab = tab if tab in {"overview", "income", "expense"} else "overview"
    tab_title_map = {
        "overview": "ພາບລວມການເງິນ",
        "income": "ລາຍງານລາຍຮັບ",
        "expense": "ລາຍງານລາຍຈ່າຍ",
    }

    filter_items: list[str] = []

    def add_filter(label: str, value: object) -> None:
        if value is None:
            return
        text = str(value).strip()
        if text:
            filter_items.append(f"{label}: {text}")

    add_filter("ສົກຮຽນ", filters.get("academic_year_name"))
    add_filter("ປີ", filters.get("year"))
    add_filter("ແທັບ", tab_title_map[normalized_tab])

    income_colors = ["#2563eb", "#16a34a", "#8b5cf6", "#f59e0b", "#06b6d4"]
    expense_colors = ["#dc2626", "#f97316", "#0ea5e9", "#8b5cf6", "#2563eb"]

    income_color_classes = ["income-c1", "income-c2", "income-c3", "income-c4", "income-c5"]
    expense_color_classes = ["expense-c1", "expense-c2", "expense-c3", "expense-c4", "expense-c5"]

    income_breakdown_items = [
        {
            **item,
            "amount_display": format_finance_currency(float(item.get("amount") or 0)),
            "percentage_display": f"{float(item.get('percentage') or 0):.1f}%",
            "color": income_colors[index % len(income_colors)],
            "color_class": income_color_classes[index % len(income_color_classes)],
        }
        for index, item in enumerate(income_breakdown)
    ]
    expense_breakdown_items = [
        {
            **item,
            "amount_display": format_finance_currency(float(item.get("amount") or 0)),
            "percentage_display": f"{float(item.get('percentage') or 0):.1f}%",
            "color": expense_colors[index % len(expense_colors)],
            "color_class": expense_color_classes[index % len(expense_color_classes)],
        }
        for index, item in enumerate(expense_breakdown)
    ]
    yearly_chart_items = build_yearly_chart_items(yearly_comparison)

    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "selected_year": filters.get("year") or datetime.now().year,
        "tab": normalized_tab,
        "tab_title": tab_title_map[normalized_tab],
        "summary": {
            "total_income": format_finance_currency(float(summary.get("total_income") or 0)),
            "total_expense": format_finance_currency(float(summary.get("total_expense") or 0)),
            "balance": format_finance_currency(float(summary.get("balance") or 0)),
        },
        "income_breakdown": income_breakdown_items,
        "expense_breakdown": expense_breakdown_items,
        "income_chart_style": build_conic_gradient(income_breakdown_items, income_colors),
        "expense_chart_style": build_conic_gradient(expense_breakdown_items, expense_colors),
        "income_chart_svg": build_donut_svg(income_breakdown_items, income_colors),
        "expense_chart_svg": build_donut_svg(expense_breakdown_items, expense_colors),
        "yearly_comparison": [
            {
                **item,
                "income_display": format_plain_currency(float(item.get("income") or 0)),
                "expense_display": format_plain_currency(float(item.get("expense") or 0)),
                "balance_display": format_plain_currency(float(item.get("balance") or 0)),
            }
            for item in yearly_comparison
        ],
        "yearly_chart_items": yearly_chart_items,
        "yearly_chart_svg": build_yearly_chart_svg(yearly_comparison),
        "incomes": [
            {
                **item,
                "amount_display": format_finance_currency(float(item.get("amount") or 0)),
                "income_date_display": format_report_date_text(item.get("income_date")),
                "description_display": item.get("description") or "-",
            }
            for item in incomes
        ],
        "expenses": [
            {
                **item,
                "amount_display": format_finance_currency(float(item.get("amount") or 0)),
                "expense_date_display": format_report_date_text(item.get("expense_date")),
                "description_display": item.get("description") or "-",
            }
            for item in expenses
        ],
        "total_income_count": report_data.get("total_income_count", 0),
        "total_expense_count": report_data.get("total_expense_count", 0),
        "filter_items": filter_items,
    }