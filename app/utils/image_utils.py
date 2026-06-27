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

def preprocess_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.filter(ImageFilter.MedianFilter(size=3))
    img = img.resize(Config.IMAGE_SIZE)
    img_array = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(img_array, axis=0)
