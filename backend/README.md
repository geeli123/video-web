# Deployment

```
gcloud functions deploy convert-video \
    --runtime python3.13 \
    --trigger-http \
    --allow-unauthenticated \
    --memory 2048MB \
    --timeout 300s
```