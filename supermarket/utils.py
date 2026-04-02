# supermarket/utils.py
import qrcode
from io import BytesIO

def generate_promptpay_qr(amount, payee="0123456789"):
    """
    Generate a PromptPay QR code.

    :param amount: float, the amount to be paid
    :param payee: str, PromptPay ID (phone number or tax ID)
    :return: BytesIO buffer containing QR image
    """
    # PromptPay QR payload (simple version)
    payload = f"00020101021129370016A000000677010111{payee}5802TH6304"
    # Append amount in the format of XXXX.XX
    payload += f"{amount:.2f}".replace(".", "")  # e.g., 125.50 → "12550"

    # Calculate CRC (for production, use full PromptPay spec; simplified here)
    payload += "0000"

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer