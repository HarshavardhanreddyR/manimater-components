"""Educational visualization of SQL INNER, LEFT, RIGHT, and FULL JOINs."""
from __future__ import annotations

from manim import (
    DOWN,
    RIGHT,
    UP,
    WHITE,
    FadeIn,
    Line,
    Rectangle,
    RoundedRectangle,
    VGroup,
)

from ... import theme
from ...ctx import Ctx, label
from ...registry import Param as P, component


# ---------------------------------------------------------------------
# SQL JOIN logic
# ---------------------------------------------------------------------


def _valid_key(value: object) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _clean_rows(rows: list[dict] | None, key: str) -> list[dict]:
    """Keep valid rows with supported scalar join keys."""
    cleaned = []
    for row in (rows or [])[:8]:
        if not isinstance(row, dict) or key not in row:
            continue
        if not _valid_key(row[key]):
            continue
        cleaned.append(dict(row))
    return cleaned


def _compute_join(
    left_rows: list[dict],
    right_rows: list[dict],
    key: str,
    join_type: str,
) -> list[dict]:
    """Compute an equality join, preserving duplicate-key fan-out.

    As in SQL, NULL does not equal NULL for join matching.
    """
    left_rows = _clean_rows(left_rows, key)
    right_rows = _clean_rows(right_rows, key)

    right_by_key = {}
    for index, row in enumerate(right_rows):
        value = row[key]
        if value is not None:
            right_by_key.setdefault(value, []).append((index, row))

    matched_right = set()
    result = []

    for left in left_rows:
        value = left[key]
        matches = right_by_key.get(value, []) if value is not None else []

        if matches:
            for right_index, right in matches:
                result.append({"key": value, "left": left, "right": right})
                matched_right.add(right_index)
        elif join_type in ("left", "full"):
            result.append({"key": value, "left": left, "right": None})

    if join_type in ("right", "full"):
        for index, right in enumerate(right_rows):
            if index not in matched_right:
                result.append({"key": right[key], "left": None, "right": right})

    return result


# ---------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------


def _short(value: object, limit: int = 16) -> str:
    value = "NULL" if value is None else str(value)
    return value if len(value) <= limit else value[: limit - 1] + "…"


def _secondary_field(rows: list[dict], key: str) -> str:
    """Choose the first non-key field, or a readable fallback."""
    for row in rows:
        for name in row:
            if name != key:
                return name
    return "value"


def _cell(
    value: object,
    width: float,
    height: float,
    fill: str,
    text_color: str = theme.FG,
    font_size: int = 19,
):
    rect = Rectangle(
        width=width,
        height=height,
        stroke_color="#35414D",
        stroke_width=1,
        fill_color=fill,
        fill_opacity=1,
    )
    content = label(_short(value), size=font_size, color=text_color)
    if content.width > width - 0.18:
        content.scale_to_fit_width(width - 0.18)
    content.move_to(rect.get_center())
    return VGroup(rect, content)


def _table_row(
    values: list,
    widths: list[float],
    height: float,
    fill: str,
    text_color: str = theme.FG,
    font_size: int = 19,
):
    cells = VGroup()
    for value, width in zip(values, widths):
        cells.add(_cell(value, width, height, fill, text_color, font_size))
    cells.arrange(RIGHT, buff=0)
    return cells


def _source_table(
    title: str,
    rows: list[dict],
    key: str,
    color: str,
):
    """Return a source table and its key-cell row groups."""
    field = _secondary_field(rows, key)
    widths = [1.65, 2.65]

    header = _table_row([key, field], widths, 0.44, color, WHITE, 18)
    body = VGroup()

    for row in rows[:4]:
        body.add(
            _table_row(
                [row[key], row.get(field)],
                widths,
                0.43,
                "#18232E",
                theme.FG,
                18,
            )
        )

    if not body:
        body.add(
            _table_row(["—", "Empty"], widths, 0.43, "#18232E", theme.MUTED, 18)
        )

    table = VGroup(header, *body).arrange(DOWN, buff=0)
    title_text = label(title, size=22, color=color)
    title_text.next_to(table, UP, buff=0.14)
    group = VGroup(title_text, table)

    hidden = max(0, len(rows) - 4)
    # Each body row is retained so connectors can be anchored to the actual row.
    return group, list(body), field, hidden


def _result_table(
    result: list[dict],
    key: str,
    left_field: str,
    right_field: str,
):
    """Build a result table with independently animatable rows."""
    widths = [1.5, 4.45, 4.45]
    header = _table_row(
        [key, left_field, right_field],
        widths,
        0.42,
        "#263746",
        WHITE,
        18,
    )

    body = VGroup()
    for item in result[:4]:
        unmatched = item["left"] is None or item["right"] is None
        fill = "#3A301D" if unmatched else "#173329"
        text_color = theme.YELLOW if unmatched else theme.FG

        left_value = (
            "NULL" if item["left"] is None else item["left"].get(left_field)
        )
        right_value = (
            "NULL" if item["right"] is None else item["right"].get(right_field)
        )

        body.add(
            _table_row(
                [item["key"], left_value, right_value],
                widths,
                0.42,
                fill,
                text_color,
                18,
            )
        )

    if not result:
        body.add(
            _table_row(
                ["—", "No matching rows", "—"],
                widths,
                0.42,
                "#18232E",
                theme.MUTED,
                18,
            )
        )

    return header, body


# ---------------------------------------------------------------------
# Component
# ---------------------------------------------------------------------


@component(
    name="sql_join",
    description="Visualize SQL JOINs with matching rows, unmatched records, and NULL values.",
    params={
        "join_type": P(
            "string",
            "SQL join type",
            default="full",
            choices=["inner", "left", "right", "full"],
        ),
        "left_rows": P(
            "object[]",
            "Rows in the left table",
            default=[
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 3, "name": "Carol"},
            ],
        ),
        "right_rows": P(
            "object[]",
            "Rows in the right table",
            default=[
                {"id": 1, "department": "Engineering"},
                {"id": 2, "department": "Sales"},
                {"id": 4, "department": "Finance"},
            ],
        ),
        "key": P("string", "Column used to match records", default="id"),
    },
    example={
        "join_type": "full",
        "left_rows": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Carol"},
        ],
        "right_rows": [
            {"id": 1, "department": "Engineering"},
            {"id": 2, "department": "Sales"},
            {"id": 4, "department": "Finance"},
        ],
        "key": "id",
    },
    domain="databases",
)
def sql_join(
    ctx: Ctx,
    join_type: str = "full",
    left_rows: list[dict] | None = None,
    right_rows: list[dict] | None = None,
    key: str = "id",
) -> None:
    join_type = (join_type or "inner").lower().strip()
    if join_type not in {"inner", "left", "right", "full"}:
        join_type = "inner"

    key = (key or "id").strip()[:20] or "id"
    left_rows = _clean_rows(left_rows, key)
    right_rows = _clean_rows(right_rows, key)
    result = _compute_join(left_rows, right_rows, key, join_type)

    left_field = _secondary_field(left_rows, key)
    right_field = _secondary_field(right_rows, key)

    # Header and short explanation.
    heading = ctx.heading(f"SQL {join_type.upper()} JOIN")
    explanations = {
        "inner": "Keep only rows with a matching key in both tables",
        "left": "Keep every left row; unmatched right values become NULL",
        "right": "Keep every right row; unmatched left values become NULL",
        "full": "Keep all rows; unmatched values on either side become NULL",
    }
    subtitle = label(explanations[join_type], size=17, color=theme.MUTED)
    subtitle.next_to(heading, DOWN, buff=0.10)

    # Source tables.
    left_table, left_body, left_field, left_hidden = _source_table(
        "LEFT TABLE", left_rows, key, theme.ACCENT
    )
    right_table, right_body, right_field, right_hidden = _source_table(
        "RIGHT TABLE", right_rows, key, theme.PURPLE
    )
    left_table.move_to((-3.05, 1.68, 0))
    right_table.move_to((3.05, 1.68, 0))

    # Draw one connector for each matching pair, anchored to the row centres.
    connectors = VGroup()
    for left_index, left in enumerate(left_rows[:4]):
        value = left[key]
        if value is None:
            continue
        for right_index, right in enumerate(right_rows[:4]):
            if right[key] != value or right[key] is None:
                continue

            start = left_table.get_right()
            end = right_table.get_left()
            start = start + UP * (
                left_body[left_index].get_center()[1] - left_table.get_center()[1]
            )
            end = end + UP * (
                right_body[right_index].get_center()[1] - right_table.get_center()[1]
            )
            connectors.add(
                Line(start, end, color=theme.GOOD, stroke_width=3)
            )

    # Result table. Keep the entire table in the fit group so its rows remain
    # aligned after ctx.fit(), even though they are revealed individually.
    result_heading = label(
        f"RESULT  ·  {len(result)} ROWS",
        size=21,
        color=theme.GOOD,
    )
    result_heading.move_to((0, -0.12, 0))

    result_header, result_body = _result_table(
        result, key, left_field, right_field
    )
    result_table = VGroup(result_header, *result_body).arrange(DOWN, buff=0)
    result_table.move_to((0, -1.42, 0))

    result_border = RoundedRectangle(
        width=11.15,
        height=result_table.height + 0.30,
        corner_radius=0.12,
        stroke_color="#35414D",
        stroke_width=1.5,
        fill_color=theme.PANEL,
        fill_opacity=1,
    )
    result_border.move_to(result_table.get_center())

    notes = []
    if left_hidden or right_hidden:
        notes.append("Only the first 4 rows of each input are shown")
    if len(result) > 4:
        notes.append(f"+ {len(result) - 4} additional result rows")
    if any(item["left"] is None or item["right"] is None for item in result):
        notes.append("NULL = no matching record")

    footer = None
    if notes:
        footer = label("  •  ".join(notes), size=13, color=theme.YELLOW)
        footer.move_to((0, -2.68, 0))

    # Include every result row in this group before fitting. This prevents
    # body rows from being left behind when ctx.fit scales/repositions content.
    static = VGroup(
        heading,
        subtitle,
        left_table,
        right_table,
        connectors,
        result_heading,
        result_border,
        result_table,
    )
    if footer is not None:
        static.add(footer)

    ctx.fit(static)

    # Animation sequence: source tables, matching relationships, then result.
    ctx.play(FadeIn(heading), FadeIn(subtitle), run_time=0.7)
    ctx.play(FadeIn(left_table), FadeIn(right_table), run_time=0.9)

    if len(connectors):
        ctx.play(FadeIn(connectors), run_time=0.7)

    ctx.play(
        FadeIn(result_border),
        FadeIn(result_heading),
        FadeIn(result_header),
        run_time=0.7,
    )

    for row in result_body:
        ctx.play(FadeIn(row), run_time=0.38)

    if footer is not None:
        ctx.play(FadeIn(footer), run_time=0.4)

    ctx.finish()
