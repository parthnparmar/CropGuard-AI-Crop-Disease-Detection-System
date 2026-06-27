import sys
import io
import pymysql
from app import create_app
from app.extensions import db
from app.models.models import User
from app.models.seed_data import seed_diseases
from dotenv import load_dotenv
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv()

def create_database_if_not_exists():
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '')
    )
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME', 'crop_disease_db')}")
    conn.close()

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()
        seed_diseases()
        
        if not User.query.filter_by(email='admin@cropguard.ai').first():
            admin = User(
                username='admin',
                email='admin@cropguard.ai',
                phone='1234567890',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("[OK] Admin user created (email: admin@cropguard.ai, password: admin123)")
        
        print("[OK] Database initialized successfully!")

if __name__ == '__main__':
    try:
        create_database_if_not_exists()
        print("[OK] Database created/verified")
    except Exception as e:
        print(f"[ERROR] Database creation error: {e}")
        print("Make sure MySQL is running and credentials in .env are correct")
        exit(1)
    
    print("Initializing database...")
    try:
        init_db()
    except Exception as e:
        print(f"[ERROR] Database initialization error: {e}")
        exit(1)
    
    print("\nStarting Flask server...")
    print("Access the app at: http://127.0.0.1:5000")
    print("Press CTRL+C to stop\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
