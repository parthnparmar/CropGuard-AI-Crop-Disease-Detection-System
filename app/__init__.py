import os
from flask import Flask, send_from_directory, request, jsonify, redirect, url_for, flash
from config import Config
from app.extensions import db, bcrypt, login_manager, jwt, cors, migrate

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    
    # Create required folders
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        flash('Please login to access this page.', 'warning')
        return redirect(url_for('auth.login'))
    
    from app.models.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from app.routes.auth_routes import auth_bp
    from app.routes.farmer_routes import farmer_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.main_routes import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(farmer_bp)
    app.register_blueprint(admin_bp)
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)
    
    return app
