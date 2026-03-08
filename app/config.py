import os

DATA_DIR = os.environ.get('COOKIT_DATA_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))
DATABASE = os.path.join(DATA_DIR, 'cookit.db')
UPLOAD_FOLDER = os.path.join(DATA_DIR, 'images')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
