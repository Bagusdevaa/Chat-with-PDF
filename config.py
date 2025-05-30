import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Base config."""
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    HOST = str(os.getenv('DB_HOST'))
    PORT = str(os.getenv('DB_PORT'))
    USER = str(os.getenv('DB_USER'))
    PASSWORD = str(os.getenv('DB_PASSWORD'))
    DATABASE = str(os.getenv('DB_DATABASE'))

    encoded_password = urllib.parse.quote_plus(PASSWORD)
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USER}:{encoded_password}@{HOST}:{PORT}/{DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  # 1 day
    JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 30  # 30 days
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Email settings for password reset
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # print(HOST, PORT, USER, PASSWORD, DATABASE)

# class DevConfig(Config):
#     """Development config."""
#     DEBUG = True
#     TESTING = True

# class ProdConfig(Config):
#     """Production config."""
#     DEBUG = False
#     TESTING = False

# config = {
#     'dev': DevConfig,
#     'prod': ProdConfig,
#     'default': DevConfig
# }