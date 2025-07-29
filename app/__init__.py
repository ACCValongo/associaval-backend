from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

# Configurar CORS para permitir requisições do frontend
CORS(app, origins=["https://gpazdluh.manus.space", "https://gbtmwecv.manus.space", "https://jomdceve.manus.space", "https://wrggdzow.manus.space"])

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

from app import routes, models

@app.template_filter("from_json")
def from_json_filter(value):
    if value:
        return json.loads(value)
    return []

with app.app_context():
    db.create_all()
    # Criar administrador padrão se não existir
    from app.models import User
    admin_email = "accvalongo@gmail.com"
    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        hashed_password = bcrypt.generate_password_hash("admin123").decode("utf-8")
        admin_user = User(email=admin_email, password=hashed_password, is_admin=True)
        db.session.add(admin_user)
        try:
            db.session.commit()
            print(f"Administrador padrão criado: {admin_email} / admin123")
        except Exception as e:
            db.session.rollback()
            print(f"Administrador já existe: {admin_email}")


