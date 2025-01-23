# Email Tracking Script

This script automatically processes emails, extracts tracking information, and stores it in a SQLite database.

## Setup Instructions

### 1. Create App Password for Gmail
1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to Security
3. Under "Signing in to Google," select "2-Step Verification"
4. At the bottom, select "App passwords"
5. Generate a new app password:
   - Select app: "Mail"
   - Select device: "Other (Custom name)"
   - Name it "Email Tracker"
6. Copy the 16-character password that appears

### 2. Configure Credentials
Create a `config.py` file in the project root:

### 3. Install Dependencies

### 4. Setup Database Viewer
On Ubuntu/Debian:
bash
sudo apt-get install sqlitebrowser

To view the database:
bash
sqlitebrowser tracking_data.db


### 5. Run the Script

## Important Notes
- Never commit your `config.py` file to version control
- Make sure to add `config.py` to your `.gitignore`
- The script will create a `tracking_data.db` file automatically
- Logs will be written to `email_tracker.log`

## Viewing the Database
Using DB Browser for SQLite (Recommended - GUI Tool):
Install on Ubuntu/Debian
sudo apt-get install sqlitebrowser

## For Mac Users
Install DB Browser for SQLite using Homebrew:
bash
Install Homebrew first if you haven't
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install DB Browser for SQLite
brew install --cask db-browser-for-sqlite
Or download directly from https://sqlitebrowser.org/dl/
