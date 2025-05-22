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