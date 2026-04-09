# API Reference

## Base URL
`http://localhost:8000/api/v1`

## Endpoints

### Health Check
```
GET /health
```
Returns server status, version, and tool availability.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "python_version": "3.11.0",
  "tools": {
    "ffmpeg": true,
    "ffprobe": true,
    "yt_dlp": true
  }
}
```

---

### Fetch Metadata
```
POST /metadata
```
Fetches video metadata without downloading.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "platform": "youtube",
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "description": "...",
  "duration": 212,
  "thumbnail": "https://...",
  "uploader": "Channel Name",
  "upload_date": "20090101",
  "view_count": 1000000,
  "like_count": 10000,
  "formats": [...],
  "is_live": false
}
```

**Rate limit:** 20 requests/minute per IP

---

### Start Download
```
POST /download
```
Creates a download job and processes it in the background.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format_id": "137",
  "quality": "best",
  "audio_only": false,
  "subtitles": false
}
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "queued",
  "message": "Download job created successfully"
}
```

**Rate limit:** 10 requests/minute per IP

---

### Get Download Status
```
GET /download/{job_id}/status
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "url": "...",
  "status": "completed",
  "progress": 100.0,
  "filename": "video.mp4",
  "title": "Video Title",
  "platform": "youtube"
}
```

**Status values:** `queued`, `processing`, `completed`, `failed`

---

### Stream/Download File
```
GET /download/{job_id}/stream
```
Streams the downloaded file to the client. Only available when status is `completed`.

---

### Get History
```
GET /history
```
Returns download history (in-memory, resets on restart).

---

### Clear History
```
DELETE /history
```

---

## Error Responses

| Status | Description |
|--------|-------------|
| 400 | Invalid URL |
| 404 | Job or file not found |
| 422 | Unsupported platform |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
