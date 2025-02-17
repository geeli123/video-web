#!/bin/bash

# Set variables
PROJECT_ID="your-project-id"
REGION="us-central1"
BACKEND_SERVICE="video-converter-backend"
FRONTEND_SERVICE="video-converter-frontend"
STORAGE_BUCKET="video-converter-storage"

# Create GCP project (if not exists)
gcloud projects create $PROJECT_ID --name="Video Converter"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    storage.googleapis.com

# Create Storage bucket
gsutil mb -l $REGION gs://$STORAGE_BUCKET

# Build and deploy backend
gcloud builds submit ./backend --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE
gcloud run deploy $BACKEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="GCP_BUCKET_NAME=$STORAGE_BUCKET"

# Build and deploy frontend
gcloud builds submit ./frontend --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE
gcloud run deploy $FRONTEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated 