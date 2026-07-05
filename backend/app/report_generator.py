import io
from datetime import datetime

from app.models import Scan, TestResult
from app.scoring.calculator import SCENARIO_OWASP_MAP


def generate_pdf(scan: Scan, results: list[TestResult]) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch, mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, PageTemplate, Frame, BaseDocTemplate,
        )
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

        buf = io.BytesIO()

        class ReportDoc(BaseDocTemplate):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                frame = Frame(
                    self.leftMargin, self.bottomMargin,
                    self.width, self.height,
                    id="normal",
                )
                self.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=self.add_footer)])

            def add_footer(self, canvas, doc):
                canvas.saveState()
                canvas.setStrokeColor(HexColor("#1E293B"))
                canvas.setLineWidth(0.5)
                canvas.line(self.leftMargin, 0.6 * inch, self.width + self.leftMargin, 0.6 * inch)
                canvas.setFont("Helvetica", 7)
                canvas.setFillColor(HexColor("#64748B"))
                canvas.drawString(self.leftMargin, 0.45 * inch, "Sentra — AI Agent Security Platform")
                canvas.drawRightString(self.width + self.leftMargin, 0.45 * inch, f"Page {doc.page}")
                canvas.restoreState()

        doc = ReportDoc(
            buf, pagesize=A4,
            topMargin=0.8 * inch,
            bottomMargin=0.9 * inch,
            leftMargin=0.7 * inch,
            rightMargin=0.7 * inch,
        )

        styles = getSampleStyleSheet()
        primary = HexColor("#06B6D4")
        dark_bg = HexColor("#1E293B")
        text_primary = HexColor("#F1F5F9")
        text_secondary = HexColor("#94A3B8")
        text_muted = HexColor("#64748B")

        title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=20, spaceAfter=2, textColor=primary)
        heading_style = ParagraphStyle("Heading2", parent=styles["Heading2"], fontSize=13, spaceAfter=6, spaceBefore=4, textColor=text_primary)
        subheading_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=10, spaceAfter=4, textColor=text_secondary)
        normal_style = ParagraphStyle("Normal2", parent=styles["Normal"], fontSize=8.5, leading=11, textColor=text_secondary)
        small_style = ParagraphStyle("Small", parent=styles["Normal"], fontSize=7.5, leading=10, textColor=text_muted)
        score_style = ParagraphStyle("Score", parent=styles["Normal"], fontSize=32, leading=36, textColor=primary, alignment=TA_CENTER)
        risk_style = ParagraphStyle("Risk", parent=styles["Normal"], fontSize=11, leading=14, alignment=TA_CENTER)
        label_center = ParagraphStyle("LC", parent=styles["Normal"], fontSize=7.5, textColor=text_muted, alignment=TA_CENTER)

        elements = []

        score = scan.score
        score_display = f"{score:.0f}" if score is not None else "—"
        risk_label = "Low Risk" if score is not None and score >= 80 else "Moderate Risk" if score is not None and score >= 50 else "High Risk"
        risk_color = "#22C55E" if score is not None and score >= 80 else "#F59E0B" if score is not None and score >= 50 else "#EF4444"

        pass_count = sum(1 for r in results if r.passed) if results else 0
        total_tests = len(results) if results else 0

        # ── Header ──
        elements.append(Paragraph("Sentra Security Report", title_style))
        elements.append(Paragraph(f"Scan #{scan.id} — {scan.provider or scan.agent_type} agent", subheading_style))
        elements.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  |  {total_tests} tests across {scan.iterations} iterations", small_style))
        elements.append(Spacer(1, 8))
        elements.append(Table(
            [["", "", ""]],
            colWidths=[doc.width / 3.0] * 3,
            style=TableStyle([("LINEBELOW", (0, 0), (-1, 0), 1, HexColor("#1E293B"))]),
        ))
        elements.append(Spacer(1, 14))

        # ── Score Card ──
        score_data = [
            [Paragraph(score_display, score_style)],
            [Paragraph(f"<font color='{risk_color}'>{risk_label}</font>", risk_style)],
            [Paragraph(f"{pass_count}/{total_tests} tests passed", label_center)],
        ]
        score_table = Table(score_data, colWidths=[2.8 * inch])
        score_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#1E293B")),
            ("TOPPADDING", (0, 0), (0, 0), 10),
            ("BOTTOMPADDING", (0, 0), (0, 0), 4),
            ("TOPPADDING", (0, 1), (0, 1), 0),
            ("BOTTOMPADDING", (0, 1), (0, 1), 4),
            ("TOPPADDING", (0, 2), (0, 2), 0),
            ("BOTTOMPADDING", (0, 2), (0, 2), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 16),
            ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 16))

        # ── Summary Info ──
        summary_data = [
            [Paragraph("<b>Metric</b>", small_style), Paragraph("<b>Value</b>", small_style)],
            [Paragraph("Agent Type", normal_style), Paragraph(scan.provider or scan.agent_type or "—", normal_style)],
            [Paragraph("Iterations per Scenario", normal_style), Paragraph(str(scan.iterations), normal_style)],
            [Paragraph("Total Tests", normal_style), Paragraph(str(total_tests), normal_style)],
            [Paragraph("Scenarios Tested", normal_style), Paragraph(str(len(set(r.scenario_name for r in results)) if results else 0), normal_style)],
        ]
        if scan.system_prompt:
            prompt = scan.system_prompt[:80] + "..." if len(scan.system_prompt) > 80 else scan.system_prompt
            summary_data.append([Paragraph("System Prompt", normal_style), Paragraph(prompt, normal_style)])

        st = Table(summary_data, colWidths=[2.2 * inch, 3.5 * inch])
        st.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E293B")),
            ("TEXTCOLOR", (0, 0), (-1, -1), text_primary),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#1E293B")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(st)
        elements.append(Spacer(1, 16))

        # ── OWASP Breakdown ──
        if scan.owasp_breakdown:
            elements.append(Paragraph("OWASP Risk Breakdown", heading_style))
            owasp_header = [Paragraph("<b>Category</b>", small_style), Paragraph("<b>Score</b>", small_style)]
            owasp_rows = [owasp_header]
            for cat, sc in scan.owasp_breakdown.items():
                sc_color = "#22C55E" if sc >= 80 else "#F59E0B" if sc >= 50 else "#EF4444"
                owasp_rows.append([
                    Paragraph(cat, normal_style),
                    Paragraph(f"<font color='{sc_color}'>{sc:.1f}%</font>", normal_style),
                ])
            ot = Table(owasp_rows, colWidths=[4 * inch, 1.5 * inch])
            ot.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E293B")),
                ("TEXTCOLOR", (0, 0), (-1, -1), text_primary),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#1E293B")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(ot)
            elements.append(Spacer(1, 16))

        # ── Attack Details ──
        if results:
            elements.append(Paragraph("Attack Details", heading_style))
            scenario_groups = {}
            for r in results:
                scenario_groups.setdefault(r.scenario_name, []).append(r)

            for sname, sresults in scenario_groups.items():
                passed = sum(1 for r in sresults if r.passed)
                total = len(sresults)
                pct = round(passed / total * 100) if total else 0
                pct_color = "#22C55E" if pct >= 80 else "#F59E0B" if pct >= 50 else "#EF4444"

                owasp_tag = SCENARIO_OWASP_MAP.get(sname, "Uncategorized")
                elements.append(Paragraph(
                    f"<b>{sname.replace('_', ' ').title()}</b>  &nbsp;"
                    f"<font color='{pct_color}'>({passed}/{total} passed, {pct}%)</font>  &nbsp;"
                    f"<font color='#64748B'>[{owasp_tag}]</font>",
                    subheading_style,
                ))
                elements.append(Spacer(1, 3))

                detail_header = [
                    Paragraph("<b>Iteration</b>", small_style),
                    Paragraph("<b>Result</b>", small_style),
                    Paragraph("<b>Payload Used</b>", small_style),
                ]
                detail_rows = [detail_header]
                for r in sresults:
                    result_text = f"<font color='#22C55E'>PASS</font>" if r.passed else f"<font color='#EF4444'>FAIL</font>"
                    payload = r.payload_used or ""
                    if len(payload) > 100:
                        payload = payload[:97] + "..."
                    detail_rows.append([
                        Paragraph(str(r.iteration), label_center),
                        Paragraph(result_text, label_center),
                        Paragraph(payload.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), small_style),
                    ])

                dt = Table(detail_rows, colWidths=[0.6 * inch, 0.6 * inch, 4.5 * inch])
                dt.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E293B")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), text_primary),
                    ("ALIGN", (0, 0), (1, -1), "CENTER"),
                    ("ALIGN", (2, 1), (2, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#1E293B")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]))
                elements.append(dt)
                elements.append(Spacer(1, 10))

        # ── Footer close ──
        elements.append(Spacer(1, 8))
        elements.append(Table(
            [["", "", ""]],
            colWidths=[doc.width / 3.0] * 3,
            style=TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1, HexColor("#1E293B"))]),
        ))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph("Sentra — AI Agent Security Platform &nbsp;|&nbsp; sentra.7.jugaar.ai", small_style))

        doc.build(elements)
        return buf.getvalue()
    except ImportError as e:
        raise RuntimeError("PDF generation requires reportlab") from e
    except Exception as e:
        raise RuntimeError(f"PDF generation error: {e}") from e
