from flask import Flask
from config import Config
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)

    # Ensure upload directory exists
    os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)

    from app.models import user
    from app.routes.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')
    
    return app
    # Ensure upload directory exists
    # os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
    
    # # Mock user class for templates until proper authentication is implemented
    # class MockUser:
    #     @property
    #     def is_authenticated(self):
    #         return False
        
    #     @property
    #     def username(self):
    #         return "Guest"
        
    #     @property
    #     def email(self):
    #         return None
    
    # # Add current_user to Jinja context
    # @app.context_processor
    # def inject_user():
    #     return {'current_user': MockUser()}
    
    # # Register blueprints
    # from app.routes.main import main
    # from app.routes.api import api
    # app.register_blueprint(main)
    # app.register_blueprint(api, url_prefix='/api')
    
    # return app