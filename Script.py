import imaplib
import email
from email.header import decode_header
from datetime import datetime
import pytz
from database import setup_database, insert_tracking
try:
    import config
except ImportError:
    raise Exception("Please create a config.py file with EMAIL, PASSWORD, and SENDER_EMAIL variables")

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
        imap.select("Processed")
        _, processed_messages = imap.search(None, f'FROM "{sender_email}"')
        processed_ids = set(msg.decode().split()[-1] for msg in processed_messages)
        
        # Then process inbox
        imap.select("INBOX")
        _, messages = imap.search(None, f'FROM "{sender_email}"')
        
        for email_id in messages[0].split():
            if email_id in processed_ids:
                print(f"Skipping already processed email {email_id}")
                continue
                
            try:
                _, msg_data = imap.fetch(email_id, "(RFC822)")
                email_message = email.message_from_bytes(msg_data[0][1])
                
                # Extract date from email
                date_tuple = email.utils.parsedate_tz(email_message['Date'])
                date = email.utils.formatdate(email.utils.mktime_tz(date_tuple))
                
                # Get email content
                if email_message.is_multipart():
                    body = next((part.get_payload(decode=True).decode('utf-8', errors='replace')
                               for part in email_message.walk()
                               if part.get_content_type() == "text/plain"), None)
                else:
                    body = email_message.get_payload(decode=True).decode('utf-8', errors='replace')
                
                if body:
                    tracking_info = extract_tracking_info(body, date)
                    for info in tracking_info:
                        # Save to database
                        insert_tracking(info)
                        print(f"Saved to database: {info}")
                    
                # Move to processed folder
                imap.copy(email_id, "Processed")
                imap.store(email_id, '+FLAGS', '\\Deleted')
            
            except Exception as e:
                print(f"Error processing email {email_id}: {str(e)}")
        
        imap.expunge()
        imap.logout()
        
    except Exception as e:
        raise Exception(f"Failed to process emails: {str(e)}")

if __name__ == "__main__":
    read_emails_from_sender(config.EMAIL, config.PASSWORD, config.SENDER_EMAIL)
