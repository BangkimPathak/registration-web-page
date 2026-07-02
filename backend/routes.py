from flask import Blueprint, render_template
from registration import verified_otp_page, set_password_page, signup, verify_otp_api, resend_otp_api, set_password_api
from sign_up import login

# Define blueprints
main_bp = Blueprint('main', __name__)
registration_bp = Blueprint('registration', __name__)
signup_bp = Blueprint('signup', __name__)

def getUser(id):
    return "hi"

def index():
    return render_template('index.html')

def home():
    return render_template('home.html')

# Register HTML/Main routes
main_bp.route('/test/<id>')(getUser)
main_bp.route('/')(index)
main_bp.route('/home')(home)

# Register Registration routes
registration_bp.route('/verify-otp')(verified_otp_page)
registration_bp.route('/set-password')(set_password_page)
registration_bp.route('/api/signup', methods=['POST'])(signup)
registration_bp.route('/api/verify-otp', methods=['POST'])(verify_otp_api)
registration_bp.route('/api/resend-otp', methods=['POST'])(resend_otp_api)
registration_bp.route('/api/set-password', methods=['POST'])(set_password_api)

# Register Sign Up/Login routes
signup_bp.route('/api/login', methods=['POST'])(login)

def register_routes(app):
    """Links and registers all routing blueprints in the project."""
    app.register_blueprint(main_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(signup_bp)
