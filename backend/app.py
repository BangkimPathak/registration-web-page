import os
from flask import Flask
from utils import init_db
from routes import register_routes

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, 
            template_folder=os.path.abspath(os.path.join(base_dir, '..', 'frontend', 'templates')), 
            static_folder=os.path.abspath(os.path.join(base_dir, '..', 'frontend', 'static')))

register_routes(app)

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run( debug=True , port=5000)