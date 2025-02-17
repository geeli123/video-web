const config = {
    API_URL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000',
    MAX_FILE_SIZE: 500 * 1024 * 1024, // 500MB
    ALLOWED_FORMATS: ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.mod', '.mpeg', '.mpg'],
};

export default config;