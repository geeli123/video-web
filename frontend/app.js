const config = {
    API_URL: 'https://us-central1-chuan-compute.cloudfunctions.net/convert_video',
    MAX_FILE_SIZE: 500 * 1024 * 1024, // 500MB
    ALLOWED_FORMATS: ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.mod', '.mpeg', '.mpg']
};

class VideoConverter {
    constructor() {
        this.files = [];
        this.setupEventListeners();
    }

    setupEventListeners() {
        const uploadInput = document.getElementById('video-upload');
        const form = document.getElementById('converter-form');

        uploadInput.addEventListener('change', this.handleFileChange.bind(this));

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleConvert(e);
        });
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

    async handleConvert(event) {
        if (this.files.length === 0) {
            this.showError('Please select at least one file');
            return;
        }

        console.log('Starting conversion process...');
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
            console.log('Sending request to API...');
            const response = await fetch(`${config.API_URL}`, {
                method: 'POST',
                body: formData,
            });
            console.log('Response received:', response);
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server response:', errorText);
                throw new Error(`Conversion failed: ${errorText}`);
            }

            const blob = await response.blob();
            console.log('Received blob:', blob.type, blob.size);

            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            console.log(response.headers.get('X-Conversion-Results'));
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