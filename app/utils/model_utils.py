import os
import json
import hashlib
import numpy as np
from config import Config

_CLASSES_PATH = os.path.join(os.path.dirname(Config.MODEL_PATH), "class_names.json")

# Fallback class names (matches original 10-class demo behaviour)
_FALLBACK_CLASSES = [
    "Tomato Late Blight", "Tomato Early Blight", "Potato Late Blight",
    "Corn Northern Leaf Blight", "Rice Blast", "Wheat Rust",
    "Apple Scab", "Grape Black Rot", "Citrus Greening", "Healthy Crop",
]

def _load_class_names():
    if os.path.exists(_CLASSES_PATH):
        with open(_CLASSES_PATH) as f:
            return json.load(f)
    return _FALLBACK_CLASSES

DISEASE_CLASSES = _load_class_names()

_model = None
_model_type = None


def get_model():
    global _model, _model_type
    if _model is not None:
        return _model, _model_type

    path = Config.MODEL_PATH
    if path.endswith(".h5") and os.path.exists(path):
        try:
            import tensorflow as tf
            _model = tf.keras.models.load_model(path)
            _model_type = "keras"
            # Refresh class names each load (in case retrained)
            global DISEASE_CLASSES
            DISEASE_CLASSES = _load_class_names()
            print(f"[MODEL] Keras model loaded ({len(DISEASE_CLASSES)} classes)")
            return _model, _model_type
        except Exception as e:
            print(f"[MODEL] Keras load failed: {e}")

    print("[MODEL] No valid model found. Running in demo mode.")
    _model_type = "demo"
    return None, "demo"


def predict_disease(preprocessed_image):
    model, model_type = get_model()

    if model_type == "keras":
        preds = model.predict(preprocessed_image, verbose=0)[0]
        idx = int(np.argmax(preds))
        confidence = float(preds[idx])
        disease_name = DISEASE_CLASSES[idx] if idx < len(DISEASE_CLASSES) else "Unknown"
        if confidence < Config.CONFIDENCE_THRESHOLD:
            return "Healthy Crop", confidence
        return disease_name, confidence

    # Demo mode — deterministic pseudo-random
    img_hash = hashlib.md5(preprocessed_image.tobytes()).hexdigest()
    idx = int(img_hash[:8], 16) % len(DISEASE_CLASSES)
    rng = np.random.default_rng(int(img_hash[:8], 16))
    confidence = float(rng.uniform(0.72, 0.97))
    return DISEASE_CLASSES[idx], confidence
