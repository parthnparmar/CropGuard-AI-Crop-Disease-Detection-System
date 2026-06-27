import os
import traceback
from flask import Blueprint, render_template, request, jsonify, send_from_directory
from flask_login import login_required, current_user
from app.extensions import db
from app.models.models import Detection, Disease, CropRecord
from app.utils.image_utils import allowed_file, save_image, preprocess_image
from app.utils.model_utils import predict_disease
from app.utils.pdf_utils import generate_pdf_report
from config import Config

farmer_bp = Blueprint('farmer', __name__)

@farmer_bp.route('/dashboard')
@login_required
def dashboard():
    detections = Detection.query.filter_by(user_id=current_user.id).order_by(Detection.detected_at.desc()).limit(10).all()
    total = Detection.query.filter_by(user_id=current_user.id).count()
    crop_records = CropRecord.query.filter_by(user_id=current_user.id).all()
    return render_template('farmer_dashboard.html', detections=detections, total=total, crop_records=crop_records)

@farmer_bp.route('/detect', methods=['GET'])
@login_required
def detect_page():
    return render_template('detect.html')

@farmer_bp.route('/api/detect', methods=['POST'])
@login_required
def detect():
    try:
        print("[DEBUG] Detection request received")
        
        if 'image' not in request.files:
            print("[DEBUG] No image in request.files")
            return jsonify({'success': False, 'message': 'No image provided.'}), 400
        
        file = request.files['image']
        print(f"[DEBUG] File received: {file.filename}")
        
        if not file.filename or not allowed_file(file.filename):
            print(f"[DEBUG] Invalid file type: {file.filename}")
            return jsonify({'success': False, 'message': 'Invalid file type. Use JPG, PNG, or JPEG.'}), 400
        
        print("[DEBUG] Saving image...")
        filename, filepath = save_image(file)
        print(f"[DEBUG] Image saved: {filepath}")
        
        print("[DEBUG] Preprocessing image...")
        img_array = preprocess_image(filepath)
        print(f"[DEBUG] Image preprocessed. Shape: {img_array.shape}")
        
        print("[DEBUG] Predicting disease...")
        disease_name, confidence = predict_disease(img_array)
        print(f"[DEBUG] Prediction: {disease_name} with confidence {confidence}")
        
        print("[DEBUG] Querying disease from database...")
        disease = Disease.query.filter_by(name=disease_name).first()
        print(f"[DEBUG] Disease found: {disease.name if disease else 'None'}")
        
        print("[DEBUG] Creating detection record...")
        detection = Detection(
            user_id=current_user.id,
            disease_id=disease.id if disease else None,
            image_path=filename,
            confidence_score=confidence,
            status='detected'
        )
        db.session.add(detection)
        db.session.commit()
        print(f"[DEBUG] Detection saved with ID: {detection.id}")
        
        result = {
            'success': True,
            'detection_id': detection.id,
            'disease_name': disease_name,
            'confidence': round(confidence * 100, 2),
            'image_url': f'/uploads/{filename}'
        }
        if disease:
            result.update({
                'crop_type': disease.crop_type,
                'symptoms': disease.symptoms,
                'causes': disease.causes,
                'organic_treatment': disease.organic_treatment,
                'chemical_treatment': disease.chemical_treatment,
                'preventive_measures': disease.preventive_measures
            })
        
        print("[DEBUG] Detection successful, returning result")
        return jsonify(result)
        
    except Exception as e:
        print(f"\n[ERROR] Detection failed with exception:")
        print(f"[ERROR] Type: {type(e).__name__}")
        print(f"[ERROR] Message: {str(e)}")
        print(f"[ERROR] Traceback:")
        traceback.print_exc()
        print("\n")
        return jsonify({
            'success': False, 
            'message': f'Server error: {type(e).__name__}: {str(e)}'
        }), 500

@farmer_bp.route('/api/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    detections = Detection.query.filter_by(user_id=current_user.id)\
        .order_by(Detection.detected_at.desc()).paginate(page=page, per_page=10)
    
    data = [{
        'id': d.id,
        'disease': d.disease.name if d.disease else 'Unknown',
        'crop_type': d.disease.crop_type if d.disease else 'N/A',
        'confidence': round(d.confidence_score * 100, 2) if d.confidence_score else 0,
        'date': d.detected_at.strftime('%Y-%m-%d %H:%M'),
        'status': d.status,
        'image_url': f'/uploads/{d.image_path}'
    } for d in detections.items]
    
    return jsonify({'success': True, 'data': data, 'total': detections.total, 'pages': detections.pages})

@farmer_bp.route('/api/stats')
@login_required
def stats():
    from sqlalchemy import func
    disease_counts = db.session.query(
        Disease.name, func.count(Detection.id).label('count')
    ).join(Detection, Detection.disease_id == Disease.id)\
     .filter(Detection.user_id == current_user.id)\
     .group_by(Disease.name).all()
    
    return jsonify({
        'success': True,
        'disease_distribution': [{'name': r[0], 'count': r[1]} for r in disease_counts],
        'total_detections': Detection.query.filter_by(user_id=current_user.id).count()
    })

@farmer_bp.route('/api/download-report')
@login_required
def download_report():
    detections = Detection.query.filter_by(user_id=current_user.id).order_by(Detection.detected_at.desc()).all()
    filename = generate_pdf_report(current_user, detections)
    return send_from_directory(Config.REPORTS_FOLDER, filename, as_attachment=True)

@farmer_bp.route('/api/crop-records', methods=['GET', 'POST'])
@login_required
def crop_records():
    if request.method == 'POST':
        data = request.get_json()
        record = CropRecord(
            user_id=current_user.id,
            crop_name=data.get('crop_name'),
            area=data.get('area'),
            planting_date=data.get('planting_date'),
            health_status=data.get('health_status', 'healthy')
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Crop record added.'})
    
    records = CropRecord.query.filter_by(user_id=current_user.id).all()
    return jsonify({'success': True, 'data': [{
        'id': r.id, 'crop_name': r.crop_name, 'area': r.area,
        'planting_date': str(r.planting_date), 'health_status': r.health_status
    } for r in records]})
