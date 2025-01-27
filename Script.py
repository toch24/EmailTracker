import imaplib
import email
from email.header import decode_header
from datetime import datetime
import pytz
from database import setup_database, insert_tracking
import time
import logging
from notification import send_error_notification
try:
    import config
except ImportError:
    raise Exception("Please create a config.py file with EMAIL, PASSWORD, and SENDER_EMAIL variables")

# Set up logging
logging.basicConfig(
    filename='email_tracker.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def connect_to_gmail(email_address, password):
    """Connect to Gmail using IMAP."""
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(email_address, password)
    return imap

def extract_tracking_info(body, date):
    """Extract tracking numbers, weight, and price from email body."""
    lines = body.split('\n')
    tracking_numbers = []
    collecting_tracking = False
    
    for line in lines:
        line = line.strip()
        if 'Numero de Tracking' in line:
            collecting_tracking = True
            continue
        
        if not collecting_tracking:
            continue
            
        parts = line.split()
        if len(parts) >= 2 and parts[-2].isdigit() and '.' in parts[-1]:
            return [{
                'Date': date,
                'Tracking_Numbers': ' '.join(tracking_numbers + parts[:-2]),
                'Weight': parts[-2],
                'Price': parts[-1]
            }]
        tracking_numbers.extend(parts)
    
    raise ValueError("Failed to extract complete tracking information from email")

def read_emails_from_sender(email_address, password, sender_email):
    """Read emails from a specific sender and extract tracking information."""
    try:
        # Setup database first
        setup_database()
        
        imap = connect_to_gmail(email_address, password)
        
        # First, check if there are any already-processed emails
        try:
            imap.select("Processed")
        except:
            # If Processed folder doesn't exist, create it
            imap.create("Processed")
            imap.select("Processed")
            
        _, processed_messages = imap.search(None, f'FROM "{sender_email}" LABEL "Facturacion"')
        processed_ids = set()
        if processed_messages[0]:  # Only process if there are messages
            processed_ids = set(msg.decode() for msg in processed_messages[0].split())
        
        # Then process inbox with both sender and label criteria
        imap.select("INBOX")
        search_criteria = f'FROM "{sender_email}" LABEL "Facturacion"'
        _, messages = imap.search(None, search_criteria)
        
        if not messages[0]:  # No messages found
            logging.info(f"No new messages found matching criteria: {search_criteria}")
            imap.logout()
            return
            
        for email_id in messages[0].split():
            email_id = email_id.decode()
            if email_id in processed_ids:
                logging.info(f"Skipping already processed email {email_id}")
                continue
                
            try:
                _, msg_data = imap.fetch(email_id, "(RFC822)")
                email_message = email.message_from_bytes(msg_data[0][1])
                
                # Extract date from email
                date_tuple = email.utils.parsedate_tz(email_message['Date'])
                if not date_tuple:
                    logging.warning(f"Could not parse date for email {email_id}")
                    continue
                    
                date = email.utils.formatdate(email.utils.mktime_tz(date_tuple))
                
                # Get email content
                if email_message.is_multipart():
                    body = next((part.get_payload(decode=True).decode('utf-8', errors='replace')
                               for part in email_message.walk()
                               if part.get_content_type() == "text/plain"), None)
                else:
                    body = email_message.get_payload(decode=True).decode('utf-8', errors='replace')
                
                if not body:
                    logging.warning(f"No text content found in email {email_id}")
                    continue
                    
                tracking_info = extract_tracking_info(body, date)
                for info in tracking_info:
                    # Save to database
                    insert_tracking(info)
                    logging.info(f"Saved to database: {info}")
                    
                # Move to processed folder
                imap.copy(email_id, "Processed")
                imap.store(email_id, '+FLAGS', '\\Deleted')
                logging.info(f"Processed and moved email {email_id}")
            
            except Exception as e:
                logging.error(f"Error processing email {email_id}: {str(e)}")
                continue
        
        imap.expunge()
        imap.logout()
        logging.info("Email processing completed successfully")
        
    except Exception as e:
        logging.error(f"Failed to process emails: {str(e)}")
        raise

def main_loop():
    """Main loop to continuously check for new emails"""
    # Setup database on startup
    setup_database()
    logging.info("Database initialized")

    while True:
        try:
            # Your email credentials should be loaded from environment variables
            email_address = config.EMAIL
            password = config.PASSWORD
            sender_email = config.SENDER_EMAIL
            
            # Process emails
            read_emails_from_sender(email_address, password, sender_email)
            
            # Log success
            logging.info("Successfully processed emails")
            
            # Wait for 5 minutes before next check
            time.sleep(300)  # 300 seconds = 5 minutes
            
        except Exception as e:
            error_msg = f"Error in main loop: {str(e)}"
            logging.error(error_msg)
            send_error_notification(error_msg, email_address, password)
            time.sleep(60)

if __name__ == "__main__":
    logging.info("Starting Email Tracking Service")
    main_loop()
