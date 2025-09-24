"""
PDF generation utilities for invoices and offers
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
from django.conf import settings
import os
from decimal import Decimal

# Register fonts for Bulgarian text support
FONT_NAME = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'

try:
    # Try to register DejaVu fonts with proper encoding
    font_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans.ttf',
    ]
    
    bold_font_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',
    ]
    
    # Try to register regular font
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('DejaVuSans', font_path, subfontIndex=0))
                FONT_NAME = 'DejaVuSans'
                print(f"Successfully registered DejaVuSans from {font_path}")
                break
        except Exception as e:
            print(f"Failed to register font from {font_path}: {e}")
            continue
    
    # Try to register bold font
    for font_path in bold_font_paths:
        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path, subfontIndex=0))
                FONT_BOLD = 'DejaVuSans-Bold'
                print(f"Successfully registered DejaVuSans-Bold from {font_path}")
                break
        except Exception as e:
            print(f"Failed to register bold font from {font_path}: {e}")
            continue
            
    if FONT_NAME == 'DejaVuSans':
        print("Using DejaVu fonts for Cyrillic support")
    else:
        print("Using Helvetica fonts as fallback")
        
except Exception as e:
    print(f"Font registration failed: {e}, using Helvetica fonts")
    # Use Helvetica as fallback - it should work for basic text


def safe_text(text):
    """Ensure text is properly encoded for PDF generation"""
    if text is None:
        return ""
    try:
        # Convert to string and clean it
        clean_text = str(text).strip()
        
        # Handle common encoding issues
        clean_text = clean_text.replace('\x00', '')  # Remove null bytes
        clean_text = clean_text.replace('\ufffd', '')  # Remove replacement characters
        clean_text = clean_text.replace('\u200b', '')  # Remove zero-width spaces
        
        # For Bulgarian text, ensure proper encoding
        if isinstance(clean_text, str):
            # Try to encode and decode to ensure it's valid UTF-8
            try:
                clean_text.encode('utf-8').decode('utf-8')
            except UnicodeError:
                # If UTF-8 fails, try to fix common issues
                clean_text = clean_text.encode('utf-8', errors='ignore').decode('utf-8')
        
        return clean_text
    except Exception as e:
        print(f"Text encoding error for '{text}': {e}")
        # Return a safe fallback
        return str(text).encode('ascii', 'ignore').decode('ascii') if text else ""


def generate_invoice_pdf(order):
    """Generate invoice PDF for an order"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=FONT_BOLD,
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph(safe_text("ФАКТУРА"), title_style))
    story.append(Spacer(1, 20))
    
    # Company information
    company_info = [
        [safe_text("Фирма:"), safe_text("АВТОЛАБОРАТОРИЯ ООД")],
        [safe_text("Адрес:"), safe_text("гр. СОФИЯ, ЖК. ТОЛСТОЙ, БЛ. 60, ЕТ. 4")],
        [safe_text("ЕИК:"), safe_text("203375580")],
        [safe_text("ДДС №:"), safe_text("BG203375580")],
        [safe_text("МОЛ:"), safe_text("ОГНЯН КОСТОВ")],
    ]
    
    company_table = Table(company_info, colWidths=[3*cm, 8*cm])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(company_table)
    story.append(Spacer(1, 20))
    
    # Order information
    story.append(Paragraph(safe_text("Информация за поръчката:"), heading_style))
    
    order_info = [
        [safe_text("Номер на фактурата:"), safe_text(order.order_number)],
        [safe_text("Дата:"), safe_text(order.order_date.strftime("%d.%m.%Y"))],
        [safe_text("Клиент:"), safe_text(order.client_name)],
        [safe_text("Адрес:"), safe_text(order.client_address or "Не е посочен")],
        [safe_text("Телефон:"), safe_text(order.client_phone or "Не е посочен")],
        [safe_text("Кола:"), safe_text(f"{order.car_brand_model} ({order.car_plate_number or 'Без рег. номер'})")],
        [safe_text("VIN:"), safe_text(order.car_vin or "Не е посочен")],
        [safe_text("Пробег:"), safe_text(f"{order.car_mileage} км" if order.car_mileage else "Не е посочен")],
    ]
    
    order_table = Table(order_info, colWidths=[5*cm, 8*cm])
    order_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(order_table)
    story.append(Spacer(1, 20))
    
    # Items table
    story.append(Paragraph(safe_text("Артикули и услуги:"), heading_style))
    
    # Prepare items data
    items_data = [[safe_text("№"), safe_text("Наименование"), safe_text("Мярка"), safe_text("Колич."), safe_text("Ед. цена"), safe_text("Общо без ДДС"), safe_text("ДДС 20%"), safe_text("Общо с ДДС")]]
    
    for i, item in enumerate(order.order_items.all(), 1):
        items_data.append([
            safe_text(str(i)),
            safe_text(item.name),
            safe_text(item.unit),
            safe_text(f"{item.quantity}"),
            safe_text(f"{item.purchase_price:.2f} лв."),
            safe_text(f"{item.total_price:.2f} лв."),
            safe_text(f"{item.total_price * Decimal('0.20'):.2f} лв."),
            safe_text(f"{item.total_price_with_vat:.2f} лв.")
        ])
    
    # Add totals
    items_data.append([safe_text(""), safe_text(""), safe_text(""), safe_text(""), safe_text(""), safe_text(""), safe_text(""), safe_text("")])
    items_data.append([
        safe_text(""),
        safe_text(""),
        safe_text(""),
        safe_text(""),
        safe_text("ОБЩО:"),
        safe_text(f"{order.total_without_vat:.2f} лв."),
        safe_text(f"{order.total_vat:.2f} лв."),
        safe_text(f"{order.total_with_vat:.2f} лв.")
    ])
    
    items_table = Table(items_data, colWidths=[0.8*cm, 6*cm, 1.2*cm, 1.2*cm, 2*cm, 3*cm, 2.5*cm, 2.5*cm])
    items_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('GRID', (0, -1), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
        ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 30))
    
    # Bank information
    story.append(Paragraph(safe_text("Банкова информация:"), heading_style))
    
    bank_info = [
        [safe_text("Банка:"), safe_text("УниКредит Булбанк АД")],
        [safe_text("IBAN:"), safe_text("BG18UNCR70001523123456")],
        [safe_text("BIC:"), safe_text("UNCRBGSF")],
        [safe_text("Получател:"), safe_text("Автосервиз Дейански")],
    ]
    
    bank_table = Table(bank_info, colWidths=[3*cm, 8*cm])
    bank_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(bank_table)
    story.append(Spacer(1, 20))
    
    # Notes
    if order.notes:
        story.append(Paragraph(safe_text("Забележки:"), heading_style))
        story.append(Paragraph(safe_text(order.notes), styles['Normal']))
    
    # Build PDF
    doc.build(story)
    return response


def generate_offer_pdf(order):
    """Generate offer PDF for an order"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="offer_{order.order_number}.pdf"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkgreen
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=FONT_BOLD,
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkgreen
    )
    
    # Create a normal style for table content
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        textColor=colors.black
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph(safe_text("ОФЕРТА"), title_style))
    story.append(Spacer(1, 20))
    
    # Company information
    company_info = [
        [safe_text("Фирма:"), safe_text("АВТОЛАБОРАТОРИЯ ООД")],
        [safe_text("Адрес:"), safe_text("гр. СОФИЯ, ЖК. ТОЛСТОЙ, БЛ. 60, ЕТ. 4")],
        [safe_text("ЕИК:"), safe_text("203375580")],
        [safe_text("ДДС №:"), safe_text("BG203375580")],
        [safe_text("МОЛ:"), safe_text("ОГНЯН КОСТОВ")],
    ]
    
    company_table = Table(company_info, colWidths=[3*cm, 8*cm])
    company_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(company_table)
    story.append(Spacer(1, 20))
    
    # Order information
    story.append(Paragraph(safe_text("Информация за офертата:"), heading_style))
    
    order_info = [
        [safe_text("Номер на офертата:"), safe_text(order.order_number)],
        [safe_text("Дата:"), safe_text(order.order_date.strftime("%d.%m.%Y"))],
        [safe_text("Клиент:"), safe_text(order.client_name)],
        [safe_text("Адрес:"), safe_text(order.client_address or "Не е посочен")],
        [safe_text("Телефон:"), safe_text(order.client_phone or "Не е посочен")],
        [safe_text("Кола:"), safe_text(f"{order.car_brand_model} ({order.car_plate_number or 'Без рег. номер'})")],
        [safe_text("VIN:"), safe_text(order.car_vin or "Не е посочен")],
        [safe_text("Пробег:"), safe_text(f"{order.car_mileage} км" if order.car_mileage else "Не е посочен")],
    ]
    
    order_table = Table(order_info, colWidths=[5*cm, 8*cm])
    order_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(order_table)
    story.append(Spacer(1, 20))
    
    # Items table
    story.append(Paragraph(safe_text("Артикули и услуги:"), heading_style))
    
    # Prepare items data
    items_data = [[safe_text("№"), safe_text("Наименование"), safe_text("Мярка"), safe_text("Колич."), safe_text("Ед. цена"), safe_text("Общо без ДДС"), safe_text("ДДС 20%"), safe_text("Общо с ДДС")]]
    
    for i, item in enumerate(order.order_items.all(), 1):
        items_data.append([
            safe_text(str(i)),
            safe_text(item.name),
            safe_text(item.unit),
            safe_text(f"{item.quantity}"),
            safe_text(f"{item.purchase_price:.2f} лв."),
            safe_text(f"{item.total_price:.2f} лв."),
            safe_text(f"{item.total_price * Decimal('0.20'):.2f} лв."),
            safe_text(f"{item.total_price_with_vat:.2f} лв.")
        ])
    
    # Add totals
    items_data.append([safe_text(""), safe_text(""), safe_text(""), safe_text(""), safe_text(""), safe_text(""), safe_text(""), safe_text("")])
    items_data.append([
        safe_text(""),
        safe_text(""),
        safe_text(""),
        safe_text(""),
        safe_text("ОБЩО:"),
        safe_text(f"{order.total_without_vat:.2f} лв."),
        safe_text(f"{order.total_vat:.2f} лв."),
        safe_text(f"{order.total_with_vat:.2f} лв.")
    ])
    
    items_table = Table(items_data, colWidths=[0.8*cm, 6*cm, 1.2*cm, 1.2*cm, 2*cm, 3*cm, 2.5*cm, 2.5*cm])
    items_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTNAME', (2, 0), (2, -1), FONT_NAME),
        ('FONTNAME', (3, 0), (3, -1), FONT_NAME),
        ('FONTNAME', (4, 0), (4, -1), FONT_NAME),
        ('FONTNAME', (5, 0), (5, -1), FONT_NAME),
        ('FONTNAME', (6, 0), (6, -1), FONT_NAME),
        ('FONTNAME', (7, 0), (7, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('GRID', (0, -1), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen),
        ('FONTNAME', (0, -1), (-1, -1), FONT_BOLD),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 30))
    
    # Notes
    if order.notes:
        story.append(Paragraph(safe_text("Забележки:"), heading_style))
        story.append(Paragraph(safe_text(order.notes), styles['Normal']))
    
    # Build PDF
    doc.build(story)
    return response
