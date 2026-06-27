# 🌿 CropGuard AI — Crop Disease Detection System

An AI-powered web application that helps farmers detect crop diseases from leaf images using Deep Learning (MobileNetV2), with multilingual support and voice interaction.

---

## 📋 Table of Contents

1. [Features](#-features)
2. [Tech Stack](#-tech-stack)
3. [Project Structure](#-project-structure)
4. [Supported Diseases (38 Classes)](#-supported-diseases-38-classes)
5. [Supported Languages](#-supported-languages)
6. [Prerequisites](#-prerequisites)
7. [Installation & Setup](#-installation--setup)
8. [AI Model Training](#-ai-model-training)
9. [Running the Application](#-running-the-application)
10. [Usage Guide](#-usage-guide)
11. [API Endpoints](#-api-endpoints)
12. [Default Credentials](#-default-credentials)
13. [Security Features](#-security-features)
14. [Troubleshooting](#-troubleshooting)
15. [Deployment](#-deployment)

---

## ✨ Features

### 🤖 AI Disease Detection
- Upload a crop leaf image (JPG/PNG/JPEG) for instant diagnosis
- MobileNetV2 Transfer Learning model trained on Plant Village dataset
- 38 disease classes across 14 crop types
- Confidence score displayed with animated progress bar
- Detailed symptoms, causes, organic & chemical treatments, preventive measures

### 🌍 Multilingual Voice Translation
- Translate the entire website into 11 Indian & international languages instantly
- Language preference saved across sessions (localStorage)
- **Speech-to-Text (STT):** Speak queries into the chatbot using your microphone
- **Text-to-Speech (TTS):** Listen to detection results, treatments & recommendations read aloud
- Powered by Google Translate Widget + Web Speech API (no API key required)

### 👨‍🌾 Farmer Dashboard
- Detection history with date, disease name, confidence, and crop type
- Analytics charts (disease distribution, detection trends)
- Crop records management (add/view planted crops)
- Download PDF reports of detection history

### 🛡️ Admin Panel
- View and manage all registered farmers
- Manage disease database (add/edit/delete entries)
- System-wide analytics and statistics
- Monitor all detections across all users

### 💬 AI Chatbot
- Ask questions about crop diseases
- Voice input supported via microphone button
- Available on every page (floating widget)

### 📄 PDF Reports
- Generate and download detection history as PDF
- Includes disease names, dates, confidence scores, and crop types

---

## 🚀 Tech Stack

| Layer       | Technology                                      |
|-------------|------------------------------------------------|
| Backend     | Python 3.x, Flask, SQLAlchemy, Flask-Login     |
| Database    | MySQL 5.7+                                     |
| AI / ML     | TensorFlow 2.x, Keras, MobileNetV2             |
| Dataset     | Plant Village (70,295 images, 38 classes)      |
| Frontend    | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5    |
| Charts      | Chart.js 4                                     |
| Translation | Google Translate Widget (free embed)           |
| Voice       | Web Speech API (browser-native, no key needed) |
| PDF         | ReportLab                                      |
| Security    | JWT, bcrypt, Flask-Login, SQLAlchemy ORM       |

---

## 🗂️ Project Structure

```
Crop Disease Detection System/
├── app/
│   ├── models/
│   │   ├── models.py          # SQLAlchemy DB models (User, Disease, Detection, CropRecord)
│   │   └── seed_data.py       # Seeds 38 disease entries into DB on first run
│   ├── routes/
│   │   ├── admin_routes.py    # Admin panel APIs
│   │   ├── auth_routes.py     # Register / Login / Logout / Profile
│   │   ├── farmer_routes.py   # Detect, History, Stats, PDF, Crop Records
│   │   └── main_routes.py     # Home page, public disease list, chatbot API
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css      # Main stylesheet
│   │   │   └── translate.css  # Language selector & mic button styles
│   │   ├── js/
│   │   │   ├── detect.js      # Image upload, preview, API call, result render
│   │   │   └── translate.js   # Translation engine, TTS, STT, language selector
│   │   └── images/
│   ├── templates/
│   │   ├── base.html          # Base layout with navbar & language selector
│   │   ├── index.html         # Home page with chatbot widget
│   │   ├── detect.html        # Disease detection page with TTS button
│   │   ├── farmer_dashboard.html
│   │   ├── admin_dashboard.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── utils/
│   │   ├── image_utils.py     # File validation, save, preprocess (224×224)
│   │   ├── model_utils.py     # Load Keras model, predict disease
│   │   └── pdf_utils.py       # Generate PDF detection report
│   ├── __init__.py            # Flask app factory (create_app)
│   └── extensions.py          # db, login_manager, bcrypt, jwt, cors
├── ml_model/
│   ├── train_model.py         # MobileNetV2 training script (2-phase)
│   ├── crop_disease_model.h5  # Trained Keras model (generated after training)
│   └── class_names.json       # 38 class name list (generated after training)
├── Plant_Disease_Dataset/
│   ├── train/                 # 70,295 training images (38 folders)
│   ├── valid/                 # 17,572 validation images (38 folders)
│   └── test/
├── uploads/                   # User-uploaded leaf images
├── reports/                   # Generated PDF reports
├── .env                       # Environment variables (DB credentials, secret keys)
├── config.py                  # App configuration class
├── requirements.txt           # Python dependencies
└── run.py                     # App entry point (DB init + Flask server)
```

---

## 🌱 Supported Diseases (38 Classes)

| Crop        | Diseases                                                                 |
|-------------|--------------------------------------------------------------------------|
| Apple       | Apple Scab, Black Rot, Cedar Apple Rust, Healthy                        |
| Blueberry   | Healthy                                                                  |
| Cherry      | Powdery Mildew, Healthy                                                  |
| Corn        | Cercospora / Gray Leaf Spot, Common Rust, Northern Leaf Blight, Healthy |
| Grape       | Black Rot, Esca (Black Measles), Leaf Blight, Healthy                   |
| Orange      | Haunglongbing (Citrus Greening)                                          |
| Peach       | Bacterial Spot, Healthy                                                  |
| Pepper      | Bacterial Spot, Healthy                                                  |
| Potato      | Early Blight, Late Blight, Healthy                                       |
| Raspberry   | Healthy                                                                  |
| Soybean     | Healthy                                                                  |
| Squash      | Powdery Mildew                                                           |
| Strawberry  | Leaf Scorch, Healthy                                                     |
| Tomato      | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Mosaic Virus, Yellow Leaf Curl Virus, Healthy |

---

## 🌍 Supported Languages

| Language   | Code | Voice Locale |
|------------|------|--------------|
| English    | en   | en-IN        |
| हिंदी       | hi   | hi-IN        |
| ગુજરાતી    | gu   | gu-IN        |
| मराठी       | mr   | mr-IN        |
| தமிழ்      | ta   | ta-IN        |
| తెలుగు     | te   | te-IN        |
| বাংলা      | bn   | bn-IN        |
| ਪੰਜਾਬੀ     | pa   | pa-IN        |
| ಕನ್ನಡ      | kn   | kn-IN        |
| മലയാളം    | ml   | ml-IN        |
| اردو       | ur   | ur-IN        |

Language preference is saved in browser localStorage and restored on every page load.

---

## 📋 Prerequisites

- Python 3.8 – 3.12
- MySQL Server 5.7+
- pip (Python package manager)
- Modern browser (Chrome/Edge recommended for full Web Speech API support)

---

## 🔧 Installation & Setup

### 1. Navigate to project directory
```bash
cd "Crop Disease Detection System"
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Edit `.env` file:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=crop_disease_db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

### 4. Make sure MySQL is running
```bash
# Windows
net start mysql

# Linux / macOS
sudo service mysql start
```

The application will **automatically create the database** and seed all 38 disease entries on first run.

---

## 🧠 AI Model Training

The model uses **MobileNetV2 Transfer Learning** with two training phases:
- **Phase 1:** Freeze base, train custom classification head
- **Phase 2:** Unfreeze last 30 layers for fine-tuning

### Quick Training (25 images/class — for testing, ~10 minutes on CPU)
```powershell
$env:TF_ENABLE_ONEDNN_OPTS="0"
$env:TF_CPP_MIN_LOG_LEVEL="2"
python ml_model/train_model.py --samples_per_class 25 --epochs 5 --fine_tune_epochs 0
```

### Full Training (all 70,295 images — best accuracy, ~8-13 hours on CPU)
```powershell
$env:TF_ENABLE_ONEDNN_OPTS="0"
$env:TF_CPP_MIN_LOG_LEVEL="2"
python ml_model/train_model.py --epochs 20 --fine_tune_epochs 10
```

### Training Arguments

| Argument              | Default              | Description                              |
|-----------------------|----------------------|------------------------------------------|
| `--data_dir`          | `Plant_Disease_Dataset` | Path to dataset folder                 |
| `--epochs`            | `15`                 | Phase 1 training epochs                  |
| `--batch_size`        | `32`                 | Batch size                               |
| `--fine_tune_epochs`  | `10`                 | Phase 2 fine-tuning epochs (0 to skip)   |
| `--samples_per_class` | `None` (all)         | Limit images per class for quick testing |

### Output files
- `ml_model/crop_disease_model.h5` — trained Keras model
- `ml_model/class_names.json` — 38 class names mapped to model output indices

> **Achieved accuracy:** ~77% validation accuracy with 25 images/class (5 epochs). Full training achieves 90%+ from epoch 1.

---

## ▶️ Running the Application

```bash
python run.py
```

On startup the app will:
1. Create the MySQL database if it doesn't exist
2. Create all tables via SQLAlchemy
3. Seed 38 disease entries into the database
4. Create the default admin account
5. Start the Flask development server

Access at: **http://localhost:5000**

---

## 📱 Usage Guide

### Farmer
1. **Register** at `/register` — create a free account
2. **Login** at `/login`
3. **Detect Disease** at `/detect`:
   - Drag & drop or click to upload a leaf image
   - Click **Analyze Disease**
   - View disease name, confidence score, symptoms, causes, treatments
   - Click **Read Aloud** to hear results in your selected language
4. **Dashboard** at `/dashboard` — view history, charts, crop records
5. **Download Report** — PDF of all your detection history
6. **Language Selector** in navbar — switch language instantly

### Chatbot
- Click the 🤖 robot button (bottom-right corner) on any page
- Type or click the 🎤 mic button to speak your question
- Get instant answers about crop diseases

### Admin
1. Login with `admin@cropguard.ai` / `admin123`
2. **Manage Users** — view/delete registered farmers
3. **Disease Database** — add, edit, delete disease entries
4. **Analytics** — system-wide stats and charts

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint    | Description         |
|--------|-------------|---------------------|
| POST   | `/register` | Register new farmer |
| POST   | `/login`    | User login          |
| GET    | `/logout`   | Logout              |
| GET/POST | `/profile` | View/update profile |

### Farmer APIs
| Method | Endpoint                | Description                      |
|--------|-------------------------|----------------------------------|
| POST   | `/api/detect`           | Detect disease from image upload |
| GET    | `/api/history`          | Paginated detection history      |
| GET    | `/api/stats`            | Disease distribution stats       |
| GET    | `/api/download-report`  | Download PDF report              |
| GET/POST | `/api/crop-records`   | Manage crop records              |

### Public APIs
| Method | Endpoint           | Description              |
|--------|--------------------|--------------------------|
| GET    | `/api/diseases`    | List all 38 diseases     |
| GET    | `/api/disease/<id>`| Get single disease detail|
| POST   | `/api/chatbot`     | Chat with AI assistant   |

### Admin APIs
| Method | Endpoint                      | Description              |
|--------|-------------------------------|--------------------------|
| GET    | `/admin/api/users`            | List all farmers         |
| DELETE | `/admin/api/users/<id>`       | Delete farmer            |
| GET/POST | `/admin/api/diseases`       | List / add diseases      |
| PUT/DELETE | `/admin/api/diseases/<id>` | Update / delete disease  |
| GET    | `/admin/api/analytics`        | System analytics         |

---

## 🔐 Default Credentials

| Role  | Email                | Password   |
|-------|----------------------|------------|
| Admin | admin@cropguard.ai   | admin123   |

> ⚠️ Change the admin password immediately in production!

---

## 🛡️ Security Features

- Passwords hashed with **bcrypt**
- **JWT** token authentication for API endpoints
- **Flask-Login** session management
- **SQLAlchemy ORM** prevents SQL injection
- File upload validation (type + size checks)
- Role-based access control (Farmer / Admin)
- CORS protection via Flask-CORS

---

## 🐛 Troubleshooting

**Database connection error**
```
Check MySQL is running → verify .env credentials → ensure DB exists
```

**Model not found / demo mode**
```powershell
python ml_model/train_model.py --samples_per_class 25 --epochs 5 --fine_tune_epochs 0
```

**scipy import error**
```bash
pip install scipy
```

**Port already in use**
```python
# In run.py, change:
app.run(host='0.0.0.0', port=5001, debug=True)
```

**PowerShell `&&` syntax error**
```powershell
# Use semicolons or separate lines in PowerShell:
$env:TF_ENABLE_ONEDNN_OPTS="0"
python ml_model/train_model.py
```

**Speech recognition not working**
- Use Chrome or Edge (Firefox has limited Web Speech API support)
- Allow microphone access when browser prompts

**Google Translate not loading**
- Check internet connection (requires access to `translate.google.com`)
- Disable browser extensions that may block translation scripts

---

## 🚀 Deployment

### Production checklist
1. Set strong `SECRET_KEY` and `JWT_SECRET_KEY` in `.env`
2. Set `debug=False` in `run.py`
3. Train model on full dataset for best accuracy
4. Use a production WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```
5. Configure MySQL with production credentials
6. Enable HTTPS/SSL (use Nginx as reverse proxy)
7. Store uploaded images on cloud storage (AWS S3 / Google Cloud Storage)
8. Host model on a GPU server for faster inference

### Environment variables for production
```env
SECRET_KEY=<strong-random-key>
JWT_SECRET_KEY=<strong-random-jwt-key>
DB_PASSWORD=<strong-db-password>
```

---

## 📄 License

This project is for educational purposes. Modify and use as needed.

---

**Built with ❤️ for Farmers — CropGuard AI**
