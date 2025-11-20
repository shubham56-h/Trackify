import os
from flask import Flask
from flask_migrate import Migrate
from models import db
from routes.auth import auth_bp
from routes.splits import splits_bp
from routes.today import today_bp
from routes.progress import progress_bp
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_mapping({
        'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': os.getenv('SECRET_KEY') or 'dev',
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY') or 'jwt-dev'
    })

    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(splits_bp)
    app.register_blueprint(today_bp)
    app.register_blueprint(progress_bp)

    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'ok'}

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)