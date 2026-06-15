import os
import logging

logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    RENDER_EXTERNAL_URL = 'https://shadow-kdr1.onrender.com/'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or os.urandom(24).hex()
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENCRYPTED_FILE_PATH = os.getenv('ENCRYPTED_FILE_PATH', os.path.join(os.getcwd(), 'backend/app/backend/app/encrypted_files'))
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

    DEBUG = os.getenv('FLASK_ENV', 'production') == 'development'
    VALID_KEY_LENGTHS = {16, 24, 32}

    @staticmethod
    def init_app():
        try:
            os.makedirs(Config.ENCRYPTED_FILE_PATH, exist_ok=True)
            logger.info(f"Created encrypted files directory: {Config.ENCRYPTED_FILE_PATH}")

        except Exception as e:

            logger.error(f"Failed to create encrypted files directory: {str(e)}")
            raise

config = Config()