from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
    
    # Ensure upload directory exists
    os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
    
    # Register blueprints
    from app.routes.main import main
    from app.routes.api import api
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')
    
    return app