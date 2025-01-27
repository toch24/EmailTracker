import sqlite3
import logging

def setup_database():
    """Create the database and tables if they don't exist."""
    try:
        conn = sqlite3.connect('tracking_data.db')
        cursor = conn.cursor()
        
        # Create table for tracking data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracking_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                tracking_numbers TEXT,
                weight TEXT,
                price TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Database setup completed successfully")
        
    except Exception as e:
        logging.error(f"Database setup failed: {str(e)}")
        raise

def insert_tracking(data):
    """Insert tracking information into database."""
    try:
        conn = sqlite3.connect('tracking_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tracking_data (date, tracking_numbers, weight, price)
            VALUES (?, ?, ?, ?)
        ''', (data['Date'], data['Tracking_Numbers'], data['Weight'], data['Price']))
        
        conn.commit()
        conn.close()
        logging.info(f"Inserted tracking data: {data}")
        
    except Exception as e:
        logging.error(f"Failed to insert tracking data: {str(e)}")
        raise 