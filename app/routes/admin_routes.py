from functools import wraps
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.models import User, Disease, Detection, CropRecord
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required.'}), 403
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.filter_by(role='farmer').count(),
        'total_detections': Detection.query.count(),
        'total_diseases': Disease.query.count(),
        'total_crops': CropRecord.query.count()
    }
    recent_detections = Detection.query.order_by(Detection.detected_at.desc()).limit(10).all()
    return render_template('admin_dashboard.html', stats=stats, recent_detections=recent_detections)

@admin_bp.route('/admin/api/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    users = User.query.filter_by(role='farmer').all()
    return jsonify({'success': True, 'data': [{
        'id': u.id, 'username': u.username, 'email': u.email,
        'phone': u.phone, 'created_at': str(u.created_at),
        'detection_count': len(u.detections)
    } for u in users]})

@admin_bp.route('/admin/api/users/<int:uid>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(uid):
    user = User.query.get_or_404(uid)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'User deleted.'})

@admin_bp.route('/admin/api/diseases', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_diseases():
    if request.method == 'POST':
        data = request.get_json()
        disease = Disease(**data)
        db.session.add(disease)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Disease added.'})
    
    diseases = Disease.query.all()
    return jsonify({'success': True, 'data': [{
        'id': d.id, 'name': d.name, 'crop_type': d.crop_type,
        'symptoms': d.symptoms, 'causes': d.causes,
        'organic_treatment': d.organic_treatment,
        'chemical_treatment': d.chemical_treatment,
        'preventive_measures': d.preventive_measures
    } for d in diseases]})

@admin_bp.route('/admin/api/diseases/<int:did>', methods=['PUT', 'DELETE'])
@login_required
@admin_required
def update_disease(did):
    disease = Disease.query.get_or_404(did)
    if request.method == 'DELETE':
        db.session.delete(disease)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Disease deleted.'})
    
    data = request.get_json()
    for key, val in data.items():
        setattr(disease, key, val)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Disease updated.'})

@admin_bp.route('/admin/api/analytics')
@login_required
@admin_required
def analytics():
    disease_distribution = db.session.query(
        Disease.name, func.count(Detection.id).label('count')
    ).join(Detection, Detection.disease_id == Disease.id)\
     .group_by(Disease.name).all()
    
    monthly_detections = db.session.query(
        func.date_format(Detection.detected_at, '%Y-%m').label('month'),
        func.count(Detection.id).label('count')
    ).group_by('month').order_by('month').limit(12).all()
    
    return jsonify({
        'success': True,
        'disease_distribution': [{'name': r[0], 'count': r[1]} for r in disease_distribution],
        'monthly_detections': [{'month': r[0], 'count': r[1]} for r in monthly_detections],
        'top_farmers': db.session.query(
            User.username, func.count(Detection.id).label('count')
        ).join(Detection).group_by(User.username).order_by(func.count(Detection.id).desc()).limit(5).all()
    })
