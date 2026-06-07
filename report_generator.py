# report_generator.py
"""
Generate a basic PDF mission report (reportlab).
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Dict

def generate_pdf_report(mission: Dict, path: str = "mission_report.pdf") -> str:
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, 800, "ELZF-AI Mission Report")
    c.setFont("Helvetica", 10)
    c.drawString(40, 780, f"Generated: {datetime.utcnow().isoformat()} UTC")
    c.drawString(40, 760, f"Start: {mission.get('start')}  Dest: {mission.get('dest')}")
    c.drawString(40, 740, f"Distance (m): {int(mission.get('distance',0))}  ETA (s): {int(mission.get('travel_time',0))}")
    y = 700
    for t in mission.get("telemetry", [])[:25]:
        c.drawString(40, y, f"t={t['t']:.1f}s lat={t['lat']:.5f} lon={t['lon']:.5f} alt={t['alt']:.0f}m")
        y -= 12
        if y < 40:
            c.showPage()
            y = 800
    c.save()
    return path