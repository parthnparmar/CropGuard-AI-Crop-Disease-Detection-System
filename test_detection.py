import sys
import os
import traceback

# Make sure we run from project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.models import User, Disease
from app.utils.image_utils import preprocess_image
from app.utils.model_utils import predict_disease, get_model

app = create_app()

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

with app.app_context():
    print("=" * 60)
    print("CROPGUARD AI - SYSTEM DIAGNOSTIC TEST")
    print("=" * 60)
    
    all_ok = True

    # Test 1: Database connection
    print("\n[1/5] Database connection...")
    try:
        disease_count = Disease.query.count()
        user_count = User.query.count()
        print(f"  {PASS} Connected: {disease_count} diseases, {user_count} users")
    except Exception as e:
        print(f"  {FAIL} Database error: {e}")
        traceback.print_exc()
        all_ok = False
        sys.exit(1)

    # Test 2: Disease records
    print("\n[2/5] Disease records...")
    diseases = Disease.query.all()
    if len(diseases) == 0:
        print(f"  {FAIL} No diseases in database. Run: python run.py")
        all_ok = False
    else:
        print(f"  {PASS} {len(diseases)} diseases found:")
        for d in diseases:
            print(f"       - {d.name}")

    # Test 3: Image preprocessing
    print("\n[3/5] Image preprocessing...")
    test_images = [
        f for f in os.listdir('uploads')
        if f.endswith(('.png', '.jpg', '.jpeg')) and not f.startswith('.')
    ]
    
    if not test_images:
        print(f"  {WARN} No images in uploads/ folder. Creating a test image...")
        try:
            from PIL import Image
            import numpy as np
            test_img_path = 'uploads/test_green.png'
            img = Image.fromarray((np.random.rand(256, 256, 3) * 255).astype('uint8'))
            img.save(test_img_path)
            test_images = ['test_green.png']
            print(f"  {PASS} Test image created: {test_img_path}")
        except Exception as e:
            print(f"  {FAIL} Cannot create test image: {e}")
            all_ok = False
    
    img_array = None
    if test_images:
        try:
            test_img_path = os.path.join('uploads', test_images[0])
            img_array = preprocess_image(test_img_path)
            print(f"  {PASS} Preprocessing OK")
            print(f"       File: {test_images[0]}")
            print(f"       Shape: {img_array.shape}")
            print(f"       Dtype: {img_array.dtype}")
            print(f"       Range: [{img_array.min():.2f}, {img_array.max():.2f}]")
        except Exception as e:
            print(f"  {FAIL} Preprocessing error: {e}")
            traceback.print_exc()
            all_ok = False

    # Test 4: Model loading
    print("\n[4/5] Model loading...")
    try:
        model, model_type = get_model()
        print(f"  {PASS} Model type: {model_type}")
        if model_type == 'demo':
            print(f"  {WARN} Running in DEMO mode (no real model found)")
            print(f"       MODEL_PATH: {app.config.get('MODEL_PATH', 'not set')}")
    except Exception as e:
        print(f"  {FAIL} Model error: {e}")
        traceback.print_exc()
        all_ok = False

    # Test 5: Full prediction
    print("\n[5/5] Disease prediction...")
    if img_array is not None:
        try:
            disease_name, confidence = predict_disease(img_array)
            print(f"  {PASS} Prediction: {disease_name} ({confidence:.2%})")
            
            db_disease = Disease.query.filter_by(name=disease_name).first()
            if db_disease:
                print(f"  {PASS} Disease matched in DB: {db_disease.name}")
                print(f"       Crop type: {db_disease.crop_type}")
                print(f"       Has symptoms: {'Yes' if db_disease.symptoms else 'No'}")
                print(f"       Has treatment: {'Yes' if db_disease.organic_treatment else 'No'}")
            else:
                print(f"  {WARN} '{disease_name}' NOT found in database!")
                print(f"       Available names:")
                for d in Disease.query.all():
                    print(f"         '{d.name}'")
        except Exception as e:
            print(f"  {FAIL} Prediction error: {e}")
            traceback.print_exc()
            all_ok = False
    else:
        print(f"  {WARN} Skipped (no test image available)")

    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("ALL TESTS PASSED - System is ready!")
        print("\nStart server with: python run.py")
        print("Then open: http://localhost:5000")
    else:
        print("SOME TESTS FAILED - Fix errors above before running server")
    print("=" * 60)
