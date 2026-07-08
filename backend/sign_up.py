from flask import request, jsonify
from mysql.connector import Error
from utils import get_db_connection, hash_password

# --- API ROUTES ---
def login(): 
    data = request.get_json() or {}
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required.'}), 400

    hashed_pwd = hash_password(password)

    conn = get_db_connection()
    if conn is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
        
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_found = cursor.fetchone()

        if not user_found:
            return jsonify({'status': 'error', 'message': 'No account found with this email. Please register first.'}), 400

        # NEW SECURITY CHECK: Are they verified?
        if not user_found['status'] == 'Verified':
            return jsonify({'status': 'error', 'message': 'Please verify your email address before logging in.'}), 403

        # Validate credentials
        if user_found['password'] == hashed_pwd:
            return jsonify({
                'status': 'success',
                'message': f'Welcome back, {user_found["name"]}!',
                'user': {
                    'name': user_found['name'],
                    'email': user_found['email'],
                    'role': user_found['role'],
                    'gender': user_found['gender'],
                    'age': user_found['age'],
                    'phone_number': user_found['phone_number'],
                    'address': user_found['address']
                }
            })
        else:
            return jsonify({'status': 'error', 'message': 'Incorrect password.'}), 400
            
    except Error as e:
        print(f"Database error during login: {e}")
        return jsonify({'status': 'error', 'message': 'Login failed due to server error.'}), 500
    finally:
        cursor.close()
        conn.close()
