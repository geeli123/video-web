import functions_framework
from flask import jsonify, request, send_file
from flask_cors import cross_origin
import uuid
import zipfile
import io
import json
import tempfile
from google.cloud import storage
from pathlib import Path
import ffmpeg
from typing import Dict, List

# Configuration
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'mod', 'mpg', 'mpeg'}
OUTPUT_FORMATS = {'mp4', 'avi', 'mov', 'webm'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB per file

# Initialize Google Cloud Storage client
storage_client = storage.Client()

class VideoConverter:
    QUALITY_SETTINGS = {
        'very low': '36',
        'low': '32',
        'medium': '31',
        'high': '24',
        'very high': '15'
    }

    @staticmethod
    def convert_video(input_path: str, output_path: str, format: str, quality: str) -> tuple[bool, str]:
        try:
            ffmpeg.input(input_path) \
                .output(output_path, crf=VideoConverter.QUALITY_SETTINGS[quality]) \
                .run(overwrite_output=True, quiet=False)
            return True, ""
        except ffmpeg.Error as e:
            error_message = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
            return False, error_message
        except Exception as e:
            error_message = f"Conversion error: {str(e)}"
            return False, error_message

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file(file) -> Dict:
    if not file or file.filename == '':
        return {'valid': False, 'error': 'Empty file'}
    
    if not allowed_file(file.filename):
        return {'valid': False, 'error': 'Invalid file format'}
        
    if file.content_length > MAX_FILE_SIZE:
        return {'valid': False, 'error': 'File too large'}
        
    return {'valid': True}

@functions_framework.http
@cross_origin(expose_headers=['X-Conversion-Results'])
def convert_video(request):
    """HTTP Cloud Function for video conversion."""
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405

    try:
        if 'videos[]' not in request.files:
            return jsonify({'error': 'No video files provided'}), 400
        
        files = request.files.getlist('videos[]')
        output_format = request.form.get('format', '').lower()
        quality = request.form.get('quality', 'medium').lower()
        
        # Validate inputs
        if not files:
            return jsonify({'error': 'No files selected'}), 400
        
        if output_format not in OUTPUT_FORMATS:
            return jsonify({'error': 'Invalid output format'}), 400
            
        if quality not in VideoConverter.QUALITY_SETTINGS:
            return jsonify({'error': 'Invalid quality setting'}), 400
        
        # Create memory file for zip
        memory_file = io.BytesIO()
        conversion_results = []
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
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
                        # Generate unique filenames
                        original_ext = file.filename.rsplit('.', 1)[1].lower()
                        unique_filename = f"{uuid.uuid4()}.{original_ext}"
                        input_path = temp_dir_path / unique_filename
                        
                        # Save uploaded file locally
                        file.save(str(input_path))
                        
                        # Generate output filename and path
                        output_filename = f"{Path(file.filename).stem}.{output_format}"
                        output_path = temp_dir_path / f"{uuid.uuid4()}.{output_format}"
                        
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
                        
                    except Exception as e:
                        conversion_results.append({
                            'filename': file.filename,
                            'status': 'error',
                            'message': str(e)
                        })
        
        # Check if any conversions were successful
        if not any(result['status'] == 'success' for result in conversion_results):
            return jsonify({
                'error': 'No files were successfully converted',
                'results': conversion_results
            }), 500
        
        # Prepare response
        memory_file.seek(0)
        
        # Create response with appropriate headers
        response = send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='converted_videos.zip',
            max_age=0,
            conditional=True
        )
        
        # Add conversion results to response headers
        response.headers['X-Conversion-Results'] = json.dumps(conversion_results)
        return response
        
    except Exception as e:
        return jsonify({
            'error': f'Conversion failed: {str(e)}',
            'results': conversion_results if 'conversion_results' in locals() else []
        }), 500 