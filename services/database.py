import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a simple connection pool
db_pool = pool.SimpleConnectionPool(
    1, 10,  # minconn, maxconn
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=5432
)

# Function to get a connection from the pool
def get_connection():
    return db_pool.getconn()

# Function to release a connection back to the pool
def release_connection(conn):
    db_pool.putconn(conn)

# Function to close all connections in the pool
def close_pool():
    db_pool.closeall()

# ----------------------
# Thesis table functions
# ----------------------

# Insert a new thesis record
def insert_thesis(title, author, ai_summary):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO thesis (title, author, ai_summary, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
                RETURNING id;
            """, (title, author, ai_summary))
            thesis_id = cur.fetchone()[0]
            conn.commit()
            return thesis_id
    except Exception as e:
        print(f"[DB ERROR] {e}")
        conn.rollback()
    finally:
        release_connection(conn)

# Get a thesis record by ID
def get_thesis_by_id(thesis_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM thesis WHERE id = %s;", (thesis_id,))
            result = cur.fetchone()
            return result
    except Exception as e:
        print(f"[DB ERROR] {e}")
    finally:
        release_connection(conn)

# Update AI summary for a thesis
def update_thesis_summary(thesis_id, ai_summary):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE thesis
                SET ai_summary = %s, updated_at = NOW()
                WHERE id = %s;
            """, (ai_summary, thesis_id))
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] {e}")
        conn.rollback()
    finally:
        release_connection(conn)

# Delete a thesis record by ID
def delete_thesis(thesis_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM thesis WHERE id = %s;", (thesis_id,))
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] {e}")
        conn.rollback()
    finally:
        release_connection(conn)


# ----------------------
# Users table functions
# ----------------------

# Insert a new user
def insert_user(email, name):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (email, name)
                VALUES (%s, %s)
                RETURNING id;
            """, (email, name))
            user_id = cur.fetchone()[0]
            conn.commit()
            return user_id
    except Exception as e:
        print(f"[DB ERROR] {e}")
        conn.rollback()
    finally:
        release_connection(conn)

# Get user info by email
def get_user_by_email(email):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s;", (email,))
            return cur.fetchone()
    except Exception as e:
        print(f"[DB ERROR] {e}")
    finally:
        release_connection(conn)


# ----------------------
# Topics table functions
# ----------------------

# Insert a new topic
def insert_topic(label):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO topics (label)
                VALUES (%s)
                RETURNING id;
            """, (label,))
            topic_id = cur.fetchone()[0]
            conn.commit()
            return topic_id
    except Exception as e:
        print(f"[DB ERROR] {e}")
        conn.rollback()
    finally:
        release_connection(conn)

# Get all topics
def get_all_topics():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM topics;")
            return cur.fetchall()
    except Exception as e:
        print(f"[DB ERROR] {e}")
    finally:
        release_connection(conn)


# ----------------------
# User_topics table functions
# ----------------------

# Link a user with a topic
def insert_user_topic(user_id, topic_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_topics (user_id, topic_id)
                VALUES (%s, %s)
                RETURNING id;
            """, (user_id, topic_id))
            ut_id = cur.fetchone()[0]
            conn.commit()
            return ut_id
    except Exception as e:
        print(f"[DB ERROR] {e}")
        conn.rollback()
    finally:
        release_connection(conn)

# Get topics linked to a user
def get_topics_by_user(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.id, t.label
                FROM user_topics ut
                JOIN topics t ON ut.topic_id = t.id
                WHERE ut.user_id = %s;
            """, (user_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"[DB ERROR] {e}")
    finally:
        release_connection(conn)
