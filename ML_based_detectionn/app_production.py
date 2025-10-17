#!/usr/bin/env python3
"""
Production-ready Flask application with rate limiting and enhanced security
"""
import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import joblib
from feature_extraction import extract_features

# Load environment variables
load_dotenv()

# Initialize Flask app with secure configuration
app = Flask(__name__)

# Secure configuration - never enable debug in production
app.config.update(
    ENV=os.getenv('FLASK_ENV', 'production'),
    DEBUG=False,  # Explicitly disable debug mode
    SECRET_KEY=os.getenv('SECRET_KEY', os.urandom(24)),
    UPLOAD_FOLDER=os.getenv('UPLOAD_FOLDER', 'uploads'),
    MAX_CONTENT_LENGTH=10 * 1024 * 1024  # 10MB max file size
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Create upload folder safely
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'exe', 'dll'}

# Load the ML model with error handling
try:
    model_path = os.path.join('ML_model', 'malwareclassifier-V2.pkl')
    if not os.path.exists(model_path):
        logging.warning(f"Model file not found at {model_path}. Please train and save a model first.")
        model = None
    else:
        model = joblib.load(model_path)
        logging.info("Model loaded successfully")
except Exception as e:
    logging.error(f"Failed to load model: {str(e)}")
    model = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@limiter.limit("30 per minute")
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
@limiter.limit("10 per minute")  # Stricter limit for analysis endpoint
def analyze():
    # Check if a file is uploaded
    if 'file' in request.files:
        file = request.files['file']
        
        if file.filename == '' or not allowed_file(file.filename):
            return render_template('index.html', error="Unsupported file type. Please upload .exe or .dll files.")
        
        # Construct the full file path
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        # Save the file
        try:
            file.save(file_path)
        except Exception as e:
            logging.error(f"Error saving file: {str(e)}")
            return render_template('index.html', error="Error saving uploaded file.")

        # Use the model for prediction if the file is `.exe` or `.dll`
        if allowed_file(file.filename):
            if model is None:
                return render_template('index.html', error="Model not loaded. Please contact administrator.")
            try:
                features = extract_features(file_path)
                prediction = model.predict(features)
                result = {
                    "type": "file",
                    "prediction": "Malware" if prediction[0] == 1 else "Safe",
                    "file_name": file.filename
                }
                
                # Log the analysis
                logging.info(f"Analysis completed: {file.filename} - {result['prediction']}")
                
            except Exception as e:
                logging.error(f"Error during prediction: {str(e)}")
                return render_template('index.html', error=f"Error analyzing file: {str(e)}")
            finally:
                # Clean up uploaded file
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logging.error(f"Error cleaning up file: {str(e)}")

        return render_template('result.html', result=result)

    return render_template('index.html', error="No file uploaded.")

@app.route('/health')
@limiter.exempt
def health():
    """Health check endpoint for monitoring"""
    return {
        'status': 'healthy',
        'model_loaded': model is not None
    }, 200

if __name__ == '__main__':
    # Get environment settings with secure defaults
    env = os.getenv('FLASK_ENV', 'production')
    debug = env == 'development'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))

    app.run(
        host=host,
        port=port,
        debug=debug
    )
#!/usr/bin/env python3
"""
Production-ready Flask application with rate limiting and enhanced security
"""
import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import joblib
from feature_extraction import extract_features
from quarantine_manager import QuarantineManager
from file_cleaner import FileCleaner

# Load environment variables
load_dotenv()

# Initialize Flask app with secure configuration
app = Flask(__name__)

# Secure configuration - never enable debug in production
app.config.update(
    ENV=os.getenv('FLASK_ENV', 'production'),
    DEBUG=False,  # Explicitly disable debug mode
    SECRET_KEY=os.getenv('SECRET_KEY', os.urandom(24)),
    UPLOAD_FOLDER=os.getenv('UPLOAD_FOLDER', 'uploads'),
    MAX_CONTENT_LENGTH=10 * 1024 * 1024  # 10MB max file size
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Create upload folder safely
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'exe', 'dll', 'txt', 'pdf'}

# Load the ML model with error handling
try:
    # Support multiple relative locations
    possible_paths = [
        os.path.join('ML_model', 'malwareclassifier-V2.pkl'),
        os.path.join(os.path.dirname(__file__), 'ML_model', 'malwareclassifier-V2.pkl')
    ]
    model_path = next((p for p in possible_paths if os.path.exists(p)), None)
    if model_path is None:
        logging.warning(f"Model file not found. Tried: {possible_paths}. Please train and save a model first.")
        model = None
        scaler = None
    else:
        model = joblib.load(model_path)
        logging.info(f"Model loaded successfully from {model_path}")
        # Load scaler if present
        scaler_path = model_path.replace('malwareclassifier-V2.pkl', 'scaler.pkl')
        scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None
        if scaler is None:
            logging.warning("Scaler not found - using unscaled features")
except Exception as e:
    logging.error(f"Failed to load model: {str(e)}")
    model = None
    scaler = None

# Initialize helpers
quarantine_manager = QuarantineManager()
file_cleaner = FileCleaner()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@limiter.limit("30 per minute")
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Stricter limit for analysis endpoint
def analyze():
    # Redirect GET requests to home page
    if request.method == 'GET':
        flash('Please use the form to submit your analysis.', 'info')
        return redirect(url_for('index'))
    
    # Check if a file is uploaded
    if 'file' in request.files:
        file = request.files['file']
        
        if file.filename == '' or not allowed_file(file.filename):
            return render_template('index.html', error="Unsupported file type. Please upload .exe, .dll, .txt or .pdf files.")
        
        # Construct the full file path
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        # Save the file
        try:
            file.save(file_path)
        except Exception as e:
            logging.error(f"Error saving file: {str(e)}")
            return render_template('index.html', error="Error saving uploaded file.")

        file_ext = file.filename.rsplit('.', 1)[1].lower()

        if file_ext in {'exe', 'dll'}:
            if model is None:
                return render_template('index.html', error="Model not loaded. Please contact administrator.")
            try:
                features = extract_features(file_path)
                # Align to expected feature order
                if hasattr(model, 'feature_names_in_'):
                    features = features.reindex(columns=list(model.feature_names_in_), fill_value=0)
                # Scale if scaler present
                features_scaled = scaler.transform(features) if scaler is not None else features
                prediction = model.predict(features_scaled)
                proba = model.predict_proba(features_scaled)[0]
                confidence = (proba[1] if int(prediction[0]) == 1 else proba[0]) * 100
                result = {
                    "type": "file",
                    "prediction": "Malware" if int(prediction[0]) == 1 else "Safe",
                    "file_name": file.filename,
                    "confidence": f"{confidence:.1f}%"
                }
                logging.info(f"Analysis completed: {file.filename} - {result['prediction']} ({confidence:.1f}%)")
            except Exception as e:
                logging.error(f"Error during prediction: {str(e)}")
                return render_template('index.html', error=f"Error analyzing file: {str(e)}")

        elif file_ext == 'txt':
            # Simple keyword heuristic for text
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000)
                content_lower = content.lower()
                suspicious_keywords = ['malware', 'virus', 'exploit', 'payload', 'shell', 'backdoor', 'ransomware']
                found = [kw for kw in suspicious_keywords if kw in content_lower]
                is_suspicious = len(found) >= 3
                result = {
                    "type": "text",
                    "prediction": "Suspicious" if is_suspicious else "Safe",
                    "file_name": file.filename,
                    "confidence": f"{min(len(found)*20,95)}%" if is_suspicious else "90%"
                }
            except Exception as e:
                logging.error(f"Error analyzing text: {e}")
                return render_template('index.html', error=f"Error analyzing text: {str(e)}")

        elif file_ext == 'pdf':
            # Lightweight heuristic analysis for PDF
            try:
                with open(file_path, 'rb') as f:
                    pdf_data = f.read()
                pdf_text = pdf_data.decode('latin-1', errors='ignore')
                score = 0
                if '/JavaScript' in pdf_text or '/JS' in pdf_text:
                    score += 2
                if '/OpenAction' in pdf_text or '/AA' in pdf_text:
                    score += 2
                if '/Launch' in pdf_text:
                    score += 3
                is_suspicious = score >= 3
                result = {
                    "type": "pdf",
                    "prediction": "Suspicious" if is_suspicious else "Safe",
                    "file_name": file.filename,
                    "confidence": f"{min(score*15,95)}%" if is_suspicious else "90%"
                }
            except Exception as e:
                logging.error(f"Error analyzing PDF: {e}")
                return render_template('index.html', error=f"Error analyzing PDF: {str(e)}")
        else:
            return render_template('index.html', error="Unsupported file type.")

        return render_template('result.html', result=result)

    return render_template('index.html', error="No file uploaded.")

@app.route('/health')
@limiter.exempt
def health():
    """Health check endpoint for monitoring"""
    return {
        'status': 'healthy',
        'model_loaded': model is not None
    }, 200

if __name__ == '__main__':
    # Get environment settings with secure defaults
    env = os.getenv('FLASK_ENV', 'production')
    debug = env == 'development'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))

    app.run(
        host=host,
        port=port,
        debug=debug
    )