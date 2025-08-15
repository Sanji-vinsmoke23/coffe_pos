from flask import Flask, render_template, request
import qrcode
import os
from datetime import datetime
import urllib.parse

app = Flask(__name__)

# Item prices and GST rates
ITEM_PRICES = {
    'Espresso': 80,
    'Latte': 120,
    'Cappuccino': 100,
    'Americano': 90,
    'Mocha': 130
}

ITEM_GST = {
    'Espresso': 5,
    'Latte': 5,
    'Cappuccino': 5,
    'Americano': 18,
    'Mocha': 18
}

# Generate UPI QR code
def generate_upi_qr(amount, upi_id):
    upi_url = f"upi://pay?pa={upi_id}&pn=SmartCafe&am={amount}&cu=INR"
    qr = qrcode.make(upi_url)
    qr_path = os.path.join("static", "qr.png")
    qr.save(qr_path)
    return qr_path

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        item = request.form.get('item')
        quantity = int(request.form.get('quantity'))
        price = float(request.form.get('price'))
        payment = request.form.get('payment')
        upi_id = request.form.get('upi_id')

        # Calculate billing
        base_amount = price * quantity
        gst_rate = ITEM_GST.get(item, 0)
        gst_amount = base_amount * gst_rate / 100
        total_amount = base_amount + gst_amount
        timestamp = datetime.now().strftime("%d-%b-%Y %I:%M %p")

        # Format bill summary
        bill_summary = f"""SmartCafe POS Bill
--------------------------
  Name: {name}
  Mobile: {mobile}
  Item: {item}
  Quantity: {quantity}
  Price per item: ₹{price}
  Payment Method: {payment}
  Time: {timestamp}
--------------------------
  Base Amount: ₹{base_amount:.2f}
  GST @ {gst_rate}%: ₹{gst_amount:.2f}
  Total Amount: ₹{total_amount:.2f}"""

        # Generate QR if UPI
        qr_path = None
        if payment == 'UPI' and upi_id:
            qr_path = generate_upi_qr(total_amount, upi_id)

        # WhatsApp link (fixed)
        mobile_number = mobile.replace("+", "").replace(" ", "")
        encoded_message = urllib.parse.quote(f"Hello {name}, your bill:\n{bill_summary}")
        whatsapp_url = f"https://wa.me/{mobile_number}?text={encoded_message}"

        return render_template('index.html', bill_summary=bill_summary, qr_path=qr_path, whatsapp_url=whatsapp_url)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)