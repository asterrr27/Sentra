import io
from datetime import datetime

from app.models import Scan, TestResult


def generate_pdf(scan: Scan, results: list[TestResult]) -> bytes:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib import colors

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=0.8 * inch, bottomMargin=0.8 * inch)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=22, spaceAfter=6, textColor=HexColor("#06B6D4"))
        heading_style = ParagraphStyle("Heading2", parent=styles["Heading2"], fontSize=14, spaceAfter=8, textColor=HexColor("#E2E8F0"))
        normal_style = ParagraphStyle("Normal2", parent=styles["Normal"], fontSize=9, leading=13, textColor=HexColor("#94A3B8"))
        score_style = ParagraphStyle("Score", parent=styles["Normal"], fontSize=36, leading=40, textColor=HexColor("#06B6D4"), alignment=1)
        label_style = ParagraphStyle("Label", parent=styles["Normal"], fontSize=8, textColor=HexColor("#64748B"), alignment=1)

        elements = []

        elements.append(Paragraph("Sentra Security Report", title_style))
        elements.append(Paragraph(f"Scan #{scan.id} — {scan.provider or scan.agent_type} agent", label_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", label_style))
        elements.append(Spacer(1, 6))
        elements.append(HRFlowable(width="100%", thickness=1, color=HexColor("#1E293B")))
        elements.append(Spacer(1, 12))

        score_display = f"{scan.score:.0f}" if scan.score is not None else "—"
        elements.append(Paragraph(score_display, score_style))
        risk_label = "Low Risk" if scan.score and scan.score >= 80 else "Moderate Risk" if scan.score and scan.score >= 50 else "High Risk"
        risk_color = "#22C55E" if scan.score and scan.score >= 80 else "#F59E0B" if scan.score and scan.score >= 50 else "#EF4444"
        elements.append(Paragraph(f"<font color='{risk_color}'>{risk_label}</font>", ParagraphStyle("Risk", parent=label_style, fontSize=12)))
        elements.append(Paragraph(f"{scan.iterations} iterations", label_style))
        elements.append(Spacer(1, 12))
        elements.append(HRFlowable(width="100%", thickness=1, color=HexColor("#1E293B")))
        elements.append(Spacer(1, 12))

        if scan.owasp_breakdown:
            elements.append(Paragraph("OWASP Risk Breakdown", heading_style))
            owasp_data = [[Paragraph("<b>Category</b>", normal_style), Paragraph("<b>Score</b>", normal_style)]]
            for cat, score in scan.owasp_breakdown.items():
                owasp_data.append([Paragraph(cat, normal_style), Paragraph(f"{score:.1f}%", normal_style)])
            t = Table(owasp_data, colWidths=[4 * inch, 1.5 * inch])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E293B")),
                ("TEXTCOLOR", (0, 0), (-1, -1), HexColor("#E2E8F0")),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#1E293B")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 16))

        if results:
            elements.append(Paragraph("Attack Details", heading_style))
            scenario_groups = {}
            for r in results:
                scenario_groups.setdefault(r.scenario_name, []).append(r)

            for sname, sresults in scenario_groups.items():
                passed = sum(1 for r in sresults if r.passed)
                total = len(sresults)
                rate = f"{passed}/{total}"
                elements.append(Paragraph(f"<b>{sname.replace('_', ' ').title()}</b> — {rate} passed", normal_style))
                elements.append(Spacer(1, 4))

                table_data = [[Paragraph("<b>Iteration</b>", label_style), Paragraph("<b>Result</b>", label_style)]]
                for r in sresults:
                    result_text = f"<font color='#22C55E'>PASS</font>" if r.passed else f"<font color='#EF4444'>FAIL</font>"
                    table_data.append([Paragraph(str(r.iteration), label_style), Paragraph(result_text, label_style)])

                t = Table(table_data, colWidths=[1 * inch, 1.5 * inch])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E293B")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), HexColor("#E2E8F0")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#1E293B")),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 10))

        elements.append(HRFlowable(width="100%", thickness=1, color=HexColor("#1E293B")))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("Sentra — AI Agent Security Platform", label_style))
        elements.append(Paragraph("https://sentra.7.jugaar.ai", label_style))

        doc.build(elements)
        return buf.getvalue()
    except ImportError:
        return b"No PDF support (reportlab not installed)"
    except Exception as e:
        return f"PDF generation error: {e}".encode()
