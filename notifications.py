import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def is_email_configured():
    """Check if email configuration is available"""
    required_vars = ['FROM_EMAIL', 'SMTP_SERVER', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'TO_EMAIL']
    return all(os.getenv(var) for var in required_vars)


def send_email(to_email, subject, body):
    """Send email notification"""
    # Check if email is configured
    if not is_email_configured():
        print("\n[EMAIL NOT CONFIGURED - Message would have been sent]")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("-" * 50)
        return
    
    try:
        from_email = os.getenv('FROM_EMAIL')
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        username = os.getenv('SMTP_USERNAME')
        password = os.getenv('SMTP_PASSWORD')
        
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")


def notify_error(error_msg, objective_name):
    """Send error notification"""
    subject = f"Automation Error: {objective_name}"
    body = f"""
Automation Error Report

Objective: {objective_name}
Error: {error_msg}
Timestamp: {datetime.now()}
    """
    
    to_email = os.getenv('TO_EMAIL')
    send_email(to_email, subject, body)


def notify_unsupported(unsupported_objectives):
    """Notify about unsupported objectives"""
    subject = "Unsupported Automation Objectives"
    body = "The following objectives are not supported:\n\n"
    
    for obj in unsupported_objectives:
        body += f"- {obj['name']}: {obj.get('reason', 'Unknown')}\n"
    
    to_email = os.getenv('TO_EMAIL')
    send_email(to_email, subject, body)

