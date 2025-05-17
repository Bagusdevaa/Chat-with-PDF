import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

class DevConfig(Config):
    """Development config."""
    DEBUG = True
    TESTING = True

class ProdConfig(Config):
    """Production config."""
    DEBUG = False
    TESTING = False

config = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'default': DevConfig
}