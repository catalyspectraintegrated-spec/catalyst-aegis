"""
CATALYST AEGIS — Automated Reporting Engine
Generates and emails trade reports (daily, weekly, monthly)
"""

import json
import os
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
import io

TRADE_LOG_FILE = "trade_log.json"
REPORTS_DIR = "reports"

# ============================================================
# REPORT GENERATOR
# ============================================================
def load_trades():
    if os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, 'r') as f:
            return json.load(f).get("trades", [])
    return []

def generate_pdf_report(trades, period_name, start_date, end_date):
    """Generate a professional PDF report."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = f"{REPORTS_DIR}/Catalyst_Aegis_{period_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=A4,
                          rightMargin=0.5*inch, leftMargin=0.5*inch,
                          topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle('Title', fontSize=24, textColor=colors.HexColor('#D4A017'),
                                spaceAfter=6, alignment=1)
    elements.append(Paragraph("CATALYST AEGIS", title_style))
    elements.append(Paragraph(f"{period_name} Trade Report", styles['Heading2']))
    elements.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Summary metrics
    closed = [t for t in trades if t.get("status") == "closed"]
    wins = [t for t in closed if t.get("pnl", 0) > 0]
    losses = [t for t in closed if t.get("pnl", 0) <= 0]
    total_pnl = sum(t.get("pnl", 0) for t in closed)
    
    summary_data = [
        ["Metric", "Value"],
        ["Total Trades", str(len(closed))],
        ["Winning Trades", str(len(wins))],
        ["Losing Trades", str(len(losses))],
        ["Win Rate", f"{len(wins)/len(closed)*100:.1f}%" if closed else "N/A"],
        ["Total P&L", f"${total_pnl:+,.2f}"],
        ["Largest Win", f"${max([t.get('pnl',0) for t in wins]):+,.2f}" if wins else "N/A"],
        ["Largest Loss", f"${min([t.get('pnl',0) for t in losses]):+,.2f}" if losses else "N/A"],
        ["Average Win", f"${sum(t.get('pnl',0) for t in wins)/len(wins):+,.2f}" if wins else "N/A"],
        ["Average Loss", f"${sum(t.get('pnl',0) for t in losses)/len(losses):+,.2f}" if losses else "N/A"],
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A1628')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#D4A017')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F2F6')]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Trade details table
    elements.append(Paragraph("Trade Details", styles['Heading3']))
    
    if closed:
        trade_data = [["Entry Time", "Symbol", "Entry", "Exit", "P&L", "Result"]]
        for t in closed[-20:]:  # Last 20 trades
            pnl = t.get("pnl", 0)
            trade_data.append([
                t.get("entry_time", "")[:16],
                t.get("symbol", ""),
                f"{t.get('entry_price', ''):.5f}" if isinstance(t.get('entry_price'), float) else str(t.get('entry_price', '')),
                f"{t.get('exit_price', ''):.5f}" if isinstance(t.get('exit_price'), float) else str(t.get('exit_price', '')),
                f"${pnl:+,.2f}",
                "WIN" if pnl > 0 else "LOSS"
            ])
        
        trade_table = Table(trade_data, colWidths=[1.2*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.8*inch, 0.7*inch])
        trade_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A1628')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#D4A017')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(trade_table)
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle('Disclaimer', fontSize=7, textColor=colors.grey, alignment=1)
    elements.append(Paragraph("─" * 70, disclaimer_style))
    elements.append(Paragraph(
        "DISCLAIMER: This report is generated by Catalyst AEGIS, a product of Catalyspectra Integrated Solutions LTD. "
        "Past performance does not guarantee future results. Trading forex and cryptocurrencies involves substantial risk of loss. "
        "Catalyspectra Integrated Solutions LTD does not provide financial advice. All trading decisions are the sole responsibility "
        "of the account holder. By using this platform, you acknowledge that you may experience profits, losses, or outcomes in between. "
        "Catalyspectra Integrated Solutions LTD shall not be held liable for any trading losses incurred.",
        disclaimer_style
    ))
    elements.append(Paragraph(
        f"© {datetime.now().year} Catalyspectra Integrated Solutions LTD. All rights reserved. | Registered in Nigeria | Not financial advice.",
        disclaimer_style
    ))
    
    doc.build(elements)
    return filename

def generate_report(period="daily"):
    """Generate report for specified period."""
    trades = load_trades()
    if not trades:
        print(f"⚠️ No trades found. Skipping {period} report.")
        return None
    
    now = datetime.now()
    
    if period == "daily":
        start = now - timedelta(days=1)
        name = "Daily"
    elif period == "weekly":
        start = now - timedelta(weeks=1)
        name = "Weekly"
    elif period == "monthly":
        start = now - timedelta(days=30)
        name = "Monthly"
    else:
        start = now - timedelta(days=1)
        name = "Custom"
    
    end = now
    period_trades = [t for t in trades if start.strftime("%Y-%m-%d") <= t.get("entry_time", "")[:10] <= end.strftime("%Y-%m-%d")]
    
    if not period_trades:
        print(f"⚠️ No trades in {period} period. Skipping.")
        return None
    
    filename = generate_pdf_report(period_trades, name, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    print(f"✅ {name} report generated: {filename}")
    return filename

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("="*55)
    print("   CATALYST AEGIS — Report Generator")
    print("="*55)
    
    for period in ["daily", "weekly", "monthly"]:
        generate_report(period)
    
    print(f"\n📁 Reports saved in: {REPORTS_DIR}/")
    print("✅ Done.")
