import os
import tempfile

import pytest

from app import create_app


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    data_dir = tempfile.mkdtemp()

    os.environ['COOKIT_DATA_DIR'] = data_dir
    os.environ['DATABASE'] = db_path

    # Reload config with new paths
    import app.config as cfg
    cfg.DATA_DIR = data_dir
    cfg.DATABASE = db_path
    cfg.UPLOAD_FOLDER = os.path.join(data_dir, 'images')

    application = create_app()
    application.config['TESTING'] = True

    yield application

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield
