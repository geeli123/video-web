const config = {
    API_URL: 'http://127.0.0.1:5000',
    MAX_FILE_SIZE: 500 * 1024 * 1024, // 500MB
    ALLOWED_FORMATS: ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.mod', '.mpeg', '.mpg']
};

class VideoConverter {
    constructor() {
        this.files = [];
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('video-upload').addEventListener('change', this.handleFileChange.bind(this));
        document.getElementById('convert-button').addEventListener('click', this.handleConvert.bind(this));
    }

    validateFiles(files) {
        for (const file of files) {
            if (file.size > config.MAX_FILE_SIZE) {
                return `${file.name} is too large. Maximum size is 500MB`;
            }
            
            const ext = file.name.toLowerCase().match(/\.[0-9a-z]+$/);
            if (!ext || !config.ALLOWED_FORMATS.includes(ext[0])) {
                return `${file.name} has an invalid format`;
            }
        }
        return null;
    }

    handleFileChange(event) {
        const files = Array.from(event.target.files);
        const error = this.validateFiles(files);
        
        if (error) {
            this.showError(error);
            return;
        }

        this.files = files;
        this.showError(null);
        this.updateSelectedFiles();
        document.getElementById('convert-button').disabled = false;
    }

    async handleConvert() {
        if (this.files.length === 0) {
            this.showError('Please select at least one file');
            return;
        }

        const button = document.getElementById('convert-button');
        button.disabled = true;
        button.classList.add('loading');
        this.showError(null);

        const formData = new FormData();
        this.files.forEach(file => {
            formData.append('videos[]', file);
        });
        formData.append('format', document.getElementById('format').value);
        formData.append('quality', document.getElementById('quality').value);

        try {
            const response = await fetch(`${config.API_URL}/api/convert`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Conversion failed');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'converted_videos.zip';
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

        } catch (err) {
            this.showError(err.message);
        } finally {
            button.disabled = false;
            button.classList.remove('loading');
        }
    }

    showError(message) {
        const errorElement = document.getElementById('error');
        errorElement.textContent = message || '';
    }

    updateSelectedFiles() {
        const element = document.getElementById('selected-files');
        element.textContent = this.files.map(f => f.name).join(', ');
    }
}

new VideoConverter(); 