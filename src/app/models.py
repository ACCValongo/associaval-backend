from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    association_id = db.Column(db.Integer, db.ForeignKey('association.id'), nullable=True)

    def __repr__(self):
        return f"User('{self.email}', Admin: {self.is_admin})"

class Association(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    social_media = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    activity_categories = db.Column(db.Text, nullable=True)  # JSON string para múltiplas categorias
    other_activities = db.Column(db.String(200), nullable=True)  # Campo "outros"
    activities = db.relationship('Activity', backref='association', lazy=True)
    users = db.relationship('User', backref='associated_association', lazy=True)

    def __repr__(self):
        return f"Association('{self.name}')"

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    association_id = db.Column(db.Integer, db.ForeignKey('association.id'), nullable=False)

    def __repr__(self):
        return f"Activity('{self.name}', '{self.date}')"

