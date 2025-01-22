import sqlite3
from datetime import datetime

def setup_database():
    """Create the database and tables"""
    conn = sqlite3.connect('tracking_data.db')
    cursor = conn.cursor()

    # Create tracking_info table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracking_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_date DATETIME,
            tracking_numbers TEXT,
            weight DECIMAL,
            price DECIMAL,
            processed_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def insert_tracking(tracking_data):
    """Insert a new tracking record"""
    conn = sqlite3.connect('tracking_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO tracking_info (email_date, tracking_numbers, weight, price)
        VALUES (?, ?, ?, ?)
    ''', (
        tracking_data['Date'],
        tracking_data['Tracking_Numbers'],
        float(tracking_data['Weight']),
        float(tracking_data['Price'].replace('$', ''))
    ))

    conn.commit()
    conn.close() 