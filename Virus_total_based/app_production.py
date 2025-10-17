#!/usr/bin/env python3
"""
Production-ready NeuroShield Threat Intelligence API with rate limiting
"""
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import defusedxml.ElementTree as ET
from defusedxml import defuse_stdlib
import tempfile
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('neuroshield-api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure defusedxml is used instead of standard xml
defuse_stdlib()

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
if not app.secret_key:
    app.secret_key = os.urandom(24)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "30 per hour"],
    storage_uri="memory://"
)

# API configuration
API_KEY = os.environ.get('NEUROSHIELD_API_KEY')
if not API_KEY:
    logger.warning("NEUROSHIELD_API_KEY environment variable is not set")
    # Don't raise error, allow app to start but show warnings

# NeuroShield API endpoints (powered by threat intelligence integration)
NEUROSHIELD_URL_FILE = 'https://www.virustotal.com/vtapi/v2/file/report'
NEUROSHIELD_URL_SCAN = 'https://www.virustotal.com/vtapi/v2/file/scan'
NEUROSHIELD_URL_URL = 'https://www.virustotal.com/vtapi/v2/url/report'

recent_results = []

@app.route('/')
@limiter.limit("60 per minute")
def index():
    return render_template('index.html', recent_results=recent_results)

@app.route('/analyze', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Strict rate limit for NeuroShield API
def analyze():
    # Redirect GET requests to home page
    if request.method == 'GET':
        flash('Please use the form to submit your analysis.', 'info')
        return redirect(url_for('index'))
    
    if not API_KEY or API_KEY == 'your-api-key-here-replace-this':
        flash('NeuroShield API key not configured. Please set NEUROSHIELD_API_KEY in .env file', 'error')
        return redirect(url_for('index'))
    
    file_hash = request.form.get('file_hash', '').strip()
    xml_data = request.form.get('xml_data', '').strip()
    file = request.files.get('file')
    url = request.form.get('url', '').strip()
    
    # Validate input lengths to prevent excessive data
    if len(file_hash) > 128:
        flash('Invalid file hash length', 'error')
        return redirect(url_for('index'))
        
    if len(url) > 2048:
        flash('URL is too long', 'error')
        return redirect(url_for('index'))
        
    if xml_data and len(xml_data) > 10240:
        flash('XML data is too large', 'error')
        return redirect(url_for('index'))
        
    # Validate file size if a file is uploaded
    if file:
        try:
            file_content = file.read()
            if len(file_content) > 32 * 1024 * 1024:
                flash('File is too large. Maximum size is 32MB', 'error')
                return redirect(url_for('index'))
            file.seek(0)
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            flash('Error processing file', 'error')
            return redirect(url_for('index'))
            
    # Basic URL validation
    if url and not url.startswith(('http://', 'https://')):
        flash('Invalid URL. Must start with http:// or https://', 'error')
        return redirect(url_for('index'))

    if not file and not url and not file_hash and not xml_data:
        flash('Please input File, URL or Hash', 'error')
        return redirect(url_for('index'))

    if xml_data:
        try:
            root = ET.XML(xml_data)
            file_hash = root.findtext('hash')
        except ET.ParseError:
            flash('Invalid XML data.', 'error')
            return redirect(url_for('index'))

    result = {}

    if url:
        try:
            params = {'apikey': API_KEY, 'resource': url}
            response = requests.get(NEUROSHIELD_URL_URL, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as e:
            logger.error(f"Error analyzing URL: {str(e)}")
            flash('Error analyzing URL. Please try again later.', 'error')
            return redirect(url_for('index'))
            
    elif file:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, file.filename)
            try:
                file.save(file_path)
                with open(file_path, 'rb') as f:
                    files = {'file': (file.filename, f)}
                    try:
                        response = requests.post(NEUROSHIELD_URL_SCAN, files=files, params={'apikey': API_KEY}, timeout=30)
                        response.raise_for_status()
                        scan_result = response.json()

                        if scan_result.get('response_code') == 1:
                            resource_id = scan_result['resource']
                            time.sleep(15)
                            params = {'apikey': API_KEY, 'resource': resource_id}
                            try:
                                report_response = requests.get(NEUROSHIELD_URL_FILE, params=params, timeout=30)
                                report_response.raise_for_status()
                                result = report_response.json()
                            except requests.RequestException as e:
                                logger.error(f"Error getting scan report: {str(e)}")
                                flash('Error retrieving scan results. Please try again later.', 'error')
                                return redirect(url_for('index'))
                        else:
                            flash('Error scanning file: {}'.format(scan_result.get('verbose_msg', 'Unknown error')), 'error')
                            return redirect(url_for('index'))
                    except requests.RequestException as e:
                        logger.error(f"Error uploading file for scanning: {str(e)}")
                        flash('Error uploading file. Please try again later.', 'error')
                        return redirect(url_for('index'))
            except Exception as e:
                logger.error(f"Error handling file upload: {str(e)}")
                flash('Error processing file upload. Please try again.', 'error')
                return redirect(url_for('index'))

    elif file_hash:
        params = {'apikey': API_KEY, 'resource': file_hash}
        try:
            response = requests.get(NEUROSHIELD_URL_FILE, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as e:
            logger.error(f"Error retrieving file hash results: {str(e)}")
            flash('Error retrieving results. Please try again later.', 'error')
            return redirect(url_for('index'))

    else:
        flash('No valid input provided.', 'error')
        return redirect(url_for('index'))

    if result.get('response_code') == 1:
        formatted_result = {
            'file_name': file.filename if file else url if url else file_hash,
            'scan_date': result.get('scan_date', 'N/A'),
            'positives': result.get('positives', 0),
            'total': result.get('total', 0),
            'detections': []
        }

        for engine, details in result.get('scans', {}).items():
            if details.get('detected'):
                formatted_result['detections'].append({
                    'engine': engine,
                    'result': details.get('result', 'N/A'),
                    'version': details.get('version', 'N/A'),
                    'update': details.get('update', 'N/A')
                })

        # Save the formatted result in the recent_results list
        recent_results.insert(0, formatted_result)
        if len(recent_results) > 30:
            recent_results.pop()

        # Count malware and clean detections based on the current scan result
        malware_count = formatted_result['positives']
        clean_count = formatted_result['total'] - malware_count
        
        chart_data = {
            'malware_count': malware_count,
            'clean_count': clean_count
        }
        
        logger.info(f"Scan completed: {formatted_result['file_name']} - {malware_count}/{formatted_result['total']} detections")
    else:
        flash('Not included in Database / Scan in Progress', 'error')
        return redirect(url_for('index'))

    return render_template('result.html', result=formatted_result, chart_data=chart_data)

@app.route('/health')
@limiter.exempt
def health():
    """Health check endpoint for monitoring"""
    return {
        'status': 'healthy',
        'api_configured': API_KEY is not None and API_KEY != 'your-api-key-here-replace-this'
    }, 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)