import os
from flask import request, jsonify
from mysql.connector import Error
from utils import get_db_connection

def add_visit_api():
    data = request.get_json() or {}
    
    patient_name = data.get("patient_name", '').strip()
    age = data.get("age", '')
    gender = data.get("gender", '').strip()
    phone_number = data.get('phone_number', '').strip()
    address = data.get("address", '').strip()  
    purpose = data.get('purpose', '').strip()
    department = data.get('department', '').strip()
    attending_doctor = data.get('attending_doctor', '').strip()

    if not patient_name or age is None or not gender or not phone_number or not address or not purpose or not department or not attending_doctor:
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400

    try:
        age = int(age)
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Age must be a valid number.'}), 400

    if age < 0 or age > 120:
        return jsonify({'status': 'error', 'message': 'Please enter a valid age.'}), 400

    if gender not in ['Male', 'Female', 'Other']:
        return jsonify({'status': 'error', 'message': 'Invalid gender option.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO patient_records (patient_name, age, gender, phone_number, address, purpose, department, attending_doctor)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (patient_name, age, gender, phone_number, address, purpose, department, attending_doctor)
        )
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Patient visit successfully registered.'})
    except Error as e:
        print(f"Database error during visit addition: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to save visit record due to server error.'}), 500
    finally:
        cursor.close()
        conn.close()