from datetime import datetime
import math

from app.services.pdf.assets import font_data_urls


def build_popular_subjects_report_context(
    report_data: dict[str, object],
) -> dict[str, object]:
    regular_font_url, bold_font_url = font_data_urls()
    filters = report_data.get("filters") or {}
    summary = report_data.get("summary") or {}
    subjects = report_data.get("subjects") or []
    levels = report_data.get("levels") or []
    categories = report_data.get("categories") or {}

    filter_items: list[str] = []
    academic_year_name = filters.get("academic_year_name")
    if academic_year_name:
        filter_items.append(f"ສົກຮຽນ: {academic_year_name}")

    top_subjects = subjects[:5]
    chart_colors = ["#3b82f6", "#16a34a", "#f59e0b", "#ef4444", "#ec4899"]
    max_student_count = max(
        (int(item.get("student_count") or 0) for item in top_subjects),
        default=1,
    )

    def _pie_path(start_angle: float, end_angle: float, radius: float = 92.0) -> str:
        center_x = 120.0
        center_y = 120.0
        start_x = center_x + radius * math.cos(math.radians(start_angle))
        start_y = center_y + radius * math.sin(math.radians(start_angle))
        end_x = center_x + radius * math.cos(math.radians(end_angle))
        end_y = center_y + radius * math.sin(math.radians(end_angle))
        large_arc = 1 if end_angle - start_angle > 180 else 0
        return (
            f"M {center_x:.2f} {center_y:.2f} "
            f"L {start_x:.2f} {start_y:.2f} "
            f"A {radius:.2f} {radius:.2f} 0 {large_arc} 1 {end_x:.2f} {end_y:.2f} Z"
        )

    pie_segments: list[dict[str, object]] = []
    current_angle = 0.0
    for index, item in enumerate(top_subjects):
        percentage = float(item.get("percentage") or 0)
        sweep = (percentage / 100) * 360 if percentage else 0
        end_angle = current_angle + sweep
        mid_angle = current_angle + sweep / 2 if sweep else current_angle
        label_x = 120 + 52 * math.cos(math.radians(mid_angle))
        label_y = 120 + 52 * math.sin(math.radians(mid_angle))
        pie_segments.append(
            {
                "path": _pie_path(current_angle, end_angle),
                "label_x": round(label_x, 2),
                "label_y": round(label_y, 2),
                "color": chart_colors[index % len(chart_colors)],
                "percentage_display": f"{percentage:.1f}%",
                "subject_name": item.get("subject_name"),
                "student_count_display": f"{int(item.get('student_count') or 0)} ຄົນ",
            }
        )
        current_angle = end_angle

    ranked_subjects = []
    for index, item in enumerate(top_subjects, start=1):
        student_count = int(item.get("student_count") or 0)
        ranked_subjects.append(
            {
                **item,
                "rank": index,
                "color": chart_colors[(index - 1) % len(chart_colors)],
                "student_count_display": f"{student_count} ຄົນ",
                "percentage_display": f"{float(item.get('percentage') or 0):.1f}%",
                "progress_width": max(
                    10,
                    round(student_count / max_student_count * 100, 1),
                ),
            }
        )

    level_rows = sorted(
        levels,
        key=lambda item: (
            -int(item.get("student_count") or 0),
            item.get("subject_name") or "",
            item.get("level_name") or "",
        ),
    )

    category_items = [
        {"name": name, "count": count}
        for name, count in sorted(categories.items(), key=lambda entry: entry[1], reverse=True)
    ]

    max_category_count = max((int(item["count"]) for item in category_items), default=1)
    category_chart_items = []
    svg_chart_items = []
    bar_width = 34
    gap = 72
    chart_base_y = 188
    for index, item in enumerate(category_items):
        count = int(item["count"])
        height = max(18, round(count / max_category_count * 180))
        category_chart_items.append(
            {
                **item,
                "height": height,
            }
        )
        x = 34 + index * gap
        svg_chart_items.append(
            {
                **item,
                "x": x,
                "y": chart_base_y - height,
                "height": height,
                "width": bar_width,
                "label_x": x + bar_width / 2,
            }
        )

    y_axis_labels = []
    for step in range(6, 0, -1):
        value = round(max_category_count * step / 6)
        y_axis_labels.append({"label": f"{value} ຄົນ"})

    return {
        "font_regular_url": regular_font_url,
        "font_bold_url": bold_font_url,
        "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "filter_items": filter_items,
        "summary": summary,
        "subjects": ranked_subjects,
        "levels": level_rows,
        "categories": category_items,
        "pie_segments": pie_segments,
        "category_chart_items": category_chart_items,
        "category_chart_svg_items": svg_chart_items,
        "y_axis_labels": y_axis_labels,
    }