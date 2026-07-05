import io
import math
from datetime import datetime

from app.models import Scan, TestResult
from app.scoring.calculator import SCENARIO_OWASP_MAP
from app.reporting.vulnerability_data import SCENARIO_METADATA

SEVERITY_COLORS = {
    "Critical": "#DC2626",
    "High": "#EA580C",
    "Medium": "#F59E0B",
    "Low": "#22C55E",
}


def _severity_color(weight: float) -> str:
    if weight >= 2.0:
        return "#DC2626"
    if weight >= 1.5:
        return "#EA580C"
    if weight >= 1.0:
        return "#F59E0B"
    return "#22C55E"


def _risk_color(score: float) -> str:
    if score >= 80:
        return "#22C55E"
    if score >= 50:
        return "#F59E0B"
    return "#EF4444"


def _risk_label(score: float) -> str:
    if score >= 80:
        return "Low Risk"
    if score >= 50:
        return "Moderate Risk"
    return "High Risk"


def generate_pdf(scan: Scan, results: list[TestResult]) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch, mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor, white, black
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, PageTemplate, Frame, BaseDocTemplate, KeepTogether,
        )
        from reportlab.graphics.shapes import Drawing, Circle, Wedge, String, Rect
        from reportlab.graphics.charts.doughnut import Doughnut
        from reportlab.graphics import renderPDF

        buf = io.BytesIO()
        W, H = A4
        margin = 0.7 * inch

        styles = getSampleStyleSheet()
        PRIMARY = HexColor("#06B6D4")
        DARK_BG = HexColor("#F1F5F9")
        CARD_BG = HexColor("#F8FAFC")
        TEXT_PRIMARY = HexColor("#1E293B")
        TEXT_SECONDARY = HexColor("#475569")
        TEXT_MUTED = HexColor("#64748B")
        BORDER = HexColor("#CBD5E1")

        s_cover_title = ParagraphStyle("CoverTitle", fontSize=28, leading=34, textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6)
        s_cover_sub = ParagraphStyle("CoverSub", fontSize=11, leading=15, textColor=TEXT_SECONDARY, alignment=TA_CENTER, spaceAfter=4)
        s_cover_small = ParagraphStyle("CoverSmall", fontSize=8, leading=11, textColor=TEXT_MUTED, alignment=TA_CENTER)
        s_h1 = ParagraphStyle("H1", fontSize=16, leading=20, textColor=TEXT_PRIMARY, spaceAfter=6, spaceBefore=4)
        s_h2 = ParagraphStyle("H2", fontSize=12, leading=15, textColor=TEXT_PRIMARY, spaceAfter=4, spaceBefore=8)
        s_h3 = ParagraphStyle("H3", fontSize=10, leading=13, textColor=TEXT_PRIMARY, spaceAfter=3)
        s_body = ParagraphStyle("Body", fontSize=8.5, leading=12, textColor=TEXT_SECONDARY, spaceAfter=4)
        s_small = ParagraphStyle("Small", fontSize=7.5, leading=10, textColor=TEXT_MUTED)
        s_label_center = ParagraphStyle("LC", fontSize=7.5, textColor=TEXT_MUTED, alignment=TA_CENTER)
        s_badge = ParagraphStyle("Badge", fontSize=7.5, leading=9, alignment=TA_CENTER)

        score = scan.score if scan.score is not None else 0.0
        risk_lbl = _risk_label(score)
        risk_clr = _risk_color(score)

        if results:
            total_tests = len(results)
            total_passed = sum(1 for r in results if r.passed)
            total_failed = total_tests - total_passed
        else:
            total_tests = 0
            total_passed = 0
            total_failed = 0
        pass_rate = round(total_passed / total_tests * 100, 1) if total_tests else 0

        scenario_groups = {}
        for r in results:
            scenario_groups.setdefault(r.scenario_name, []).append(r)

        elements = []

        def draw_score_gauge(canvas, x, y, r, score_val, label=""):
            canvas.saveState()
            sweep = score_val / 100.0 * 360
            start_angle = 90
            end_angle = start_angle + sweep
            gap_angle = start_angle + sweep

            canvas.setStrokeColor(HexColor("#1E293B"))
            canvas.setLineWidth(10)
            canvas.arc(x - r, y - r, x + r, y + r, start_angle, start_angle + 360)

            color = HexColor(risk_clr)
            canvas.setStrokeColor(color)
            canvas.setLineWidth(10)
            if sweep > 0:
                canvas.arc(x - r, y - r, x + r, y + r, start_angle, end_angle)

            canvas.setFillColor(TEXT_PRIMARY)
            canvas.setFont("Helvetica-Bold", 28)
            canvas.drawCentredString(x, y - 8, f"{score_val:.0f}")
            if label:
                canvas.setFont("Helvetica", 6)
                canvas.setFillColor(TEXT_MUTED)
                canvas.drawCentredString(x, y - 24, label)
            canvas.restoreState()

        def draw_bar(canvas, x, y, w, h, pct, color_hex):
            canvas.saveState()
            canvas.setStrokeColor(BORDER)
            canvas.setLineWidth(0.5)
            canvas.drawRect(x, y, w, h, stroke=1, fill=0)
            fill_w = max(w * pct / 100, 0)
            if fill_w > 0:
                canvas.setFillColor(HexColor(color_hex))
                canvas.drawRect(x, y, fill_w, h, stroke=0, fill=1)
            canvas.restoreState()

        def risk_badge_html(text, color):
            return f'<font color="{color}"><b>⬤</b></font> <b>{text}</b>'

        # ===== PAGE 1: COVER =====
        elements.append(Spacer(1, 1.5 * inch))
        elements.append(Paragraph("SENTRA", s_cover_title))
        elements.append(Paragraph("AI Agent Security Audit Report", ParagraphStyle("CoverTag", fontSize=14, leading=18, textColor=TEXT_SECONDARY, alignment=TA_CENTER, spaceAfter=24)))
        elements.append(Spacer(1, 0.3 * inch))

        score_disp = f"{score:.0f}" if scan.score is not None else "--"
        s_score = ParagraphStyle("Score", fontSize=48, leading=54, textColor=HexColor(risk_clr), alignment=TA_CENTER, spaceAfter=2)
        elements.append(Paragraph(score_disp, s_score))
        elements.append(Paragraph(risk_badge_html(risk_lbl, risk_clr), ParagraphStyle("RiskBadge", fontSize=12, leading=16, alignment=TA_CENTER, spaceAfter=24)))
        elements.append(Spacer(1, 0.3 * inch))

        cover_info = [
            [Paragraph("<b>Scan ID</b>", s_small), Paragraph(f"#{scan.id}", s_small)],
            [Paragraph("<b>Agent</b>", s_small), Paragraph(f"{scan.provider or scan.agent_type}", s_small)],
            [Paragraph("<b>Iterations</b>", s_small), Paragraph(str(scan.iterations), s_small)],
            [Paragraph("<b>Date</b>", s_small), Paragraph(datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), s_small)],
        ]
        ci_table = Table(cover_info, colWidths=[1.2 * inch, 2.5 * inch])
        ci_table.setStyle(TableStyle([
            ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_MUTED),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(ci_table)
        elements.append(Spacer(1, 1.5 * inch))

        elements.append(Paragraph("CONFIDENTIAL", ParagraphStyle("Confidential", fontSize=9, leading=12, textColor=TEXT_MUTED, alignment=TA_CENTER, spaceBefore=12)))
        elements.append(PageBreak())

        # ===== PAGE 2: EXECUTIVE SUMMARY =====
        elements.append(Paragraph("Executive Summary", s_h1))
        elements.append(Spacer(1, 6))

        failing_scenarios = [s for s, r in scenario_groups.items() if sum(1 for x in r if x.passed) < len(r)]
        if failing_scenarios:
            meta = [SCENARIO_METADATA.get(s, {}) for s in failing_scenarios]
            critical = [m["label"] for m in meta if m.get("severity_weight", 0) >= 2.0]
            high = [m["label"] for m in meta if 1.5 <= m.get("severity_weight", 0) < 2.0]
            parts = []
            if critical:
                parts.append(f"{len(critical)} critical-severity vulnerabilities ({', '.join(critical)})")
            if high:
                parts.append(f"{len(high)} high-severity vulnerabilities ({', '.join(high)})")
            other = len(failing_scenarios) - len(critical) - len(high)
            if other > 0:
                parts.append(f"{other} medium/low-severity vulnerabilities")
            vuln_summary = "; ".join(parts) + "."
        else:
            vuln_summary = "No vulnerabilities were detected across all tested scenarios."

        summary_text = (
            f"Sentra conducted a security audit of the {scan.provider or scan.agent_type} AI agent "
            f"across {len(scenario_groups)} attack scenarios with {scan.iterations} iterations per scenario "
            f"({total_tests} total tests). The agent achieved a security score of {score} out of 100, "
            f"indicating {risk_lbl.lower()}. "
        )
        if total_failed > 0:
            summary_text += f"Of {total_tests} tests, {total_passed} passed and {total_failed} failed. {vuln_summary}"
        else:
            summary_text += f"All {total_tests} tests passed with no security issues detected."

        if scan.system_prompt:
            summary_text += f" The agent was configured with a custom system prompt."
        else:
            summary_text += " The agent was tested using its default system prompt configuration."

        elements.append(Paragraph(summary_text, s_body))
        elements.append(Spacer(1, 12))

        metrics_data = [
            [Paragraph(f"<b>{len(scenario_groups)}</b>", ParagraphStyle("MetricVal", fontSize=18, leading=22, textColor=PRIMARY, alignment=TA_CENTER)),
             Paragraph(f"<b>{total_tests}</b>", ParagraphStyle("MetricVal", fontSize=18, leading=22, textColor=TEXT_PRIMARY, alignment=TA_CENTER)),
             Paragraph(f"<b>{total_passed}</b>", ParagraphStyle("MetricVal", fontSize=18, leading=22, textColor=HexColor("#22C55E"), alignment=TA_CENTER)),
             Paragraph(f"<b>{total_failed}</b>", ParagraphStyle("MetricVal", fontSize=18, leading=22, textColor=HexColor("#EF4444"), alignment=TA_CENTER))],
            [Paragraph("Scenarios", s_label_center),
             Paragraph("Tests", s_label_center),
             Paragraph("Passed", s_label_center),
             Paragraph("Failed", s_label_center)],
        ]
        mt = Table(metrics_data, colWidths=[1.4 * inch] * 4)
        mt.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 0), (-1, 0), CARD_BG),
        ]))
        elements.append(mt)
        elements.append(Spacer(1, 6))

        if scan.owasp_breakdown:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("OWASP Risk Breakdown", s_h2))
            owasp_items = sorted(scan.owasp_breakdown.items(), key=lambda x: x[1])
            for cat, sc in owasp_items:
                clr = _risk_color(sc)
                owasp_rows = []
                owasp_rows.append([
                    Paragraph(f"<b>{cat}</b>", ParagraphStyle("OWCat", fontSize=8.5, leading=11, textColor=TEXT_SECONDARY)),
                    Paragraph(f"<b>{sc:.1f}%</b>", ParagraphStyle("OWScore", fontSize=8.5, leading=11, textColor=HexColor(clr), alignment=TA_RIGHT)),
                ])
                bar_drawing = Drawing(3.8 * inch, 8)
                bar_drawing.add(Rect(0, 2, 3.8 * inch, 5, strokeColor=BORDER, fillColor=HexColor("#0F172A")))
                if sc > 0:
                    bar_drawing.add(Rect(0, 2, 3.8 * inch * sc / 100, 5, strokeColor=None, fillColor=HexColor(clr)))
                owasp_rows.append([bar_drawing, ""])
                ot = Table(owasp_rows, colWidths=[2.8 * inch, 0.8 * inch])
                ot.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (0, 0), 1),
                    ("TOPPADDING", (0, 0), (0, 0), 1),
                    ("LEFTPADDING", (0, 0), (0, 0), 2),
                ]))
                elements.append(ot)
                elements.append(Spacer(1, 3))

        elements.append(PageBreak())

        # ===== VULNERABILITY FINDINGS =====
        elements.append(Paragraph("Vulnerability Findings", s_h1))
        elements.append(Spacer(1, 6))

        if total_failed == 0:
            elements.append(Paragraph("All scenarios passed. No vulnerabilities detected.", s_body))
        else:
            for sname, sresults in scenario_groups.items():
                passed = sum(1 for r in sresults if r.passed)
                total = len(sresults)
                pct = round(passed / total * 100) if total else 0
                if passed == total:
                    continue

                meta = SCENARIO_METADATA.get(sname, {})
                label = meta.get("label", sname.replace("_", " ").title())
                owasp = meta.get("owasp_category", SCENARIO_OWASP_MAP.get(sname, ""))
                severity = meta.get("severity_label", "Medium")
                sev_color = SEVERITY_COLORS.get(severity, "#F59E0B")
                desc = meta.get("description", "Security vulnerability detected.")
                mitigation = meta.get("mitigation", "Review agent configuration and security controls.")

                block = []

                block.append(Paragraph(
                    f"<b>{label}</b> &nbsp; "
                    f"<font color='#64748B' size='7'>{owasp}</font>",
                    s_h2,
                ))

                severity_data = [
                    [Paragraph(f"<b>Severity</b>", ParagraphStyle("SevLabel", fontSize=8, leading=10, textColor=TEXT_MUTED)),
                     Paragraph(f"<font color='{sev_color}'><b>⬤ {severity}</b></font>", ParagraphStyle("SevVal", fontSize=8, leading=10, textColor=TEXT_SECONDARY))],
                    [Paragraph(f"<b>Pass Rate</b>", ParagraphStyle("SevLabel", fontSize=8, leading=10, textColor=TEXT_MUTED)),
                     Paragraph(f"<font color='{_risk_color(pct)}'><b>{passed}/{total} ({pct}%)</b></font>", ParagraphStyle("SevVal", fontSize=8, leading=10, textColor=TEXT_SECONDARY))],
                ]
                sev_t = Table(severity_data, colWidths=[1 * inch, 2.2 * inch])
                sev_t.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]))
                block.append(sev_t)

                bar_d = Drawing(4 * inch, 8)
                bar_d.add(Rect(0, 2, 4 * inch, 5, strokeColor=BORDER, fillColor=DARK_BG))
                if pct > 0:
                    bar_d.add(Rect(0, 2, 4 * inch * pct / 100, 5, strokeColor=None, fillColor=HexColor(_risk_color(pct))))
                block.append(bar_d)
                block.append(Spacer(1, 3))

                block.append(Paragraph(f"<b>Description:</b> {desc}", s_body))
                block.append(Spacer(1, 2))

                fail_iters = [r for r in sresults if not r.passed]
                if fail_iters:
                    block.append(Paragraph("<b>Failed Iterations:</b>", s_small))
                    iter_data = [[
                        Paragraph("<b>Iter</b>", s_small),
                        Paragraph("<b>Payload</b>", s_small),
                    ]]
                    for r in fail_iters:
                        payload = (r.payload_used or "")[:120]
                        if len(payload or "") > 120:
                            payload = payload[:117] + "..."
                        iter_data.append([
                            Paragraph(str(r.iteration), s_label_center),
                            Paragraph((payload or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), s_small),
                        ])
                    it = Table(iter_data, colWidths=[0.4 * inch, 4.3 * inch])
                    it.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), CARD_BG),
                        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_SECONDARY),
                        ("ALIGN", (0, 0), (0, -1), "CENTER"),
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                        ("TOPPADDING", (0, 0), (-1, -1), 2),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]))
                    block.append(it)

                block.append(Spacer(1, 4))
                block.append(Paragraph(f"<b>Mitigation:</b> {mitigation}", ParagraphStyle("Mitigation", fontSize=8.5, leading=12, textColor=HexColor("#22C55E"), spaceBefore=2)))
                block.append(Spacer(1, 12))

                elements.append(KeepTogether(block))

            # Also list passing scenarios briefly
            passing = [(s, r) for s, r in scenario_groups.items() if sum(1 for x in r if x.passed) == len(r)]
            if passing:
                elements.append(Spacer(1, 8))
                elements.append(Paragraph("Passed Scenarios", s_h2))
                for sname, sresults in passing:
                    meta = SCENARIO_METADATA.get(sname, {})
                    label = meta.get("label", sname.replace("_", " ").title())
                    owasp_tag = meta.get("owasp_category", "")
                    elements.append(Paragraph(
                        f"✔ {label} &nbsp; <font color='#64748B' size='7'>{owasp_tag}</font>"
                        f" &nbsp; <font color='#22C55E'>(all {len(sresults)} passed)</font>",
                        s_body,
                    ))

        elements.append(PageBreak())

        # ===== APPENDIX: SCAN CONFIGURATION =====
        elements.append(Paragraph("Appendix: Scan Configuration", s_h1))
        elements.append(Spacer(1, 6))

        config_items = [
            ["Scan ID", f"#{scan.id}"],
            ["Provider", scan.provider or "-"],
            ["Agent Type", scan.agent_type or "-"],
            ["Iterations", str(scan.iterations)],
            ["Total Tests", str(total_tests)],
            ["Created", scan.created_at.strftime("%Y-%m-%d %H:%M UTC") if scan.created_at else "-"],
            ["Report Generated", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")],
        ]
        if scan.system_prompt:
            config_items.append(["System Prompt", scan.system_prompt])

        ct = Table(config_items, colWidths=[1.5 * inch, 4.2 * inch])
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), CARD_BG),
            ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_SECONDARY),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(ct)
        elements.append(Spacer(1, 20))

        elements.append(Paragraph(
            "Sentra - AI Agent Security Platform &nbsp;|&nbsp; CONFIDENTIAL",
            ParagraphStyle("FooterText", fontSize=7, leading=10, textColor=TEXT_MUTED, alignment=TA_CENTER),
        ))

        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            topMargin=margin, bottomMargin=margin,
            leftMargin=margin, rightMargin=margin,
        )
        doc.build(elements)
        return buf.getvalue()

    except ImportError as e:
        raise RuntimeError("PDF generation requires reportlab") from e
    except Exception as e:
        raise RuntimeError(f"PDF generation error: {e}") from e
