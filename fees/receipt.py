
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def generate_fee_receipt(payment):

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Title'],
        textColor=colors.HexColor('#172554'),
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=10
    )

    normal_style = styles['Normal']

    elements = []

    elements.append(
        Paragraph("STUDENT FEE MANAGEMENT SYSTEM", title_style)
    )

    elements.append(
        Paragraph("OFFICIAL FEE PAYMENT RECEIPT",
                  ParagraphStyle(
                      'Subtitle',
                      parent=normal_style,
                      alignment=TA_CENTER,
                      textColor=colors.HexColor('#2563eb')
                  ))
    )

    elements.append(Spacer(1, 30))

    student = payment.student

    receipt_data = [
        ["Receipt Number", f"FEE-{payment.id:05d}"],
        ["Student ID", student.student_id],
        ["Student Name", student.user.get_full_name() or student.user.username],
        ["Course", student.course.course_name],
        ["Payment Date", str(payment.payment_date)],
        ["Payment Mode", payment.payment_mode],
        ["Transaction ID", payment.transaction_id or "N/A"],
        ["Amount Paid", f"Rs. {payment.amount}"],
    ]

    table = Table(
        receipt_data,
        colWidths=[170, 300],
        rowHeights=35
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eff6ff')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#172554')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, -1), (1, -1), colors.HexColor('#dcfce7')),
        ('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor('#166534')),
    ]))

    elements.append(table)

    elements.append(Spacer(1, 40))

    elements.append(
        Paragraph(
            "Thank you for your payment!",
            ParagraphStyle(
                'ThankYou',
                parent=normal_style,
                alignment=TA_CENTER,
                fontSize=13,
                textColor=colors.HexColor('#166534')
            )
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "This is a computer-generated receipt.",
            ParagraphStyle(
                'Footer',
                parent=normal_style,
                alignment=TA_CENTER,
                fontSize=9,
                textColor=colors.grey
            )
        )
    )

    pdf.build(elements)

    buffer.seek(0)

    return buffer
