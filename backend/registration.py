import random 
from datetime import datetime   
from mysql.connector import Error
from flask import request, jsonify, render_template
from utils import get_db_connection, hash_password, is_valid_email, send_otp_email

# html routes 
def verified_otp_page(): 
   
    return render_template('verified_otp.html')

def set_password_page():
    return render_template('set_password.html')

# api routes
def signup():
    data = request.get_json() or {}

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    role = 'Patient'
    gender = data.get('gender', '').strip()
    age = data.get('age')
    phone = data.get('phone', '').strip()
    address = data.get('address', '').strip()

    if not name or not email or not role or not gender or age is None or not phone or not address:
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400

    try:
        age = int(age)
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Age must be a valid number.'}), 400

    if age <= 0 or age > 120:
        return jsonify({'status': 'error', 'message': 'Please enter a valid age.'}), 400

    if not is_valid_email(email):
        return jsonify({'status': 'error', 'message': 'Invalid email address format.'}), 400

    if gender not in ['Male', 'Female', 'Other']:
        return jsonify({'status': 'error', 'message': 'Invalid gender option selected.'}), 400

    if role not in ['Patient', 'Doctor', 'Staff', 'Other']:
        return jsonify({'status': 'error', 'message': 'Invalid hospital role selected.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

    # else:
    try:
        cursor = conn.cursor(dictionary=True)

# 1. Check if the user already exists in the permanent table = user 
        cursor.execute("SELECT status FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            if existing_user['status'] == 'Verified':
                return jsonify({'status': 'error', 'message': 'An account with this email is already verified. Please log in.'}), 400
            else:
                # User exists but isn't verified yet. Update their details.
                cursor.execute(
                    "UPDATE users SET name = %s, role = %s, gender = %s, age = %s, phone_number = %s, address = %s WHERE email = %s", 
                    (name, role, gender, age, phone, address, email)
                )
        else:
            #  New/Fresh user: Insert into permanent table as unverified with blank password
            cursor.execute(
                "INSERT INTO users (name, email, password, role, gender, age, phone_number, address, status) VALUES (%s, %s, '', %s, %s, %s, %s, %s, %s)", 
                (name, email, role, gender, age, phone, address, 'Unverified')
            )

        otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
        # 2. Add or Update the OTP tracker in the pending table
        sql_pending = """
            INSERT INTO otp (email, otp, attempts, status, expires_at)
            VALUES (%s, %s, 0, 'Unverified', CURRENT_TIMESTAMP + INTERVAL 10 MINUTE)
            ON DUPLICATE KEY UPDATE 
            otp = %s, attempts = 0, status = 'Unverified', requested_at = CURRENT_TIMESTAMP, expires_at = (CURRENT_TIMESTAMP + INTERVAL 10 MINUTE)
        """
        cursor.execute(sql_pending, (email, otp, otp))
        conn.commit()
    
        # 3. Send email
        send_otp_email(email, otp)
        
        return jsonify({
            'status': 'success', 
            'message': 'Account validation code generated. Check your email for OTP.',
            'redirect': f'/verify-otp?email={email}'
        })

    except Error as e:
        error_message = str(e)
        print(f"Database error during signup: {error_message}")
        return jsonify({'status': 'error', 'message': f'MySQL Error: {error_message}'}), 500
    finally:
        cursor.close()
        conn.close()

def verify_otp_api():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    otp_input = data.get('otp', '').strip()

    if not email or not otp_input:
        return jsonify({'status': 'error', 'message': 'Email and verification code are required.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM otp WHERE email = %s", (email,))
        otp = cursor.fetchone()

        if not otp:
            return jsonify({'status': 'error', 'message': 'Verification session not found. Please sign up again.'}), 400

        # Check Expiration Time (from MySQL expires_at column) or if already marked expired
        if datetime.now() > otp['expires_at'] or otp['status'] == 'Expired':
            cursor.execute("UPDATE otp SET status = 'Expired' WHERE email = %s", (email,))
            conn.commit()
            return jsonify({'status': 'error', 'message': 'OTP has expired. Please request a new one or sign up again.'}), 400

        # Check Maximum Attempts
        if otp['attempts'] >= 3:
            cursor.execute("UPDATE otp SET status = 'Expired' WHERE email = %s", (email,))
            conn.commit()
            return jsonify({'status': 'error', 'message': 'Too many failed attempts. For security, please sign up again.'}), 400

        # Verify the OTP
        if otp['otp'] != otp_input:
            cursor.execute("UPDATE otp SET attempts = attempts + 1 WHERE email = %s", (email,))
            conn.commit()
            return jsonify({'status': 'error', 'message': 'Invalid verification code. Please try again.'}), 400

        # SUCCESS! Update otp status to 'Verified'
        cursor.execute("UPDATE otp SET status = 'Verified' WHERE email = %s", (email,))
        conn.commit()

        return jsonify({
            'status': 'success', 
            'message': 'Email address successfully verified. Please choose a password to complete your profile.',
            'redirect': f'/set-password?email={email}'
        })
    except Error as e:
        print(f"Database error during verification: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to verify account due to database error.'}), 500
    finally:
        cursor.close()
        conn.close()

def resend_otp_api():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'status': 'error', 'message': 'Email is required.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
    try:
        cursor = conn.cursor()
        
        # Check if they are actually in the waiting room
        cursor.execute("SELECT email FROM otp WHERE email = %s", (email,))
        if not cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Verification session expired. Please sign up again.'}), 400

        # Generate new OTP, reset attempts, update timers
        new_otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
        cursor.execute(
            """UPDATE otp 
               SET otp = %s, attempts = 0, status = 'Unverified', requested_at = CURRENT_TIMESTAMP, expires_at = (CURRENT_TIMESTAMP + INTERVAL 10 MINUTE) 
               WHERE email = %s""",
            (new_otp, email)
        )
        conn.commit()

        send_otp_email(email, new_otp)

        return jsonify({'status': 'success', 'message': 'A new verification code has been sent to your email.'})
    except Error as e:
        print(f"Database error during resend: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to resend OTP.'}), 500
    finally:
        cursor.close()
        conn.close()

def set_password_api():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required.'}), 400

    if len(password) < 6:
        return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters long.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Verify that OTP was verified for this email
        cursor.execute("SELECT status FROM otp WHERE email = %s", (email,))
        pending_user = cursor.fetchone()
        
        if not pending_user or pending_user['status'] != 'Verified':
            return jsonify({'status': 'error', 'message': 'Unauthorized password change request or session expired.'}), 401

        # Hashing password
        hashed_pwd = hash_password(password)

        # Update users table with password and set status to 'Verified'
        cursor.execute("UPDATE users SET password = %s, status = 'Verified' WHERE email = %s", (hashed_pwd, email))
        
        # Update otp table status to 'Completed' to indicate registration completion
        cursor.execute("UPDATE otp SET status = 'Completed' WHERE email = %s", (email,))
        conn.commit()

        # Fetch verified user details to send back for frontend session
        cursor.execute("SELECT name, email, role FROM users WHERE email = %s", (email,))
        verified_user = cursor.fetchone()

        return jsonify({
            'status': 'success',
            'message': 'Password successfully set. Profile created!',
            'user': verified_user
        })
        
    except Error as e:
        print(f"Database error during set-password: {e}")
        return jsonify({'status': 'error', 'message': 'Database error while setting password.'}), 500
    finally:
        cursor.close()
        conn.close()

