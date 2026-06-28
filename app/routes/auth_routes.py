from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('farmer.dashboard'))
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        phone = data.get('phone', '')
        address = data.get('address', '')
        
        if User.query.filter_by(email=email).first():
            msg = 'Email already registered.'
            return jsonify({'success': False, 'message': msg}) if request.is_json else (flash(msg, 'danger'), render_template('register.html'))[1]
        if User.query.filter_by(username=username).first():
            msg = 'Username already taken.'
            return jsonify({'success': False, 'message': msg}) if request.is_json else (flash(msg, 'danger'), render_template('register.html'))[1]
        
        user = User(username=username, email=email, phone=phone, address=address)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Registration successful!'})
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('farmer.dashboard') if current_user.role == 'farmer' else url_for('admin.dashboard'))
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            token = create_access_token(identity={'id': user.id, 'role': user.role})
            if request.is_json:
                return jsonify({'success': True, 'token': token, 'role': user.role, 'username': user.username})
            return redirect(url_for('farmer.dashboard') if user.role == 'farmer' else url_for('admin.dashboard'))
        
        msg = 'Invalid email or password.'
        return jsonify({'success': False, 'message': msg}) if request.is_json else (flash(msg, 'danger'), render_template('login.html'))[1]
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        current_user.phone = data.get('phone', current_user.phone)
        current_user.address = data.get('address', current_user.address)
        if data.get('new_password'):
            if not current_user.check_password(data.get('current_password', '')):
                return jsonify({'success': False, 'message': 'Current password incorrect.'})
            current_user.set_password(data.get('new_password'))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully.'})
    return render_template('profile.html', user=current_user)
