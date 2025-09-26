import os
from flask import Flask, send_from_directory, jsonify
from flask_bcrypt import Bcrypt
from .shared_db import db
from .models.user import User

# Blueprintのインポート
from .routes.auth import auth_bp
from .routes.textbook import textbook_bp
from .routes.cart import cart_bp
from .routes.order import order_bp

# Flaskアプリケーションのセットアップ
app = Flask(__name__, static_folder='../../frontend/build', static_url_path='/')
bcrypt = Bcrypt(app)

# 設定
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///default.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_default_secret_key')

# データベースとアプリケーションの初期化
db.init_app(app)

# Blueprintの登録
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(textbook_bp, url_prefix='/api/textbooks')
app.register_blueprint(cart_bp, url_prefix='/api/cart')
app.register_blueprint(order_bp, url_prefix='/api/orders')

# データベーステーブルの作成と管理者ユーザーの追加
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
        admin_user = User(username='admin', password=hashed_password, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()

# Reactフロントエンドのルーティング
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# エラーハンドリング
@app.errorhandler(404)
def not_found(e):
    # APIリクエストの場合はJSONを、それ以外はindex.htmlを返す
    if request.path.startswith('/api/'):
        return jsonify(error='Not Found'), 404
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
