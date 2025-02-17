import React, { useState } from 'react';
import {
  Box,
  Button,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
  Paper,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';
import config from '../config';

interface ConversionResult {
  filename: string;
  status: 'success' | 'error';
  message?: string;
}

const VideoConverter: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [format, setFormat] = useState('mp4');
  const [quality, setQuality] = useState('medium');
  const [converting, setConverting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);

  const validateFiles = (files: File[]): string | null => {
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
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const newFiles = Array.from(event.target.files);
      const error = validateFiles(newFiles);
      if (error) {
        setError(error);
        return;
      }
      setFiles(newFiles);
      setError(null);
    }
  };

  const handleConvert = async () => {
    if (files.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setConverting(true);
    setError(null);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('videos[]', file);
    });
    formData.append('format', format);
    formData.append('quality', quality);

    try {
        const response = await axios.post(config.API_URL + '/api/convert', formData, {
          responseType: 'blob',
        });
      
        // Get conversion results from header with error handling
        const conversionResults = response.headers['x-conversion-results'];
        if (conversionResults) {
          const results = JSON.parse(conversionResults);
          console.log('Conversion results:', results);
        }
      
        // Create download link for zip file
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'converted_videos.zip');
        document.body.appendChild(link);
        link.click();
        link.remove();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred during conversion');
      } finally {
        setConverting(false);
      }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Video Converter
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Button
          variant="contained"
          component="label"
          startIcon={<CloudUploadIcon />}
          sx={{ mb: 2 }}
        >
          Select Videos
          <input
            type="file"
            hidden
            multiple
            accept={config.ALLOWED_FORMATS.join(',')}
            onChange={handleFileChange}
          />
        </Button>
        <Typography>
          Selected files: {files.map(f => f.name).join(', ')}
        </Typography>
      </Box>

      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Output Format</InputLabel>
        <Select
          value={format}
          label="Output Format"
          onChange={(e) => setFormat(e.target.value)}
        >
          <MenuItem value="mp4">MP4</MenuItem>
          <MenuItem value="avi">AVI</MenuItem>
          <MenuItem value="mov">MOV</MenuItem>
          <MenuItem value="webm">WebM</MenuItem>
        </Select>
      </FormControl>

      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>Quality</InputLabel>
        <Select
          value={quality}
          label="Quality"
          onChange={(e) => setQuality(e.target.value)}
        >
          <MenuItem value="very low">Very Low</MenuItem>
          <MenuItem value="low">Low</MenuItem>
          <MenuItem value="medium">Medium</MenuItem>
          <MenuItem value="high">High</MenuItem>
          <MenuItem value="very high"> Very High</MenuItem>
        </Select>
      </FormControl>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Button
        variant="contained"
        onClick={handleConvert}
        disabled={converting || files.length === 0}
        fullWidth
      >
        {converting ? (
          <CircularProgress size={24} color="inherit" />
        ) : (
          'Convert Videos'
        )}
      </Button>
    </Paper>
  );
};

export default VideoConverter; 