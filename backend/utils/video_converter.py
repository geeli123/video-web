from pathlib import Path
import ffmpeg

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
        """
        Convert video using ffmpeg
        
        Args:
            input_path: Path to input video
            output_path: Path to save converted video
            format: Output format (mp4, avi, etc.)
            quality: Conversion quality (low, medium, high)
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
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