from datetime import datetime
from app.extensions import db, bcrypt
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    role = db.Column(db.String(20), default='farmer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    detections = db.relationship('Detection', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Disease(db.Model):
    __tablename__ = 'diseases'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    crop_type = db.Column(db.String(50), nullable=False)
    symptoms = db.Column(db.Text)
    causes = db.Column(db.Text)
    organic_treatment = db.Column(db.Text)
    chemical_treatment = db.Column(db.Text)
    preventive_measures = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    detections = db.relationship('Detection', backref='disease', lazy=True)

class Detection(db.Model):
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    disease_id = db.Column(db.Integer, db.ForeignKey('diseases.id'))
    image_path = db.Column(db.String(255), nullable=False)
    confidence_score = db.Column(db.Float)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='detected')
    notes = db.Column(db.Text)

class CropRecord(db.Model):
    __tablename__ = 'crop_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    area = db.Column(db.Float)
    planting_date = db.Column(db.Date)
    health_status = db.Column(db.String(50), default='healthy')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='crop_records')
