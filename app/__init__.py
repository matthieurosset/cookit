import os

from flask import Flask, redirect, url_for

from .db import init_db, close_db


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbs'), exist_ok=True)

    init_db(app)
    app.teardown_appcontext(close_db)

    from .routes import recipes, tags, shopping, import_url
    app.register_blueprint(recipes.bp)
    app.register_blueprint(tags.bp)
    app.register_blueprint(shopping.bp)
    app.register_blueprint(import_url.bp)

    @app.route('/')
    def index():
        return redirect(url_for('recipes.index'))

    return app
