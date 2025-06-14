# INSTWAVE - AI Research Paper Digest System

INSTWAVE is an automated system that discovers the latest research papers from arXiv, generates AI-powered summaries, and delivers personalized notifications to users based on their preferences.

## Features
- Automated paper discovery from arXiv
- AI-powered summaries using OpenAI GPT-3.5
- Personalized email and Kakao notifications
- User preference management via web dashboard
- Multi-language support (English and Korean)
- Weekly digest scheduling and on-demand notifications

## Technology Stack
- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **AI Service**: OpenAI API
- **Email Service**: Resend
- **Kakao Notification**: Kakao API
- **Frontend**: HTML/CSS/Jinja2 templates

## Prerequisites
- Python 3.9+
- PostgreSQL
- OpenAI API Key
- Resend API Key
- Kakao API Key (for Kakao notifications)

## Local Setup

### 1. Clone the repository
```bash
git clone <https://github.com/dogukanatar/insightwave251.git>
cd insightwave251
```
### 2. Set up a virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```
### 3. Set up environment variables

Create a `.env` file in the root directory and add the following:

```bash
SECRET_KEY=your_secret_key
RESEND_API_KEY=your_resend_api_key
OPENAI_API_KEY=your_openai_api_key
DB_HOST=your_db_host
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
KAKAO_CLIENT_ID=your_kakao_client_id
```

### 4. Initialize the Database

Run the following command to create the required database tables:

```bash
python init_db.py

```

This script will create all necessary tables in your PostgreSQL database based on your ERD. Make sure your environment variables (DB_NAME, DB_USER, etc.) are set correctly.

### 5. Run the application

```bash
python app.py

```

The application will be available at `http://localhost:8000`.

## Usage

1. Register a new account at `http://localhost:8000/register`
2. Log in and set your preferences (topics, language, notification method)
3. The system will send weekly digests every Tuesday. You can also trigger a digest immediately from the dashboard.

## Project Structure

```
├── app.py                     # Main Flask application
├── config.py                  # Configuration settings
├── scheduler.py               # Background task scheduler
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (example)
├── i18n.py                    # Translation dictionary
├── services/                  # Service layer
│   ├── ai_summary.py          # AI summary generation
│   ├── auth.py                # User authentication
│   ├── database.py            # Database operations
│   ├── email.py               # Email notification service
│   ├── kakao.py               # Kakao notification service
│   └── translation_service.py # Translation service
├── templates/                 # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── email_base.html
│   ├── login.html
│   └── register.html

```
