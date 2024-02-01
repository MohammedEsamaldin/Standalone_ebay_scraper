import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email_notification():
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "mohammedesam.mem@gmail.com"  # Add you Email here
    smtp_password = "upfi plbj ldyq khjb" # Add generated pass code here 
    sender_email = "mohammedesam.mem@gmail.com"  # Add you Email here
    receiver_email = "mohammedesam.mem@gmail.com"  # Add you Email here

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "Pipeline failure !!"

    body = """Dear Mohammed,\nThe pipeline scraper has been stop due some errors, one is that the user reached the limit of 5000/day.\nPlease login to the account of AWS and chaneged the user!! \nBest regards,\nNotification center."""
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email notification sent successfully.")
    except Exception as e:
        print(f"Failed to send email notification: {e}")
