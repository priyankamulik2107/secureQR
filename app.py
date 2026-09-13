from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import qrcode
import os
import cv2

app = Flask(__name__)

# Create encryption key
KEY_FILE = "secret.key"

if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()

    with open(KEY_FILE, "wb") as file:
        file.write(key)
else:
    with open(KEY_FILE, "rb") as file:
        key = file.read()

# Create cipher
cipher = Fernet(key)


@app.route("/", methods=["GET", "POST"])
def home():

    qr_image = None
    decrypted_message = None

    if request.method == "POST":

        action = request.form.get("action")

        
        # GENERATE QR CODE
        
        if action == "generate":

            message = request.form.get("message")

            # Encrypt message
            encrypted_message = cipher.encrypt(
                message.encode()
            )

            # Generate QR Code
            img = qrcode.make(
                encrypted_message.decode()
            )

            # Save QR Code
            qr_path = os.path.join(
                "static",
                "qr_code.png"
            )

            img.save(qr_path)

            qr_image = "qr_code.png"

        
        # SCAN AND DECRYPT QR CODE

        elif action == "decrypt":

            qr_file = request.files.get("qr_file")

            if qr_file:

                # Save uploaded QR image
                upload_path = os.path.join(
                    "static",
                    "uploaded_qr.png"
                )

                qr_file.save(upload_path)

                # Read image
                image = cv2.imread(upload_path)

                # Create QR detector
                detector = cv2.QRCodeDetector()

                # Detect and read QR code
                encrypted_data, points, _ = (
                    detector.detectAndDecode(image)
                )

                # Decrypt message
                if encrypted_data:

                    decrypted_message = cipher.decrypt(
                        encrypted_data.encode()
                    ).decode()

    return render_template(
        "index.html",
        qr_image=qr_image,
        decrypted_message=decrypted_message
    )


if __name__ == "__main__":
    app.run(debug=True)