import psycopg2
import os

# Get DB credentials from environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
)
cur = conn.cursor()

# Create tables based on your ERD

# users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    language VARCHAR(50),
    notification_method VARCHAR(50),
    password_hash VARCHAR(255),
    active BOOLEAN DEFAULT TRUE
);
""")

# topics table
cur.execute("""
CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    label VARCHAR(255) NOT NULL
);
""")

# thesis table
cur.execute("""
CREATE TABLE IF NOT EXISTS thesis (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    author VARCHAR(500),
    ai_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    arxiv_id VARCHAR(255),
    publish_date DATE,
    categories VARCHAR(500),
    summary TEXT
);
""")

# paper_topics table (join table between thesis and topics)
cur.execute("""
CREATE TABLE IF NOT EXISTS paper_topics (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER REFERENCES thesis(id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE
);
""")

# arxiv_category_mapping table
cur.execute("""
CREATE TABLE IF NOT EXISTS arxiv_category_mapping (
    arxiv_category VARCHAR(50) PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE
);
""")

# user_topics table (join table between users and topics)
cur.execute("""
CREATE TABLE IF NOT EXISTS user_topics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE
);
""")

conn.commit()
cur.close()
conn.close()

print("Database initialized successfully.")
