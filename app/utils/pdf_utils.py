import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from config import Config

def generate_pdf_report(user, detections):
    os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)
    filename = f"report_{user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(Config.REPORTS_FOLDER, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('Title', parent=styles['Title'], textColor=colors.HexColor('#2e7d32'), fontSize=20)
    story.append(Paragraph("Crop Disease Detection Report", title_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Farmer: {user.username} | Email: {user.email}", styles['Normal']))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    story.append(Paragraph("Detection History", styles['Heading2']))
    data = [["#", "Date", "Disease", "Confidence", "Status"]]
    
    for i, det in enumerate(detections, 1):
        data.append([
            str(i),
            det.detected_at.strftime('%Y-%m-%d'),
            det.disease.name if det.disease else "Unknown",
            f"{det.confidence_score:.1%}" if det.confidence_score else "N/A",
            det.status.capitalize()
        ])
    
    table = Table(data, colWidths=[0.4*inch, 1.2*inch, 2.2*inch, 1.0*inch, 1.0*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f1f8e9')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(table)
    
    doc.build(story)
    return filename
