import os
from flask import request, jsonify
from mysql.connector import Error
from utils import get_db_connection

def get_visits_api():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patient_records ORDER BY visit_time DESC")
        visits = cursor.fetchall()
        
        # Format timestamps to strings so they are JSON serializable
        for v in visits:
            if v['visit_time']:
                v['visit_time'] = v['visit_time'].strftime('%Y-%m-%d %H:%M:%S')
                
        return jsonify({'status': 'success', 'visits': visits})
    except Error as e:
        print(f"Database error during fetching visits: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to retrieve visitor records.'}), 500
    finally:
        cursor.close()
        conn.close()

def get_visit_detail_api():
    visit_id = request.args.get('id')
    if not visit_id:
        return jsonify({'status': 'error', 'message': 'Record ID is required.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patient_records WHERE id = %s", (visit_id,))
        visit = cursor.fetchone()

        if not visit:
            return jsonify({'status': 'error', 'message': 'Record not found.'}), 404

        if visit['visit_time']:
            visit['visit_time'] = visit['visit_time'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify({'status': 'success', 'visit': visit})
    except Error as e:
        print(f"Database error during fetching visit detail: {e}")
        return jsonify({'status': 'error', 'message': f"Database Error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

def edit_api():
    data = request.get_json() or {}    
    visit_id = data.get('id')

   

    patient_name = data.get('patient_name', '').strip()
    age = data.get('age')
    gender = data.get('gender', '').strip()
    phone_number = data.get('phone_number', '').strip()
    address = data.get('address', '').strip()
    purpose = data.get('purpose', '').strip()
    department = data.get('department', '').strip()
    attending_doctor = data.get('attending_doctor', '').strip()

    if not visit_id or not patient_name or age is None or not gender or not phone_number or not address or not purpose or not department or not attending_doctor:
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
        update_query = """
            UPDATE patient_records
            SET patient_name = %s, age = %s, gender = %s, phone_number = %s, address = %s, purpose = %s, department = %s, attending_doctor = %s
            WHERE id = %s
        """
        cursor.execute(update_query, (patient_name, age, gender, phone_number, address, purpose, department, attending_doctor, visit_id))
        conn.commit()

        # If it returns 0 rowcount, it might mean the ID doesn't exist OR the user submitted without making any changes.
        # Let's check if the ID exists to give a more accurate error.
        cursor.execute("SELECT id FROM patient_records WHERE id = %s", (visit_id,))
        if not cursor.fetchone():
            return jsonify({'status': 'error', 'message': "No record found with the provided id"}), 404

        return jsonify({'status': 'success', 'message': "Record updated successfully"})
    except Error as e:
        print(f"Database error during visit update: {e}")
        return jsonify({'status': 'error', 'message': f"Database Error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()