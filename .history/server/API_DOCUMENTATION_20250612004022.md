# INSTWAVE Research Digest System - API Documentation

## Overview

The INSTWAVE Research Digest System provides a Flask-based REST API for managing research paper subscriptions, automated AI-powered summarization, and personalized email delivery. This documentation covers all available endpoints, data models, and usage examples.

**Base URL**: `http://localhost:5000` (Development)  
**API Version**: 1.0  
**Content-Type**: `application/json` or `application/x-www-form-urlencoded`  
**Timezone**: Asia/Seoul (KST)

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Data Models

### User Model
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "created_at": "2024-01-15T10:30:00+09:00",
  "topics": [1, 2, 3]
}
```

### Topic Model
Predefined research categories:
```json
{
  "1": "AI/ML",
  "2": "Physics", 
  "3": "Computer Science",
  "4": "Mathematics",
  "5": "Biology",
  "6": "Engineering"
}
```

### Paper Model
```json
{
  "id": 42,
  "title": "Advanced Neural Networks for Computer Vision",
  "author": "Smith, J. et al.",
  "arxiv_id": "2024.12345",
  "summary": "Original paper abstract...",
  "ai_summary": {
    "summary": "AI가 생성한 한 줄 요약",
    "evaluation": "AI 평가 및 의미",
    "importance": 0.85,
    "keywords": ["deep learning", "computer vision", "neural networks"],
    "category": "Computer Vision"
  },
  "created_at": "2024-01-15T10:30:00+09:00",
  "updated_at": "2024-01-15T11:45:00+09:00",
  "topics": [1, 3],
  "link": "https://arxiv.org/abs/2024.12345"
}
```

## API Endpoints

### 1. Subscription Form Page

**Endpoint**: `GET /`  
**Description**: Renders the HTML subscription form page  
**Authentication**: None required

#### Request
```bash
curl -X GET http://localhost:5000/
```

#### Response
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html>
<head>
    <title>INSTWAVE Research Digest - Subscribe</title>
</head>
<body>
    <!-- HTML subscription form -->
</body>
</html>
```

#### Usage Example
```javascript
// Access via browser
window.location.href = 'http://localhost:5000/';

// Or fetch via JavaScript
fetch('http://localhost:5000/')
  .then(response => response.text())
  .then(html => {
    document.body.innerHTML = html;
  });
```

---

### 2. Create Subscription

**Endpoint**: `POST /submit`  
**Description**: Handle user subscription submission with topic preferences  
**Authentication**: None required  
**Content-Type**: `application/x-www-form-urlencoded` or `application/json`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | User's full name |
| `email` | string | Yes | Valid email address |
| `topics` | array | Yes | List of topic IDs (minimum 3 required) |

#### Request Examples

**Form Data (application/x-www-form-urlencoded):**
```bash
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=John Doe&email=john.doe@example.com&topics=1&topics=2&topics=3"
```

**JSON (application/json):**
```bash
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com", 
    "topics": ["1", "2", "3"]
  }'
```

**JavaScript/Fetch API:**
```javascript
const subscriptionData = {
  name: 'John Doe',
  email: 'john.doe@example.com',
  topics: ['1', '2', '3']
};

fetch('http://localhost:5000/submit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(subscriptionData)
})
.then(response => response.json())
.then(data => {
  if (data.status === 'success') {
    console.log('Subscription successful:', data.user_id);
  } else {
    console.error('Subscription failed:', data.message);
  }
});
```

**HTML Form:**
```html
<form action="http://localhost:5000/submit" method="POST">
  <input type="text" name="name" placeholder="Full Name" required>
  <input type="email" name="email" placeholder="Email Address" required>
  
  <div>
    <label><input type="checkbox" name="topics" value="1"> AI/ML</label>
    <label><input type="checkbox" name="topics" value="2"> Physics</label>
    <label><input type="checkbox" name="topics" value="3"> Computer Science</label>
    <label><input type="checkbox" name="topics" value="4"> Mathematics</label>
    <label><input type="checkbox" name="topics" value="5"> Biology</label>
    <label><input type="checkbox" name="topics" value="6"> Engineering</label>
  </div>
  
  <button type="submit">Subscribe</button>
</form>
```

#### Successful Response
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "message": "Subscription received!",
  "user_id": 42
}
```

#### Error Responses

**Missing Required Fields (400 Bad Request):**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "status": "error",
  "message": "Invalid input: name=John Doe, email=, topics_count=2"
}
```

**Invalid Topic IDs (400 Bad Request):**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "status": "error", 
  "message": "Invalid topic IDs: 7, 8"
}
```

**Duplicate Email (400 Bad Request):**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "status": "error",
  "message": "Email already exists in the system"
}
```

**Internal Server Error (500 Internal Server Error):**
```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "status": "error",
  "message": "Internal server error"
}
```

#### Validation Rules

1. **Name**: 
   - Required field
   - Must not be empty string
   - No specific length restrictions

2. **Email**:
   - Required field  
   - Must be valid email format
   - Must be unique in the system

3. **Topics**:
   - Required field
   - Minimum 3 topics must be selected
   - Topic IDs must exist in the system (1-6)
   - Must be provided as array of strings or multiple form fields

## Database Schema

### Tables Structure

```sql
-- Users table
CREATE TABLE Users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Topics table (predefined)
CREATE TABLE Topics (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- User topic preferences (many-to-many)
CREATE TABLE User_topics (
    user_id BIGINT REFERENCES Users(id) ON DELETE CASCADE,
    topic_id BIGINT REFERENCES Topics(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, topic_id)
);

-- Research papers
CREATE TABLE Thesis (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(1000) NOT NULL,
    author VARCHAR(500),
    arxiv_id VARCHAR(50),
    summary TEXT,
    ai_summary JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Paper topic classification (many-to-many)
CREATE TABLE Paper_topics (
    paper_id BIGINT REFERENCES Thesis(id) ON DELETE CASCADE,
    topic_id BIGINT REFERENCES Topics(id) ON DELETE CASCADE,
    PRIMARY KEY (paper_id, topic_id)
);
```

## Automated Background Services

### Weekly AI Summary Generation
- **Schedule**: Every Tuesday at 21:12 KST
- **Function**: Processes papers without AI summaries using OpenAI GPT-3.5-turbo
- **Language**: Korean language prompts and responses
- **Storage**: JSON format in `thesis.ai_summary` column

### Weekly Email Distribution  
- **Schedule**: Every Tuesday at 21:13 KST (1 minute after AI generation)
- **Function**: Sends personalized research digests to all subscribed users
- **Personalization**: Based on user topic preferences
- **Service**: Resend API for email delivery

## Error Handling

### Standard Error Response Format
All API errors follow this consistent format:

```json
{
  "status": "error",
  "message": "Human-readable error description",
  "code": "ERROR_CODE_IF_APPLICABLE",
  "timestamp": "2024-01-15T10:30:00+09:00"
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success - Request completed successfully |
| 400 | Bad Request - Invalid input data or missing required fields |
| 404 | Not Found - Endpoint does not exist |
| 500 | Internal Server Error - Server-side error occurred |

### Common Error Scenarios

1. **Missing Required Fields**: Returns 400 with specific field information
2. **Invalid Topic IDs**: Returns 400 with list of invalid IDs  
3. **Database Connection Issues**: Returns 500 with generic error message
4. **Duplicate Email**: Returns 400 with duplicate email error
5. **Malformed JSON**: Returns 400 with JSON parsing error

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use:

- **Subscription endpoint**: 5 requests per minute per IP
- **Static pages**: 100 requests per minute per IP

## CORS Configuration

The API currently does not have CORS headers configured. For frontend integration, add CORS support:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])  # Allow Next.js frontend
```

## Health Check Endpoint (Recommended)

Consider adding a health check endpoint for monitoring:

```python
@app.route('/health')
def health_check():
    try:
        # Test database connectivity
        conn = get_db_connection()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy', 
            'error': 'Database connection failed',
            'timestamp': datetime.now().isoformat()
        }), 500
```

## Testing Examples

### Manual Testing with curl

```bash
# Test subscription with valid data
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Test User&email=test@example.com&topics=1&topics=2&topics=3" \
  -v

# Test with missing email (should return 400)
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Test User&topics=1&topics=2&topics=3" \
  -v

# Test with insufficient topics (should return 400)  
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Test User&email=test2@example.com&topics=1&topics=2" \
  -v

# Test with invalid topic IDs (should return 400)
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Test User&email=test3@example.com&topics=1&topics=2&topics=99" \
  -v
```

### Python Testing Script

```python
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_valid_subscription():
    """Test valid subscription submission"""
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'topics': ['1', '2', '3']
    }
    
    response = requests.post(f'{BASE_URL}/submit', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()['status'] == 'success'

def test_invalid_subscription():
    """Test invalid subscription (missing email)"""
    data = {
        'name': 'Test User',
        'topics': ['1', '2', '3']
    }
    
    response = requests.post(f'{BASE_URL}/submit', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 400
    assert response.json()['status'] == 'error'

if __name__ == '__main__':
    test_valid_subscription()
    test_invalid_subscription()
    print("All tests passed!")
```

## Environment Configuration

### Required Environment Variables

```env
# Database Configuration
DB_HOST=localhost
DB_NAME=instwave_db
DB_USER=postgres  
DB_PASSWORD=your_secure_password

# API Service Keys
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx

# Optional: Google Cloud Storage
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
BUCKET_NAME=instwave-storage
```

### Flask Configuration

The application uses `config.py` for centralized configuration management:

```python
# Access configuration in application
from flask import current_app

db_host = current_app.config['DB_HOST']
api_key = current_app.config['RESEND_API_KEY']
```

## Logging

The application uses Python's built-in logging with the 'INSTWAVE' logger:

```python
import logging
logger = logging.getLogger('INSTWAVE')

# Log levels used:
logger.info("Operation completed successfully")
logger.error("Error occurred", exc_info=True) 
logger.debug("Debug information")
logger.warning("Warning message")
```

## Production Considerations

### Security Enhancements
1. **Input Validation**: Implement comprehensive input sanitization
2. **Rate Limiting**: Prevent abuse with request rate limiting
3. **HTTPS**: Use SSL/TLS for encrypted communication
4. **CORS**: Configure appropriate CORS policies
5. **Authentication**: Consider adding API key authentication

### Performance Optimizations
1. **Database Indexing**: Add indexes on frequently queried columns
2. **Connection Pooling**: Implement database connection pooling
3. **Caching**: Add Redis/Memcached for frequently accessed data
4. **Load Balancing**: Use multiple server instances for high availability

### Monitoring and Observability
1. **Health Checks**: Implement comprehensive health monitoring
2. **Metrics**: Add application performance metrics
3. **Error Tracking**: Integrate error tracking service (Sentry, etc.)
4. **Logging**: Centralized logging with structured log format

---

**API Version**: 1.0  
**Last Updated**: January 2024  
**Contact**: INSTWAVE Development Team 