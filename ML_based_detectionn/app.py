import os
import logging
import pefile
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, flash, send_file, jsonify
import joblib
import numpy as np
import tempfile
import zipfile
import tarfile
import shutil
import io
from pathlib import Path
from feature_extraction import extract_features
from quarantine_manager import QuarantineManager
from file_cleaner import FileCleaner
import ast
from ml_worker import submit_job, get_job_status

# Archive scan limits (to avoid resource exhaustion)
MAX_ARCHIVE_ENTRIES = int(os.getenv('MAX_ARCHIVE_ENTRIES', 100))
MAX_ARCHIVE_UNCOMPRESSED_BYTES = int(os.getenv('MAX_ARCHIVE_UNCOMPRESSED_BYTES', 50 * 1024 * 1024))  # 50MB


def analyze_python_ast(content: str):
    """Perform lightweight AST static analysis on Python source.
    Returns a list of suspicious indicators found.
    """
    indicators = []
    try:
        tree = ast.parse(content)
    except Exception:
        return indicators

    for node in ast.walk(tree):
        # Look for exec/eval calls
        if isinstance(node, ast.Call):
            try:
                func = node.func
                if isinstance(func, ast.Name) and func.id in ('exec', 'eval'):
                    indicators.append(func.id)
                elif isinstance(func, ast.Attribute):
                    attr = func.attr.lower()
                    if attr in ('system', 'popen', 'call', 'run'):
                        indicators.append(f'subprocess.{attr}')
            except Exception:
                continue
        # Look for import of suspicious modules
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name in ('ctypes', 'socket', 'subprocess'):
                    indicators.append(f'import:{n.name}')
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split('.')[0] in ('ctypes', 'socket', 'subprocess'):
                indicators.append(f'from:{node.module}')

    return list(set(indicators))

# Load environment variables
load_dotenv()

# Import polymorphic detection
from polymorphic_detection import extract_polymorphic_features, analyze_polymorphic_indicators

# Initialize Flask app with secure configuration
app = Flask(__name__)

# Secure configuration - never enable debug in production
app.config.update(
    ENV=os.getenv('FLASK_ENV', 'production'),
    DEBUG=False,  # Explicitly disable debug mode
    SECRET_KEY=os.getenv('SECRET_KEY', os.urandom(24)),
    UPLOAD_FOLDER=os.getenv('UPLOAD_FOLDER', 'uploads'),
    MAX_CONTENT_LENGTH=25 * 1024 * 1024  # 25MB max file size to handle larger samples
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Add a file handler for ML analysis logs
ml_log_path = os.path.join(os.path.dirname(__file__), 'ml_analysis.log')
file_handler = logging.FileHandler(ml_log_path)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

# Create upload folder safely
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions - Including common benign file types
ALLOWED_EXTENSIONS = {
    # Executables and libraries
    'exe', 'dll',
    # Document formats
    'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    # Image formats
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg',
    # Archive formats
    'zip', 'tar', 'gz', 'tar.gz', 'rar', '7z',
    # Source code
    'py', 'js', 'html', 'css', 'json', 'xml',
    # Other common formats
    'csv', 'md', 'sql', 'log'
}

# Load the ML model and scaler with error handling
try:
    # Try different possible paths for the model
    possible_paths = [
        os.path.join('ML_model', 'malwareclassifier-V2.pkl'),
        os.path.join('ML_based_detectionn', 'ML_model', 'malwareclassifier-V2.pkl'),
        os.path.join(os.path.dirname(__file__), 'ML_model', 'malwareclassifier-V2.pkl')
    ]
    
    model_path = None
    for path in possible_paths:
        if os.path.exists(path):
            model_path = path
            break
    
    if model_path is None:
        logging.warning(f"Model file not found. Tried: {possible_paths}. Please train and save a model first.")
        model = None
        scaler = None
    else:
        model = joblib.load(model_path)
        logging.info(f"Advanced ensemble model loaded successfully from {model_path}")
        
        # Try to load scaler (co-located with model)
        scaler_path = model_path.replace('malwareclassifier-V2.pkl', 'scaler.pkl')
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
            logging.info(f"Feature scaler loaded from {scaler_path}")
        else:
            scaler = None
            logging.warning("Scaler not found - will use unscaled features")
            
except Exception as e:
    logging.error(f"Failed to load model: {str(e)}")
    model = None
    scaler = None

# Initialize helpers
quarantine_manager = QuarantineManager()
file_cleaner = FileCleaner()


def analyze_text_content(content: str, safe_filename: str) -> dict:
    """Analyze text content and return result dict. Extracted to helper for testing."""
    suspicious_keywords = ['malware', 'virus', 'exploit', 'payload', 'shell', 'backdoor',
                          'ransomware', 'trojan', 'rootkit', 'keylogger', 'botnet', 'malicious']

    content_lower = content.lower()
    found_keywords = [kw for kw in suspicious_keywords if kw in content_lower]

    # Explicitly detect EICAR test string or common signature fragments
    eicar_signatures = ['eicar', 'x5o!p@', 'eicar-standard-antivirus-test-file', 'x5o!p%@ap']
    found_eicar = any(sig in content_lower for sig in eicar_signatures)

    # Determine if suspicious: mark suspicious if EICAR signature found or keywords >= 1
    is_suspicious = found_eicar or len(found_keywords) >= 1

    # Compute a better-confidence estimate for text heuristics
    if found_eicar:
        confidence_text = "99%"
    elif len(found_keywords) > 0:
        # base confidence 60% plus a boost per keyword, cap at 95
        confidence_text = f"{min(60 + len(found_keywords) * 10, 95)}%"
    else:
        confidence_text = "90%"

    result = {
        "type": "text",
        "prediction": "Suspicious" if is_suspicious else "Safe",
        "file_name": safe_filename,
        "confidence": confidence_text,
        "note": "Text file analysis - improved heuristic and EICAR detection",
        "found_keywords": found_keywords
    }

    return result


def process_saved_file(file_path: str, safe_filename: str) -> dict:
    """Process a saved file path and return the analysis result dict.
    This encapsulates the per-file analysis logic so it can be called from sync or async paths.
    """
    # Replicate the logic that was in the analyze() route, but operate on file_path/safe_filename directly.
    # Determine file extension
    lower_name = safe_filename.lower()
    if lower_name.endswith('.tar.gz'):
        file_ext = 'tar.gz'
    elif lower_name.endswith('.tar'):
        file_ext = 'tar'
    elif lower_name.endswith('.zip'):
        file_ext = 'zip'
    else:
        file_ext = safe_filename.rsplit('.', 1)[1].lower()

    # Handle text
    if file_ext == 'txt':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10000)
            result = analyze_text_content(content, safe_filename)
        except Exception as e:
            result = {"type": "text", "prediction": "Unknown", "file_name": safe_filename, "confidence": "N/A", "note": str(e)}
        result['file_path'] = file_path
        return result

    # For other types, call through the route's logic by reusing sections from analyze()
    # To avoid duplication, we will call analyze() via an internal approach is non-trivial; instead re-use key primitives here.
    if file_ext == 'pdf':
        try:
            with open(file_path, 'rb') as f:
                pdf_data = f.read()
            pdf_text = pdf_data.decode('latin-1', errors='ignore')
            suspicious_count = 0
            findings = []
            if '/JavaScript' in pdf_text or '/JS' in pdf_text:
                suspicious_count += 2
                findings.append('Contains JavaScript')
            if '/OpenAction' in pdf_text or '/AA' in pdf_text:
                suspicious_count += 2
                findings.append('Contains auto-action')
            if '/EmbeddedFile' in pdf_text:
                suspicious_count += 1
                findings.append('Contains embedded files')
            if '/Launch' in pdf_text:
                suspicious_count += 3
                findings.append('Contains launch action (HIGH RISK)')
            if '/URI' in pdf_text:
                suspicious_count += 1
                findings.append('Contains URI/URL')
            pdf_lower = pdf_text.lower()
            malicious_keywords = ['exploit', 'payload', 'shell', 'malware', 'backdoor', 'rootkit']
            found_mal_keywords = [kw for kw in malicious_keywords if kw in pdf_lower]
            if found_mal_keywords:
                suspicious_count += len(found_mal_keywords)
                findings.append(f"Suspicious keywords: {', '.join(found_mal_keywords)}")
            if '/Encrypt' in pdf_text:
                findings.append('Encrypted PDF')
            file_size = len(pdf_data)
            if file_size > 10 * 1024 * 1024:
                suspicious_count += 1
                findings.append('Large file size')
            is_suspicious = suspicious_count >= 3
            risk_level = 'HIGH RISK' if suspicious_count >= 5 else ('MEDIUM RISK' if suspicious_count >= 3 else 'LOW RISK')
            result = {'type': 'pdf', 'prediction': 'Suspicious' if is_suspicious else 'Safe', 'file_name': safe_filename, 'confidence': f"{min(suspicious_count * 15, 95)}%" if is_suspicious else f"{max(100 - suspicious_count * 10, 85)}%", 'note': f'PDF analysis - {risk_level}', 'findings': findings if findings else ['No suspicious indicators found'], 'file_path': file_path}
            if wants_json:
                return jsonify(result)
            return render_template('result.html', result=result)
        except Exception as e:
            result = {'type': 'pdf', 'prediction': 'Unknown', 'file_name': safe_filename, 'confidence': 'N/A', 'note': str(e), 'file_path': file_path}
            if wants_json:
                return jsonify(result)
            return render_template('result.html', result=result)

    # Executable files (.exe, .dll)
    if file_ext in ('exe', 'dll'):
        try:
            # Extract standard features for ML model
            features = extract_features(file_path)
            if hasattr(model, 'feature_names_in_'):
                expected_columns = list(model.feature_names_in_)
                features = features.reindex(columns=expected_columns, fill_value=0)
            is_malware, confidence, raw_label, probabilities = predict_features(features, model, scaler)
            
            # Extract and analyze polymorphic features
            poly_features = extract_polymorphic_features(file_path)
            is_polymorphic, poly_risk_score, poly_indicators = analyze_polymorphic_indicators(poly_features, file_path)
            
            # Combine results
            final_confidence = max(confidence, poly_risk_score * 100)
            is_threat = is_malware or is_polymorphic
            
            result = {
                'type': 'file',
                'prediction': 'Malware' if is_threat else 'Safe',
                'file_name': safe_filename,
                'confidence': f"{final_confidence:.1f}%",
                'model': 'NeuroShield Model + Polymorphic Detection',
                'raw_prediction': raw_label,
                'probabilities': probabilities,
                'file_path': file_path,
                'polymorphic_analysis': {
                    'is_polymorphic': is_polymorphic,
                    'risk_score': f"{poly_risk_score:.2f}",
                    'indicators': poly_indicators
                }
            }
            if wants_json:
                return jsonify(result)
            return render_template('result.html', result=result)
        except pefile.PEFormatError as pe_err:
            result = {'type': 'file', 'prediction': 'Unknown', 'file_name': safe_filename, 'confidence': 'N/A', 'model': 'NeuroShield Model', 'note': 'File appears not to be a valid PE executable or is corrupted', 'file_path': file_path}
            if wants_json:
                return jsonify(result)
            return render_template('result.html', result=result)
        except Exception as e:
            result = {'type': 'file', 'prediction': 'Unknown', 'file_name': safe_filename, 'confidence': 'N/A', 'model': 'NeuroShield Model', 'note': str(e), 'file_path': file_path}
            if wants_json:
                return jsonify(result)
            return render_template('result.html', result=result)

    # Python files
    if file_ext == 'py':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(20000)
            result = analyze_text_content(content, safe_filename)
            py_indicators = analyze_python_ast(content)
            if py_indicators:
                result['prediction'] = 'Suspicious'
                result['note'] = result.get('note', '') + ' | AST indicators found'
                result['confidence'] = '95%'
                result['found_indicators'] = py_indicators
            result['file_path'] = file_path
            return result
        except Exception as e:
            return {'type': 'py', 'prediction': 'Unknown', 'file_name': safe_filename, 'confidence': 'N/A', 'note': str(e), 'file_path': file_path}

    # Archives (zip/tar)
    if file_ext in ('zip', 'tar', 'tar.gz', 'gz'):
        findings = []
        any_suspicious = False
        highest_conf = 0.0
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                entry_count = 0
                total_uncompressed = 0
                if file_ext == 'zip':
                    with zipfile.ZipFile(file_path, 'r') as z:
                        for zi in z.infolist():
                            entry_count += 1
                            if entry_count > MAX_ARCHIVE_ENTRIES:
                                raise Exception('Archive has too many entries')
                            if zi.is_dir():
                                continue
                            try:
                                data = z.read(zi)
                            except Exception:
                                continue
                            total_uncompressed += len(data)
                            if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                                raise Exception('Archive total uncompressed size exceeds limit')
                            if len(data) >= 2 and data[:2] == b'MZ' and model is not None:
                                temp_pe = Path(tmpdir) / Path(zi.filename).name
                                temp_pe.write_bytes(data)
                                try:
                                    feats = extract_features(str(temp_pe))
                                    is_malware, confidence, raw_label, probs = predict_features(feats, model, scaler)
                                    findings.append({'file': zi.filename, 'prediction': 'Malware' if is_malware else 'Safe', 'confidence': f"{confidence:.1f}%"})
                                    if is_malware:
                                        any_suspicious = True
                                        highest_conf = max(highest_conf, confidence)
                                except Exception:
                                    pass
                            else:
                                try:
                                    text = data.decode('latin-1', errors='ignore')
                                    txt_res = analyze_text_content(text, zi.filename)
                                    findings.append({'file': zi.filename, 'prediction': txt_res['prediction'], 'confidence': txt_res['confidence']})
                                    if txt_res['prediction'] != 'Safe':
                                        any_suspicious = True
                                        try:
                                            c = float(txt_res['confidence'].strip('%'))
                                            highest_conf = max(highest_conf, c)
                                        except Exception:
                                            highest_conf = max(highest_conf, 50.0)
                                except Exception:
                                    continue
                else:
                    with tarfile.open(file_path, 'r:*') as tar:
                        for member in tar.getmembers():
                            entry_count += 1
                            if entry_count > MAX_ARCHIVE_ENTRIES:
                                raise Exception('Archive has too many entries')
                            if member.isdir():
                                continue
                            f = tar.extractfile(member)
                            if f is None:
                                continue
                            data = f.read()
                            total_uncompressed += len(data)
                            if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                                raise Exception('Archive total uncompressed size exceeds limit')
                            if len(data) >= 2 and data[:2] == b'MZ' and model is not None:
                                temp_pe = Path(tmpdir) / Path(member.name).name
                                temp_pe.write_bytes(data)
                                try:
                                    feats = extract_features(str(temp_pe))
                                    is_malware, confidence, raw_label, probs = predict_features(feats, model, scaler)
                                    findings.append({'file': member.name, 'prediction': 'Malware' if is_malware else 'Safe', 'confidence': f"{confidence:.1f}%"})
                                    if is_malware:
                                        any_suspicious = True
                                        highest_conf = max(highest_conf, confidence)
                                except Exception:
                                    pass
                            else:
                                try:
                                    text = data.decode('latin-1', errors='ignore')
                                    txt_res = analyze_text_content(text, member.name)
                                    findings.append({'file': member.name, 'prediction': txt_res['prediction'], 'confidence': txt_res['confidence']})
                                    if txt_res['prediction'] != 'Safe':
                                        any_suspicious = True
                                        try:
                                            c = float(txt_res['confidence'].strip('%'))
                                            highest_conf = max(highest_conf, c)
                                        except Exception:
                                            highest_conf = max(highest_conf, 50.0)
                                except Exception:
                                    continue

            return {'type': 'archive', 'prediction': 'Suspicious' if any_suspicious else 'Safe', 'file_name': safe_filename, 'confidence': f"{highest_conf:.1f}%" if any_suspicious else '90%', 'findings': findings if findings else ['No suspicious indicators found'], 'file_path': file_path}
        except Exception as e:
            return {'type': 'archive', 'prediction': 'Unknown', 'file_name': safe_filename, 'confidence': 'N/A', 'findings': [str(e)], 'file_path': file_path}

    # Default unsupported
    return {'type': 'unknown', 'prediction': 'Unknown', 'file_name': safe_filename, 'confidence': 'N/A', 'note': 'Unsupported file type', 'file_path': file_path}



def predict_features(features, model_obj, scaler_obj=None):
    """Predict from a feature DataFrame using model and optional scaler.
    Returns a tuple: (is_malware_bool, confidence_float, raw_label, probabilities_or_none)
    """
    try:
        # Align features and scale if scaler provided
        features_arr = features
        if scaler_obj is not None:
            try:
                features_arr = scaler_obj.transform(features)
            except Exception as e:
                logging.warning(f"Scaler transform failed in helper: {e}")
                features_arr = features

        # prediction raw
        prediction = model_obj.predict(features_arr)
        raw_prediction = prediction[0]

        prediction_proba = None
        confidence = None
        pred_label = raw_prediction

        if hasattr(model_obj, 'predict_proba'):
            try:
                prediction_proba = model_obj.predict_proba(features_arr)[0]
                pred_index = int(np.argmax(prediction_proba))
                confidence = float(prediction_proba[pred_index]) * 100.0
                if hasattr(model_obj, 'classes_'):
                    try:
                        pred_label = model_obj.classes_[pred_index]
                    except Exception:
                        pass
            except Exception as e:
                logging.warning(f"predict_proba failed in helper: {e}")

        else:
            # fallback to decision_function
            if hasattr(model_obj, 'decision_function'):
                try:
                    df = model_obj.decision_function(features_arr)
                    score = float(df[0]) if hasattr(df, '__len__') and len(df) == 1 else float(df)
                    prob = 1.0 / (1.0 + np.exp(-score))
                    confidence = prob * 100.0
                except Exception as e:
                    logging.warning(f"decision_function fallback failed in helper: {e}")
                    confidence = 100.0

        # Normalize predicted label to boolean malware flag
        is_malware = False
        try:
            is_malware = int(pred_label) == 1
        except Exception:
            if str(pred_label).lower() in ('malware', 'malicious', '1', 'true'):
                is_malware = True

        # Ensure confidence is present
        if confidence is None:
            confidence = 100.0

        return is_malware, float(confidence), pred_label, (prediction_proba.tolist() if prediction_proba is not None else None)

    except Exception as err:
        logging.error(f"Error in predict_features helper: {err}")
        return False, 0.0, None, None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    # Redirect GET requests to home page
    if request.method == 'GET':
        return jsonify({"error": "Use POST method"}) if request.headers.get('Accept') == 'application/json' else redirect(url_for('index'))
    
    # Decide response format early so all handlers can use it
    wants_json = 'application/json' in request.headers.get('Accept', '') or \
                request.headers.get('Content-Type', '').startswith('multipart/form-data')
    logging.info("Request headers: %s", dict(request.headers))
    logging.info("wants_json=%s", wants_json)
    
    try:
        # Check if a file is uploaded
        if 'file' not in request.files:
            error = "No file uploaded. Please select a file."
            logging.warning(error)
            return jsonify({"error": error}) if wants_json else render_template('index.html', error=error)
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            error = "No file selected. Please choose a file."
            logging.warning(error)
            return jsonify({"error": error}) if wants_json else render_template('index.html', error=error)
        
        # Check file extension
        if not allowed_file(file.filename):
            error = f"Invalid file type. Supported types: .exe, .dll, .txt, .pdf, .py, .zip, .tar(.gz). You uploaded: {file.filename}"
            logging.warning(error)
            return jsonify({"error": error}) if wants_json else render_template('index.html', error=error)
        
        # Check if model is loaded
        if model is None:
            error = "Malware detection model is not loaded. Please contact administrator."
            logging.error(error)
            return jsonify({"error": error}) if wants_json else render_template('index.html', error=error)
        
    # (wants_json already determined above)

    # Construct the full file path with sanitized filename
        safe_filename = os.path.basename(file.filename)  # Prevent directory traversal
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        # Save the file
        logging.info(f"Saving file: {safe_filename}")
        file.save(file_path)
        logging.info(f"File saved successfully: {file_path}")
        
        # Determine file extension (support multi-part like .tar.gz)
        lower_name = safe_filename.lower()
        if lower_name.endswith('.tar.gz'):
            file_ext = 'tar.gz'
        elif lower_name.endswith('.tar'):
            file_ext = 'tar'
        elif lower_name.endswith('.zip'):
            file_ext = 'zip'
        else:
            file_ext = safe_filename.rsplit('.', 1)[1].lower()
        
        if file_ext == 'txt':
            # Handle text files - simple content analysis
            logging.info(f"Analyzing text file: {safe_filename}")
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000)  # Read first 10KB
                
                # Improved heuristic analysis for text files
                suspicious_keywords = ['malware', 'virus', 'exploit', 'payload', 'shell', 'backdoor',
                                      'ransomware', 'trojan', 'rootkit', 'keylogger', 'botnet', 'malicious']

                content_lower = content.lower()
                found_keywords = [kw for kw in suspicious_keywords if kw in content_lower]

                # Explicitly detect EICAR test string or common signature fragments
                eicar_signatures = ['eicar', 'x5o!p@', 'eicar-standard-antivirus-test-file', 'x5o!p%@ap']
                found_eicar = any(sig in content_lower for sig in eicar_signatures)

                # Determine if suspicious: mark suspicious if EICAR signature found or keywords >= 1
                is_suspicious = found_eicar or len(found_keywords) >= 1

                # Compute a better-confidence estimate for text heuristics
                if found_eicar:
                    confidence_text = "99%"
                elif len(found_keywords) > 0:
                    # base confidence 60% plus a boost per keyword, cap at 95
                    confidence_text = f"{min(60 + len(found_keywords) * 10, 95)}%"
                else:
                    confidence_text = "90%"

                result = {
                    "type": "text",
                    "prediction": "Suspicious" if is_suspicious else "Safe",
                    "file_name": safe_filename,
                    "confidence": confidence_text,
                    "note": "Text file analysis - improved heuristic and EICAR detection",
                    "found_keywords": found_keywords
                }
                
                logging.info(f"Text file analysis complete: {safe_filename} - {result['prediction']}")
            
            except Exception as txt_error:
                logging.error(f"Error reading text file: {txt_error}")
                result = {
                    "type": "text",
                    "prediction": "Unknown",
                    "file_name": safe_filename,
                    "confidence": "N/A",
                    "note": "Could not analyze text file"
                }
                if wants_json:
                    return jsonify(result)
                return render_template('result.html', result=result)
        
        elif file_ext == 'pdf':
            # Handle PDF files - comprehensive analysis
            logging.info(f"Analyzing PDF file: {safe_filename}")
            
            try:
                # Read PDF file in binary mode
                with open(file_path, 'rb') as f:
                    pdf_data = f.read()
                
                # Convert to string for analysis
                pdf_text = pdf_data.decode('latin-1', errors='ignore')
                
                # Suspicious indicators for PDFs
                suspicious_count = 0
                findings = []
                
                # Check for JavaScript (often used in malicious PDFs)
                if '/JavaScript' in pdf_text or '/JS' in pdf_text:
                    suspicious_count += 2
                    findings.append("Contains JavaScript")
                
                # Check for auto-actions
                if '/OpenAction' in pdf_text or '/AA' in pdf_text:
                    suspicious_count += 2
                    findings.append("Contains auto-action")
                
                # Check for embedded files
                if '/EmbeddedFile' in pdf_text:
                    suspicious_count += 1
                    findings.append("Contains embedded files")
                
                # Check for launch actions
                if '/Launch' in pdf_text:
                    suspicious_count += 3
                    findings.append("Contains launch action (HIGH RISK)")
                
                # Check for URI/URL actions
                if '/URI' in pdf_text:
                    suspicious_count += 1
                    findings.append("Contains URI/URL")
                
                # Check for suspicious keywords
                pdf_lower = pdf_text.lower()
                malicious_keywords = ['exploit', 'payload', 'shell', 'malware', 'backdoor', 'rootkit']
                found_mal_keywords = [kw for kw in malicious_keywords if kw in pdf_lower]
                if found_mal_keywords:
                    suspicious_count += len(found_mal_keywords)
                    findings.append(f"Suspicious keywords: {', '.join(found_mal_keywords)}")
                
                # Check for encryption
                if '/Encrypt' in pdf_text:
                    findings.append("Encrypted PDF")
                
                # Check file size (unusually large PDFs can be suspicious)
                file_size = len(pdf_data)
                if file_size > 10 * 1024 * 1024:  # > 10MB
                    suspicious_count += 1
                    findings.append("Large file size")
                
                # Determine classification
                is_suspicious = suspicious_count >= 3
                risk_level = "HIGH RISK" if suspicious_count >= 5 else ("MEDIUM RISK" if suspicious_count >= 3 else "LOW RISK")
                
                result = {
                    "type": "pdf",
                    "prediction": "Suspicious" if is_suspicious else "Safe",
                    "file_name": safe_filename,
                    "confidence": f"{min(suspicious_count * 15, 95)}%" if is_suspicious else f"{max(100 - suspicious_count * 10, 85)}%",
                    "note": f"PDF analysis - {risk_level}",
                    "findings": findings if findings else ["No suspicious indicators found"]
                }
                
                logging.info(f"PDF analysis complete: {safe_filename} - {result['prediction']} ({len(findings)} findings)")
            
            except Exception as pdf_error:
                logging.error(f"Error analyzing PDF: {pdf_error}")
                result = {
                    "type": "pdf",
                    "prediction": "Unknown",
                    "file_name": safe_filename,
                    "confidence": "N/A",
                    "note": "Could not analyze PDF file",
                    "findings": [f"Analysis error: {str(pdf_error)}"]
                }
        
        # Add Python and archive handlers before executable fallback
        elif file_ext == 'py':
            logging.info(f"Analyzing python file: {safe_filename}")
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(20000)
                result = analyze_text_content(content, safe_filename)
                py_indicators = ['exec(', 'eval(', 'os.system', 'subprocess', 'Popen(', 'socket', 'ctypes', 'base64.b64decode', 'marshal.loads']
                found_py = [kw for kw in py_indicators if kw in content.lower()]
                if found_py:
                    result['prediction'] = 'Suspicious'
                    result['note'] = result.get('note', '') + ' | Python indicator(s) found'
                    result['confidence'] = '95%'
                    result['found_indicators'] = found_py
                logging.info(f"Python analysis complete: {safe_filename} - {result['prediction']}")
            except Exception as py_err:
                logging.error(f"Error analyzing python file: {py_err}")
                result = {"type": "py", "prediction": "Unknown", "file_name": safe_filename, "confidence": "N/A", "note": "Could not analyze python file"}

        elif file_ext in ('zip', 'tar', 'tar.gz', 'gz'):
            logging.info(f"Analyzing archive: {safe_filename}")
            findings = []
            any_suspicious = False
            highest_conf = 0.0
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    if file_ext == 'zip':
                        with zipfile.ZipFile(file_path, 'r') as z:
                            for zi in z.infolist():
                                if zi.is_dir():
                                    continue
                                try:
                                    with z.open(zi) as fh:
                                        data = fh.read()
                                except Exception:
                                    continue
                                # if PE inside archive
                                if len(data) >= 2 and data[:2] == b'MZ' and model is not None:
                                    temp_pe = Path(tmpdir) / Path(zi.filename).name
                                    temp_pe.write_bytes(data)
                                    try:
                                        feats = extract_features(str(temp_pe))
                                        is_malware, confidence, raw_label, probs = predict_features(feats, model, scaler)
                                        findings.append({'file': zi.filename, 'prediction': 'Malware' if is_malware else 'Safe', 'confidence': f"{confidence:.1f}%"})
                                        if is_malware:
                                            any_suspicious = True
                                            highest_conf = max(highest_conf, confidence)
                                    except Exception:
                                        pass
                                else:
                                    try:
                                        text = data.decode('latin-1', errors='ignore')
                                        txt_res = analyze_text_content(text, zi.filename)
                                        findings.append({'file': zi.filename, 'prediction': txt_res['prediction'], 'confidence': txt_res['confidence']})
                                        if txt_res['prediction'] != 'Safe':
                                            any_suspicious = True
                                            try:
                                                c = float(txt_res['confidence'].strip('%'))
                                                highest_conf = max(highest_conf, c)
                                            except Exception:
                                                highest_conf = max(highest_conf, 50.0)
                                    except Exception:
                                        continue
                    else:
                        try:
                            with tarfile.open(file_path, 'r:*') as tar:
                                for member in tar.getmembers():
                                    if member.isdir():
                                        continue
                                    try:
                                        f = tar.extractfile(member)
                                        if f is None:
                                            continue
                                        data = f.read()
                                    except Exception:
                                        continue
                                    if len(data) >= 2 and data[:2] == b'MZ' and model is not None:
                                        temp_pe = Path(tmpdir) / Path(member.name).name
                                        temp_pe.write_bytes(data)
                                        try:
                                            feats = extract_features(str(temp_pe))
                                            is_malware, confidence, raw_label, probs = predict_features(feats, model, scaler)
                                            findings.append({'file': member.name, 'prediction': 'Malware' if is_malware else 'Safe', 'confidence': f"{confidence:.1f}%"})
                                            if is_malware:
                                                any_suspicious = True
                                                highest_conf = max(highest_conf, confidence)
                                        except Exception:
                                            pass
                                    else:
                                        try:
                                            text = data.decode('latin-1', errors='ignore')
                                            txt_res = analyze_text_content(text, member.name)
                                            findings.append({'file': member.name, 'prediction': txt_res['prediction'], 'confidence': txt_res['confidence']})
                                            if txt_res['prediction'] != 'Safe':
                                                any_suspicious = True
                                                try:
                                                    c = float(txt_res['confidence'].strip('%'))
                                                    highest_conf = max(highest_conf, c)
                                                except Exception:
                                                    highest_conf = max(highest_conf, 50.0)
                                        except Exception:
                                            continue
                        except Exception as tar_e:
                            logging.warning(f"Failed to open tar archive: {tar_e}")

                result = {'type': 'archive', 'prediction': 'Suspicious' if any_suspicious else 'Safe', 'file_name': safe_filename, 'confidence': f"{highest_conf:.1f}%" if any_suspicious else '90%', 'findings': findings if findings else ['No suspicious indicators found']}
                logging.info(f"Archive analysis complete: {safe_filename} - {result['prediction']}")
            except Exception as arch_err:
                logging.error(f"Error analyzing archive: {arch_err}")
                result = {'type': 'archive', 'prediction': 'Unknown', 'file_name': safe_filename, 'confidence': 'N/A', 'findings': [f'Error: {str(arch_err)}']}

        else:
            # Handle executable files (.exe, .dll) with ML model
            logging.info(f"Extracting features from: {safe_filename}")
            try:
                features = extract_features(file_path)

                # Align features to model expectations to prevent misclassification due to ordering
                try:
                    if hasattr(model, 'feature_names_in_'):
                        expected_columns = list(model.feature_names_in_)
                        # Reindex to expected columns, fill any missing with 0 and drop extras
                        features = features.reindex(columns=expected_columns, fill_value=0)
                except Exception as align_err:
                    logging.warning(f"Feature alignment warning: {align_err}")

                # Use helper to predict
                is_malware, confidence, raw_label, probabilities = predict_features(features, model, scaler)

                # Also analyze polymorphic indicators and combine
                try:
                    poly_features = extract_polymorphic_features(file_path)
                    is_polymorphic, poly_risk_score, poly_indicators = analyze_polymorphic_indicators(poly_features, file_path)
                except Exception:
                    is_polymorphic, poly_risk_score, poly_indicators = False, 0.0, []

                final_confidence = max(confidence, poly_risk_score * 100)
                is_threat = is_malware or is_polymorphic

                result = {
                    "type": "file",
                    "prediction": "Malware" if is_threat else "Safe",
                    "file_name": safe_filename,
                    "confidence": f"{final_confidence:.1f}%",
                    "model": "NeuroShield Model + Polymorphic Detection",
                    "raw_prediction": raw_label,
                    "probabilities": probabilities,
                    "file_path": file_path,
                    "polymorphic_analysis": {
                        "is_polymorphic": is_polymorphic,
                        "risk_score": f"{poly_risk_score:.2f}",
                        "indicators": poly_indicators
                    }
                }

                logging.info(f"Analysis complete: {safe_filename} - {result['prediction']} ({result['confidence']} confidence)")

            except pefile.PEFormatError as pe_err:
                logging.warning(f"PE parsing failed for {safe_filename}: {pe_err}")
                result = {
                    "type": "file",
                    "prediction": "Unknown",
                    "file_name": safe_filename,
                    "confidence": "N/A",
                    "model": "NeuroShield Model",
                    "note": "File appears not to be a valid PE executable or is corrupted"
                }
            except Exception as ex:
                logging.error(f"Error analyzing executable: {ex}")
                result = {
                    "type": "file",
                    "prediction": "Unknown",
                    "file_name": safe_filename,
                    "confidence": "N/A",
                    "model": "NeuroShield Model",
                    "note": str(ex)
                }
        
        # Store file path in result for potential quarantine/cleaning
        result['file_path'] = file_path
        
        # Return JSON for API clients, otherwise render HTML
        if wants_json:
            return jsonify(result)
        # Don't delete yet - let user choose action
        return render_template('result.html', result=result)
    
    except Exception as e:
        # Log the full error for debugging
        logging.error(f"Error during file analysis: {str(e)}", exc_info=True)
        
        # Clean up file if it exists
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        # Return user-friendly error
        return render_template('index.html', error=f"An error occurred while analyzing the file. Please try again. Error details: {str(e)}")

@app.route('/quarantine', methods=['POST'])
def quarantine():
    """Quarantine a malicious file"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        threat_info = data.get('threat_info', {})
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'File not found'})
        
        # Quarantine the file
        result = quarantine_manager.quarantine_file(file_path, threat_info)
        
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Error quarantining file: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/analyze_async', methods=['POST'])
def analyze_async():
    """Accept a file upload and enqueue analysis, returning a job id."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Empty filename'})
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Unsupported file type'})

        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(file_path)

        # submit job
        job_id, fut = submit_job(process_saved_file, file_path, safe_filename)
        return jsonify({'success': True, 'job_id': job_id})
    except Exception as e:
        logging.error(f"Error enqueueing async analysis: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/job_status/<job_id>')
def job_status(job_id):
    try:
        status = get_job_status(int(job_id))
        if status is None:
            return jsonify({'success': False, 'message': 'Job not found'}), 404
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logging.error(f"Error querying job status: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/clean', methods=['POST'])
def clean():
    """Clean a malicious file"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        file_type = data.get('file_type')
        findings = data.get('findings', [])
        keywords = data.get('keywords', [])
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'File not found'})
        
        # Clean based on file type
        if file_type == 'txt':
            result = file_cleaner.clean_text_file(file_path, keywords)
        elif file_type == 'pdf':
            result = file_cleaner.clean_pdf_file(file_path, findings)
        else:
            return jsonify({'success': False, 'message': 'Cannot clean executable files. Please quarantine instead.'})
        
        # Delete original after cleaning
        if result['success']:
            try:
                os.remove(file_path)
            except:
                pass
        
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Error cleaning file: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_file', methods=['POST'])
def delete_file():
    """Delete a file without quarantine"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'File not found'})
        
        os.remove(file_path)
        logging.info(f"File deleted: {file_path}")
        
        return jsonify({'success': True, 'message': 'File deleted successfully'})
    
    except Exception as e:
        logging.error(f"Error deleting file: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/performance')
def performance_page():
    """Show performance metrics page"""
    return render_template('performance.html')

@app.route('/quarantine_manager')
def quarantine_manager_page():
    """Show quarantine management page"""
    try:
        quarantined_files = quarantine_manager.list_quarantined_files()
        stats = quarantine_manager.get_quarantine_stats()
        
        return render_template('quarantine.html', 
                             files=quarantined_files, 
                             stats=stats)
    
    except Exception as e:
        logging.error(f"Error loading quarantine page: {e}")
        return render_template('quarantine.html', 
                             files=[], 
                             stats={},
                             error=str(e))

@app.route('/restore_quarantine', methods=['POST'])
def restore_quarantine():
    """Restore a quarantined file"""
    try:
        data = request.get_json()
        quarantine_id = data.get('quarantine_id')
        
        result = quarantine_manager.restore_file(quarantine_id)
        
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Error restoring file: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_quarantine', methods=['POST'])
def delete_quarantine():
    """Permanently delete a quarantined file"""
    try:
        data = request.get_json()
        quarantine_id = data.get('quarantine_id')
        
        result = quarantine_manager.delete_quarantined_file(quarantine_id)
        
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Error deleting quarantined file: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/download_cleaned/<filename>')
def download_cleaned(filename):
    """Download a cleaned file"""
    try:
        file_path = os.path.join(file_cleaner.cleaned_dir, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        logging.error(f"Error downloading cleaned file: {e}")
        return str(e), 500

if __name__ == '__main__':
    # Get environment settings with secure defaults
    env = os.getenv('FLASK_ENV', 'production')
    debug = env == 'development'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))

    app.run(
        host=host,
        port=port,
        debug=debug
    )