# Email Tracking Script

This script automatically processes emails labeled as "Facturacion" from a specific sender and extracts tracking information, storing it in a SQLite database.

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
EMAIL_ADDRESS = "your.email@gmail.com"
EMAIL_PASSWORD = "your-16-digit-app-password" # The app password generated above
SENDER_EMAIL = "sender@example.com" # The email address you want to track

### 3. Email Requirements
The script will only process emails that meet both criteria:
- From the specified sender email address
- Labeled as "Facturacion" in Gmail

To label emails in Gmail:
1. Open Gmail
2. Select the email
3. Click the label icon (tag symbol)
4. Select "Facturacion" or create the label if it doesn't exist
5. You can also create a filter to automatically apply this label:
   - Click the search options (down arrow in search bar)
   - Enter the sender's email address
   - Click "Create filter"
   - Check "Apply the label" and select "Facturacion"
   - Click "Create filter"

### 3. Running the Script

#### For Windows Users:
1. Double click `run.bat`
2. If you get a security warning, click "More info" and then "Run anyway"
3. A terminal window will open and the script will start running

#### For Mac Users:
1. Open Terminal
   - Press Command + Space
   - Type "Terminal"
   - Press Enter
2. Navigate to script directory:
   ```bash
   cd path/to/script/folder
   ```
3. Make the script executable:
   ```bash
   chmod +x run.sh
   ```
4. Run the script:
   ```bash
   ./run.sh
   ```

### 4. Viewing the Database

#### For Windows:
1. Download DB Browser for SQLite: https://sqlitebrowser.org/dl/
2. Install and open DB Browser for SQLite
3. Click "Open Database"
4. Navigate to your script folder and select `tracking_data.db`

#### For Mac:
Option 1 - Using Homebrew:
bash
Install Homebrew first if you haven't
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
Then install DB Browser for SQLite
brew install --cask db-browser-for-sqlite

Option 2:
1. Download DB Browser for SQLite: https://sqlitebrowser.org/dl/
2. Open the downloaded .dmg file
3. Drag DB Browser for SQLite to Applications
4. Open DB Browser and select your `tracking_data.db` file

## Important Notes
- Never commit your `config.py` file to version control
- Make sure to add `config.py` to your `.gitignore`
- The script will create a `tracking_data.db` file automatically
- Logs will be written to `email_tracker.log`