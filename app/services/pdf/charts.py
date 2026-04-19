from math import cos, radians, sin
from urllib.parse import quote


def format_compact_currency(value: float) -> str:
    absolute = abs(value)
    if absolute >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if absolute >= 1_000:
        return f"{value / 1_000:.0f}K"
    return f"{value:.0f}"


def build_conic_gradient(items: list[dict[str, object]], colors: list[str]) -> str:
    if not items:
        return "conic-gradient(#e5e7eb 0deg 360deg)"

    current_angle = 0.0
    segments: list[str] = []
    for index, item in enumerate(items):
        percentage = float(item.get("percentage") or 0)
        sweep = max(percentage, 0) * 3.6
        next_angle = current_angle + sweep
        color = colors[index % len(colors)]
        segments.append(f"{color} {current_angle:.2f}deg {next_angle:.2f}deg")
        current_angle = next_angle

    if current_angle < 360:
        segments.append(f"#e5e7eb {current_angle:.2f}deg 360deg")

    return f"conic-gradient({', '.join(segments)})"


def polar_to_cartesian(
    cx: float,
    cy: float,
    radius: float,
    angle_deg: float,
) -> tuple[float, float]:
    angle_rad = radians(angle_deg - 90)
    return cx + radius * cos(angle_rad), cy + radius * sin(angle_rad)


def build_donut_svg(items: list[dict[str, object]], colors: list[str]) -> str:
    size = 190
    stroke = 62
    radius = (size - stroke) / 2
    center = size / 2
    circumference = 2 * 3.141592653589793 * radius
    inner_radius = 31
    label_radius = center - (stroke / 2) + 1

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        f'<circle cx="{center}" cy="{center}" r="{radius}" fill="none" stroke="#e5e7eb" stroke-width="{stroke}"/>',
    ]

    offset = 0.0
    current_angle = 0.0
    for index, item in enumerate(items):
        percentage = float(item.get("percentage") or 0)
        if percentage <= 0:
            continue
        arc = circumference * (percentage / 100.0)
        sweep_angle = percentage * 3.6
        color = colors[index % len(colors)]
        parts.append(
            f'<circle cx="{center}" cy="{center}" r="{radius}" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="butt" transform="rotate(-90 {center} {center})" '
            f'stroke-dasharray="{arc:.2f} {circumference:.2f}" stroke-dashoffset="{-offset:.2f}"/>'
        )

        if percentage >= 4.5:
            mid_angle = current_angle + (sweep_angle / 2)
            label_x, label_y = polar_to_cartesian(center, center, label_radius, mid_angle)
            font_size = 18 if percentage >= 35 else 14
            parts.append(
                f'<text x="{label_x:.2f}" y="{label_y:.2f}" text-anchor="middle" dominant-baseline="middle" '
                f'fill="#ffffff" font-size="{font_size}" font-weight="700" font-family="Arial">{percentage:.1f}%</text>'
            )

        offset += arc
        current_angle += sweep_angle

    parts.append(f'<circle cx="{center}" cy="{center}" r="{inner_radius}" fill="#ffffff"/>')
    parts.append("</svg>")
    return f"data:image/svg+xml;utf8,{quote(''.join(parts))}"


def build_yearly_chart_svg(yearly_comparison: list[dict[str, object]]) -> str:
    width = 920
    height = 260
    padding_left = 78
    padding_right = 20
    padding_top = 18
    padding_bottom = 44
    plot_height = 176
    plot_width = width - padding_left - padding_right

    if not yearly_comparison:
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            '<rect width="100%" height="100%" fill="#ffffff"/>'
            '<text x="50%" y="50%" text-anchor="middle" fill="#72829b" font-size="16" font-family="Arial">ບໍ່ມີຂໍ້ມູນ</text>'
            "</svg>"
        )
        return f"data:image/svg+xml;utf8,{quote(svg)}"

    max_value = max(
        max(float(item.get("income") or 0), float(item.get("expense") or 0))
        for item in yearly_comparison
    ) or 1

    grid_lines = 5
    segments = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff" rx="12" ry="12"/>',
    ]

    vertical_lines = min(max(len(yearly_comparison) * 2 + 16, 12), 18)
    for index in range(vertical_lines):
        x = padding_left + (plot_width / max(vertical_lines - 1, 1)) * index
        segments.append(
            f'<line x1="{x:.2f}" y1="{padding_top}" x2="{x:.2f}" y2="{padding_top + plot_height}" stroke="rgba(148,163,184,0.45)" stroke-width="1" stroke-dasharray="6 4"/>'
        )

    for index in range(grid_lines + 1):
        y = padding_top + (plot_height / grid_lines) * index
        label_value = max_value - ((max_value / grid_lines) * index)
        segments.append(
            f'<line x1="{padding_left}" y1="{y:.2f}" x2="{width - padding_right}" y2="{y:.2f}" stroke="rgba(148,163,184,0.25)" stroke-width="1"/>'
        )
        segments.append(
            f'<text x="{padding_left - 8}" y="{y + 4:.2f}" text-anchor="end" fill="#64748b" font-size="11" font-family="Arial">{format_compact_currency(label_value)}</text>'
        )

    count = len(yearly_comparison)
    group_width = max(plot_width / max(count, 1), 72)
    rod_width = 14
    rod_gap = 8
    start_x = padding_left + max((plot_width - group_width * count) / 2, 0)

    for index, item in enumerate(yearly_comparison):
        income = float(item.get("income") or 0)
        expense = float(item.get("expense") or 0)
        income_height = (income / max_value) * plot_height
        expense_height = (expense / max_value) * plot_height
        group_center = start_x + group_width * index + group_width / 2
        income_x = group_center - rod_gap / 2 - rod_width
        expense_x = group_center + rod_gap / 2
        income_y = padding_top + plot_height - income_height
        expense_y = padding_top + plot_height - expense_height
        label_y = padding_top + plot_height + 18

        segments.append(
            f'<rect x="{income_x:.2f}" y="{income_y:.2f}" width="{rod_width}" height="{max(income_height, 0):.2f}" rx="4" ry="4" fill="#16a34a"/>'
        )
        segments.append(
            f'<rect x="{expense_x:.2f}" y="{expense_y:.2f}" width="{rod_width}" height="{max(expense_height, 0):.2f}" rx="4" ry="4" fill="#ef4444"/>'
        )
        segments.append(
            f'<text x="{group_center:.2f}" y="{label_y:.2f}" text-anchor="middle" fill="#475569" font-size="12" font-family="Arial">{item.get("year")}</text>'
        )

    segments.append("</svg>")
    return f"data:image/svg+xml;utf8,{quote(''.join(segments))}"


def build_yearly_chart_items(
    yearly_comparison: list[dict[str, object]],
) -> list[dict[str, object]]:
    if not yearly_comparison:
        return []

    max_value = max(
        max(float(item.get("income") or 0), float(item.get("expense") or 0))
        for item in yearly_comparison
    )
    denominator = max_value if max_value > 0 else 1

    chart_items: list[dict[str, object]] = []
    for item in yearly_comparison:
        income = float(item.get("income") or 0)
        expense = float(item.get("expense") or 0)
        chart_items.append(
            {
                **item,
                "income_height": max((income / denominator) * 170, 4 if income > 0 else 0),
                "expense_height": max((expense / denominator) * 170, 4 if expense > 0 else 0),
            }
        )

    return chart_items