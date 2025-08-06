from xhtml2pdf import pisa
from datetime import datetime
import os

def generate_pdf(customer, company, services, filename="invoice.pdf", start=None, end=None):
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    service_rows = ""
    total_amount = 0

    for idx, service in enumerate(services, start=1):
        comprehensive_type = 'Comprehensive' if service.comprehensive.lower() == 'yes' else 'Ordinary'
        amount = service.total_price
        total_amount += amount

        service_rows += f"""
        <tr>
            <td>{idx}</td>
            <td>
                {service.brand} {service.category} AMC CONTRACT<br>
                {service.amc_years} years {comprehensive_type} AMC with  {len(service.visits)} services.
            </td>
            <td>-</td>
            <td class="right">₹{service.base_price}</td>
            <td>{service.quantity}</td>
            <td class="right">₹{amount}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 12px; padding: 10px; }}
        .header, .footer {{ text-align: center; }}
        .title {{ font-size: 20px; font-weight: bold; margin-bottom: 5px; }}
        .subtitle {{ font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #000; padding: 5px; text-align: left; }}
        .right {{ text-align: right; }}
        .total {{ font-weight: bold; background-color: #f0f0f0; }}
        .signature {{ margin-top: 40px; float: right; text-align: center; }}
        .terms {{ font-size: 11px; line-height: 1.5; margin-top: 40px; }}
    </style>
    </head>
    <body>

    <div class="header">
      <
        <div class="title">{company['name']}</div>
        <div class="subtitle">
            Address: {company['address']}<br>
            Mobile: {company['phone']} | Email: {company['email']}
        </div>
    </div>

    <table style="margin-top: 20px;">
        <tr>
            <td>
                <strong>Customer Details:</strong><br>
                {customer['name']}<br>
                Billing Address:<br>
                {customer['address']}<br>
                Phone: {customer['phone']}<br>
                Email: {customer['email']}
            </td>
            <td>
                <strong>Invoice #:</strong> {invoice_number}<br>
                <strong>Date:</strong> {start.strftime('%d %b %Y') if start else '-'}<br>
                <strong>Due Date:</strong> {end.strftime('%d %b %Y') if end else '-'}
            </td>
        </tr>
    </table>

    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Item</th>
                <th>HSN/SAC</th>
                <th>Rate</th>
                <th>Qty</th>
                <th>Amount</th>
            </tr>
        </thead>
        <tbody>
            {service_rows}
        </tbody>
        <tfoot>
            <tr>
                <td colspan="5" class="right total">Total</td>
                <td class="right total">₹{total_amount}</td>
            </tr>
        </tfoot>
    </table>

    <div class="terms">
        <strong>Notes:</strong><br>
        Thank you for choosing SAI ENTERPRISES.<br><br>

        <strong>Terms & Conditions:</strong><br>
        1. Under this contract we undertake only services.<br>
        2. No visiting charge throughout the maintenance period.<br>
        3. Spare parts not included. If required, customer will pay for them.<br>
        4. Applicable in Mumbai/Thane/Dahisar region only.<br>
        5. Equipment will be checked before acceptance.<br>
        6. Inspection and service will be carried out within 24 hours.<br>
        7. Contract once placed will not be cancelled or refunded.<br><br>

        <em>Declaration:</em> I agree to all terms and conditions of the AMC Contract.
    </div>

    <div class="signature">
        Authorized Signatory<br>
        <strong>SAI ENTERPRISES</strong>
    </div>

    </body>
    </html>
    """

    with open(filename, "wb") as result_file:
        pisa.CreatePDF(html, dest=result_file)

    print(f"PDF generated successfully: {filename}")
