# INSTWAVE Research Digest System

## Project Overview

INSTWAVE is an AI-powered research paper digest platform that delivers personalized summaries of recent academic publications directly to users. The system automatically collects papers from arXiv, generates AI summaries, and sends weekly digests based on user preferences. Users can subscribe to topics, choose notification methods, and receive updates in their preferred language.

## Key Features

- **Automated Paper Collection**: Daily arXiv crawler captures latest research papers
- **AI-Powered Summarization**: GPT-3.5 generates concise summaries with key insights
- **Personalized Digests**: Users receive weekly updates matching their interests
- **Multi-Platform Notifications**: Email and KakaoTalk delivery options
- **Bilingual Support**: English and Korean interfaces and content
- **User Dashboard**: Manage preferences, topics, and notification settings
- **Manual Digest Trigger**: Send current week's digest immediately
- **Kakao Integration**: Connect Kakao account for direct messaging

## Technology Stack

### Backend

- **Framework**: Flask (Python)
- **Database**: PostgreSQL (user data), Firestore (raw paper storage)
- **Scheduling**: Flask-APScheduler
- **AI Services**: OpenAI API (summarization, translation)
- **Email Service**: Resend API
- **Authentication**: Session-based with password hashing
- **APIs**: RESTful endpoints for frontend communication

### Frontend

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Context API
- **Routing**: Next.js Navigation

### Infrastructure

- **Cloud Storage**: Google Cloud Storage (GCS)
- **Task Scheduling**: Cloud Scheduler
- **Database Hosting**: Google Cloud SQL (PostgreSQL)

## Database Schema (PostgreSQL)

### Users

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    password_hash TEXT NOT NULL,
    language VARCHAR(2) DEFAULT 'en',
    notification_method VARCHAR(10) DEFAULT 'email',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

```

### Topics

```sql
CREATE TABLE topics (
    id BIGSERIAL PRIMARY KEY,
    label VARCHAR NOT NULL UNIQUE
);

```

### User Topics

```sql
CREATE TABLE user_topics (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    topic_id BIGINT REFERENCES topics(id) ON DELETE CASCADE
);

```

### Research Papers

```sql
CREATE TABLE thesis (
    id BIGSERIAL PRIMARY KEY,
    arxiv_id VARCHAR UNIQUE,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    content TEXT,
    ai_summary TEXT,
    publish_date DATE,
    categories TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

```

### ArXiv Category Mapping

```sql
CREATE TABLE arxiv_category_mapping (
    arxiv_category VARCHAR PRIMARY KEY,
    topic_id BIGINT REFERENCES topics(id) ON DELETE CASCADE
);

```

### Kakao Tokens

```sql
CREATE TABLE kakao_tokens (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

```

## Project Structure

```
INSTWAVE/
├── server(backend)/                  # Flask application
│   ├── app.py                # Main application entry point
│   ├── config.py             # Configuration settings
│   ├── scheduler.py          # Task scheduling manager
│   ├── requirements.txt      # Python dependencies
│   ├── services/             # Core application services
│   │   ├── core_services.py  # Authentication, content generation, notifications
│   │   └── database.py       # Database operations
│   └── templates/            # Email templates
│       └── email_base.html   # Base email template
│
└── web(frontend)/                 # Next.js application
    ├── app/                  # App router directory
    │   ├── login/            # Login page
    │   │   └── page.tsx
    │   ├── register/         # Registration page
    │   │   └── page.tsx
    │   ├── dashboard/        # User dashboard
    │   │   └── page.tsx
    │   ├── layout.tsx        # Root layout
    │   └── page.tsx          # Home page redirect
    ├── components/           # Reusable components
    │   ├── ui/               # shadcn/ui components
    │   ├── AppHeader.tsx     # Application header
    │   └── Logo.tsx          # Brand logo
    ├── context/              # Application contexts
    │   ├── AuthContext.tsx   # Authentication context
    │   └── LanguageContext.tsx # Language context
    ├── services/             # API services
    │   └── api.ts            # API client
    └── lib/                  # Utility functions
        └── utils.ts          # Helper functions

```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- PostgreSQL 15+
- Firebase account (for Firestore)
- Resend API key
- OpenAI API key
- Kakao Developers account

### Installation

1. **Clone repository**

```bash
git clone <https://github.com/dogukanatar/insightwave251.git>
cd insightwave251

```

1. **Backend setup**

```bash
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

1. **Frontend setup**

```bash
cd ../web
npm install

```

1. **Environment configuration**
Create `.env` files in both backend and frontend directories with required keys:

**Server / .env**

```
DB_HOST=your_db_host
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
RESEND_API_KEY=your_resend_key
OPENAI_API_KEY=your_openai_key
KAKAO_CLIENT_ID=your_kakao_client_id
KAKAO_REDIRECT_URI=your_kakao_redirect_url
SECRET_KEY=your_secret_key

```

**Web / (.env.local)**

```
NEXT_PUBLIC_BACKEND_URL=your_be_url

```

### Running the Application

1. **Start backend**

```bash
cd server
source venv/bin/activate
python app.py

```

1. **Start frontend**

```bash
cd ../web
npm run dev

```

1. **Access application**
Open `http://localhost:3000` in your browser

### Scheduled Tasks

1. Weekly AI summary generation (Tuesday 7:00 AM KST)
2. Weekly notification dispatch (Tuesday 8:00 AM KST)