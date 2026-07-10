# ABC Hospital - Secure Patient Portal

ABC Hospital is a secure, role-based web portal for patients, doctors, and medical staff. It allows users to register an account, verify their identity via a 6-digit email OTP (One-Time Password), set a password securely, login, and access a customized dashboard depending on their hospital role.

## Features
- **User Signup & Validation**: Generates and sends a 6-digit OTP to the registrant's email.
- **Secure Password Completion**: Users completes their profiles by creating a secure password (stored as SHA-256 hashes).
- **Role-Based Authentication**: Secure login validating credentials, verifying validation status, and assigning dashboard layouts tailored for patients, doctors, and staff.
- **Modern UI/UX**: Designed using a clean, interactive, and trustworthy teal color palette with hover animations and toast notifications.
- **GitHub Ready Security**: All sensitive database credentials and SMTP keys are loaded dynamically from environment variables, protected locally, and excluded from source control.

---

## Tech Stack
- **Backend**: Python 3 (Flask)
- **Database**: MySQL Server
- **Frontend**: Vanilla HTML5, Vanilla CSS3 (Custom design system), Vanilla JavaScript (ES6 fetch API)

---

## Prerequisites
Before running the application, make sure you have:
1. **Python 3.x** installed.
2. **MySQL Server** running locally.
3. A **Gmail account** (with an App Password enabled) if you wish to send real OTP verification emails.

---

## Installation & Setup

### 1. Clone & Navigate to the Project Root
```bash
cd "practice webpage"
```

### 2. Set Up a Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a file named `.env` in the root folder (this file is excluded from GitHub via `.gitignore` for security) and add the following configuration:

```env
# Gmail SMTP Credentials
SENDER_EMAIL=your_email@gmail.com
SENDER_APP_PASSWORD=your_gmail_app_password  # Must be a 16-character App Password (not your primary password)

# MySQL Connection Details
DB_HOST=your_host_number
DB_PORT=your_port
DB_USER=your_user
DB_PASSWORD=your_mysql_password
DB_NAME=your_patien_records
```

### 4. Run the Application
Start the Flask development server:
```bash
python backend/app.py
```
The application will start, automatically initialize the database/tables if they do not exist, and run on `http://127.0.0.1:5000`.

---

## Database Initialization
On startup, the system will automatically:
1. Check if the database specified in `DB_NAME` exists (and create it if it doesn't).
2. Create the `users` table to store permanent registration details.
3. Create the `otp` table to handle OTP verification sessions, attempts, and expirations.
