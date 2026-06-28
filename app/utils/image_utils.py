import os
import uuid
import numpy as np
from PIL import Image, ImageFilter
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_image(file):
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file.save(filepath)
    return filename, filepath

def is_plant_leaf(image_path):
    """Heuristic check: returns True if image looks like a plant leaf."""
    img = Image.open(image_path).convert('RGB').resize((128, 128))
    arr = np.array(img, dtype=np.float32)
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]

    # 1. Some green/yellow/brown present (diseased leaves can be yellow/brown)
    has_vegetation = np.mean(
        (g > r + 5) & (g > b + 5) |   # green pixels
        ((r > 100) & (g > 80) & (b < 80))  # yellow/brown pixels (diseased)
    )
    if has_vegetation < 0.05:
        return False

    # 2. Texture variance: plain solid-color images (logos, sky) have very low variance
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    if np.std(gray) < 5.0:
        return False

    return True

def preprocess_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.filter(ImageFilter.MedianFilter(size=3))
    img = img.resize(Config.IMAGE_SIZE)
    img_array = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(img_array, axis=0)
