import os
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_cors import CORS
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
    CORS(app)

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(splits_bp)
    app.register_blueprint(today_bp)
    app.register_blueprint(progress_bp)
    
    from routes.exercises import exercises_bp
    app.register_blueprint(exercises_bp)

    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'ok'}

    # Frontend routes
    @app.route('/')
    def index():
        return render_template('home.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/signup')
    def signup_page():
        return render_template('signup.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/workout-session')
    def workout_session():
        return render_template('workout_session.html')

    @app.route('/exercise')
    def exercise():
        return render_template('exercise.html')

    @app.route('/splits')
    def splits_page():
        return render_template('splits.html')

    @app.route('/progress')
    def progress_page():
        return render_template('progress.html')

    @app.route('/muscle-selection')
    def muscle_selection():
        return render_template('muscle_selection.html')

    @app.route('/exercise-list')
    def exercise_list():
        return render_template('exercise_list.html')

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)