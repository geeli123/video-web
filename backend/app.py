from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
import zipfile
import io
import json
from typing import List, Dict
import logging

from config import Config
from utils.video_converter import VideoConverter

app = Flask(__name__)
config = Config()
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add file size validation
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB per file

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def validate_file(file) -> Dict:
    if not file or file.filename == '':
        return {'valid': False, 'error': 'Empty file'}
    
    if not allowed_file(file.filename):
        return {'valid': False, 'error': 'Invalid file format'}
        
    if file.content_length > MAX_FILE_SIZE:
        return {'valid': False, 'error': 'File too large'}
        
    return {'valid': True}

@app.route('/api/convert', methods=['POST'])
def convert_video():
    try:
        if 'videos[]' not in request.files:
            return jsonify({'error': 'No video files provided'}), 400
        
        files = request.files.getlist('videos[]')
        output_format = request.form.get('format', '').lower()
        quality = request.form.get('quality', 'medium').lower()
        
        # Validate inputs
        if not files:
            return jsonify({'error': 'No files selected'}), 400
        
        if output_format not in config.OUTPUT_FORMATS:
            return jsonify({'error': 'Invalid output format'}), 400
            
        if quality not in VideoConverter.QUALITY_SETTINGS:
            return jsonify({'error': 'Invalid quality setting'}), 400
        
        # Create memory file for zip
        memory_file = io.BytesIO()
        conversion_results = []
        
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for file in files:
                if file.filename == '':
                    continue
                
                if not allowed_file(file.filename):
                    conversion_results.append({
                        'filename': file.filename,
                        'status': 'error',
                        'message': 'Invalid file format'
                    })
                    continue

                try:
                    # Generate unique filename for upload
                    original_ext = file.filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4()}.{original_ext}"
                    input_path = config.UPLOAD_FOLDER / unique_filename
                    
                    # Save uploaded file
                    file.save(str(input_path))
                    
                    # Generate output filename and path
                    output_filename = f"{Path(file.filename).stem}.{output_format}"
                    output_path = config.CONVERTED_FOLDER / f"{uuid.uuid4()}.{output_format}"
                    
                    # Convert video
                    success, error_message = VideoConverter.convert_video(
                        str(input_path),
                        str(output_path),
                        output_format,
                        quality
                    )

                    if success:
                        # Add to zip file
                        zf.write(str(output_path), output_filename)
                        conversion_results.append({
                            'filename': file.filename,
                            'status': 'success'
                        })
                    else:
                        conversion_results.append({
                            'filename': file.filename,
                            'status': 'error',
                            'message': error_message
                        })
                    
                    # Clean up files
                    input_path.unlink()
                    output_path.unlink()
                    
                except Exception as e:
                    print(e)
                    conversion_results.append({
                        'filename': file.filename,
                        'status': 'error',
                        'message': str(e)
                    })
                    
                    # Clean up files in case of error
                    if 'input_path' in locals() and input_path.exists():
                        input_path.unlink()
                    if 'output_path' in locals() and output_path.exists():
                        output_path.unlink()
        
        # Check if any conversions were successful
        if not any(result['status'] == 'success' for result in conversion_results):
            return jsonify({
                'error': 'No files were successfully converted',
                'results': conversion_results
            }), 500
        
        # Prepare zip file for response
        memory_file.seek(0)
        response = send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='converted_videos.zip'
        )
        
        # Add conversion results to response headers
        response.headers['X-Conversion-Results'] = json.dumps(conversion_results)
        return response
        
    except Exception as e:
        return jsonify({
            'error': f'Conversion failed: {str(e)}',
            'results': conversion_results
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 
