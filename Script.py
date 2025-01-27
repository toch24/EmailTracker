import imaplib
import email
from email.header import decode_header
from datetime import datetime
import pytz
from database import setup_database, insert_tracking
import time
import logging

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
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(email_address, password)
        logging.info("Successfully connected to Gmail")
        return imap
    except Exception as e:
        logging.error(f"Failed to connect to Gmail: {str(e)}")
        raise

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
        # Connect to Gmail
        imap = connect_to_gmail(email_address, password)
        
        # Select INBOX
        status, messages = imap.select("INBOX")
        if status != 'OK':
            raise Exception(f"Failed to select INBOX: {messages}")
        
        logging.info("Successfully selected INBOX")
        
        # Search for emails from sender
        status, messages = imap.search(None, f'FROM "{sender_email}"')
        if status != 'OK':
            raise Exception(f"Failed to search emails: {messages}")
        
        email_ids = messages[0].split()
        logging.info(f"Found {len(email_ids)} emails to process")
        
        for email_id in email_ids:
            try:
                # Fetch email content
                status, msg_data = imap.fetch(email_id, "(RFC822)")
                if status != 'OK':
                    logging.error(f"Failed to fetch email {email_id}")
                    continue
                
                email_message = email.message_from_bytes(msg_data[0][1])
                
                # Extract date
                date_str = email_message['Date']
                date_tuple = email.utils.parsedate_tz(date_str)
                if date_tuple:
                    date = email.utils.formatdate(email.utils.mktime_tz(date_tuple))
                else:
                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Get email content
                body = None
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                            break
                else:
                    body = email_message.get_payload(decode=True).decode('utf-8', errors='replace')
                
                if body:
                    tracking_info = extract_tracking_info(body, date)
                    for info in tracking_info:
                        logging.info(f"Extracted tracking info: {info}")
                        insert_tracking(info)
                        print(f"Saved to database: {info}")
                    
                    # Move to processed folder
                    try:
                        imap.create('Processed')
                    except:
                        pass  # Folder might already exist
                    
                    status = imap.copy(email_id, 'Processed')
                    if status[0] == 'OK':
                        imap.store(email_id, '+FLAGS', '\\Deleted')
                        logging.info(f"Moved email {email_id} to Processed folder")
                    else:
                        logging.error(f"Failed to move email {email_id} to Processed folder")
                
            except Exception as e:
                logging.error(f"Error processing email {email_id}: {str(e)}")
                continue
        
        # Cleanup
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
            # Process emails
            read_emails_from_sender(config.EMAIL, config.PASSWORD, config.SENDER_EMAIL)
            
            # Wait for 5 minutes before next check
            logging.info("Waiting 5 minutes before next check...")
            time.sleep(300)
            
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            # Wait 1 minute before retry on error
            time.sleep(60)

if __name__ == "__main__":
    logging.info("Starting Email Tracking Service")
    main_loop()
