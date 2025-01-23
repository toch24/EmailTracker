import smtplib
from email.mime.text import MIMEText
import logging

# Set up logging
logging.basicConfig(
    filename='email_tracker.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_error_notification(error_message, sender_email, sender_password):
    """Send an error notification email."""
    try:
        # Create message
        msg = MIMEText(f"An error occurred in the email tracking service:\n\n{error_message}")
        msg['Subject'] = 'Email Tracking Service Error'
        msg['From'] = sender_email
        msg['To'] = sender_email  # Sending to self

        # Connect to Gmail SMTP
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        logging.info("Error notification sent successfully")
        
    except Exception as e:
        logging.error(f"Failed to send error notification: {str(e)}") 