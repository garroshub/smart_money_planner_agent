from app.report_render import clean_body_text, parse_report_blocks


def test_clean_body_text_removes_markdown_emphasis():
    text = "Client u_004 has **low** risk and _stable_ income."
    cleaned = clean_body_text(text)
    assert "**" not in cleaned
    assert "_" not in cleaned
    assert "low" in cleaned
    assert "stable" in cleaned


def test_parse_report_blocks_keeps_headings_plain_body_and_bullets():
    report = "## Overview\nClient u_004 has _low_ risk.\n\n- First item\n- Second item"
    blocks = parse_report_blocks(report)

    assert blocks[0]["type"] == "heading"
    assert blocks[0]["text"] == "Overview"
    assert blocks[1]["type"] == "paragraph"
    assert "_" not in blocks[1]["text"]
    assert "low" in blocks[1]["text"]
    assert blocks[2]["type"] == "bullets"
    assert blocks[2]["items"] == ["First item", "Second item"]


def test_parse_report_blocks_extracts_plan_table_rows():
    report = """## Plans
Three strategic allocations have been identified for the $200 surplus:

Debt Focus: $40 Emergency Fund | $100 Debt Payment | $60 Investment
Balanced: $60 Emergency Fund | $70 Debt Payment | $70 Investment
Growth Focus: $30 Emergency Fund | $50 Debt Payment | $120 Investment
"""
    blocks = parse_report_blocks(report)

    table_blocks = [block for block in blocks if block["type"] == "plan_table"]
    assert len(table_blocks) == 1
    rows = table_blocks[0]["rows"]
    assert len(rows) == 3
    assert rows[0]["Plan"] == "Debt Focus"
    assert rows[0]["Emergency Fund"] == 40
    assert rows[0]["Debt Payment"] == 100
    assert rows[0]["Investment"] == 60
