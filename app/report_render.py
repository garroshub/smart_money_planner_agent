import re


def clean_body_text(text: str) -> str:
    value = text or ""
    value = value.replace("**", "")
    value = value.replace("__", "")
    value = value.replace("*", "")
    value = value.replace("_", " ")
    value = value.replace("`", "")
    value = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", value)
    value = re.sub(r"(?<=[A-Za-z]),(?=[A-Za-z])", ", ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def parse_report_blocks(markdown_text: str) -> list[dict]:
    lines = (markdown_text or "").splitlines()
    blocks: list[dict] = []
    paragraph: list[str] = []
    bullets: list[str] = []
    plan_rows: list[dict] = []

    def parse_plan_allocation_line(text: str) -> dict | None:
        pattern = re.compile(
            r"^([A-Za-z][A-Za-z ]*):\s*\$?([\d,]+)\s*Emergency\s*Fund\s*\|\s*\$?([\d,]+)\s*Debt\s*Payment\s*\|\s*\$?([\d,]+)\s*Investment$",
            re.IGNORECASE,
        )
        match = pattern.match(text.strip())
        if not match:
            return None
        return {
            "Plan": clean_body_text(match.group(1)),
            "Emergency Fund": int(match.group(2).replace(",", "")),
            "Debt Payment": int(match.group(3).replace(",", "")),
            "Investment": int(match.group(4).replace(",", "")),
        }

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(
                {"type": "paragraph", "text": clean_body_text(" ".join(paragraph))}
            )
            paragraph = []

    def flush_bullets() -> None:
        nonlocal bullets
        if bullets:
            blocks.append(
                {
                    "type": "bullets",
                    "items": [clean_body_text(item) for item in bullets],
                }
            )
            bullets = []

    def flush_plan_rows() -> None:
        nonlocal plan_rows
        if plan_rows:
            blocks.append({"type": "plan_table", "rows": plan_rows})
            plan_rows = []

    for raw in lines:
        stripped = raw.strip()

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            flush_paragraph()
            flush_bullets()
            flush_plan_rows()
            blocks.append(
                {
                    "type": "heading",
                    "level": len(heading_match.group(1)),
                    "text": clean_body_text(heading_match.group(2)),
                }
            )
            continue

        if not stripped:
            flush_paragraph()
            flush_bullets()
            flush_plan_rows()
            continue

        bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
        if bullet_match:
            flush_paragraph()
            flush_plan_rows()
            bullets.append(bullet_match.group(1))
            continue

        plan_row = parse_plan_allocation_line(stripped)
        if plan_row:
            flush_paragraph()
            flush_bullets()
            plan_rows.append(plan_row)
            continue

        flush_bullets()
        flush_plan_rows()
        paragraph.append(stripped)

    flush_paragraph()
    flush_bullets()
    flush_plan_rows()
    return blocks
