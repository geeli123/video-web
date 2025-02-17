from pathlib import Path

class Config:
    # Base directory of the project
    BASE_DIR = Path(__file__).parent.parent

    # Upload configurations
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    CONVERTED_FOLDER = BASE_DIR / 'static' / 'converted'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB max-size

    # Allowed video formats
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'mod', 'mpg', 'mpeg'}
    
    # Allowed output formats
    OUTPUT_FORMATS = {'mp4', 'avi', 'mov', 'webm'}

    def __init__(self):
        # Create upload and converted directories if they don't exist
        self.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        self.CONVERTED_FOLDER.mkdir(parents=True, exist_ok=True) 