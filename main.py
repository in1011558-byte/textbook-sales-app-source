from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import os

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key')
    # DATABASE_URLのプロトコルをHerokuが要求するものに置換
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        # Herokuのウェルカムページではなく、このメッセージが表示されれば成功
        return "<h1>Flask Application Deployed!</h1><p>Use /init_db to initialize the database, and /register to create a user.</p>"

    @app.cli.command('init-db')
    def init_db_command():
        """Creates the database tables."""
        db.create_all()
        print('Initialized the database.')

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400
        username = data.get('username')
        password = data.get('password')
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "User already exists"}), 400
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": f"User {username} registered successfully"}), 201

    return app

app = create_app()





@app.route(\"/init_db_and_user\")
def init_db_and_user():
    db.create_all()
    username = \'S85073\'
    password = \'87073\'
    if not User.query.filter_by(username=username).first():
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return f\'Database initialized and user {username} created!\'
    return \'Database already initialized or user already exists!\'
