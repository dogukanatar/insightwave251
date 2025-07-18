import psycopg2
import json
import logging
from datetime import datetime, timedelta
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger('INSTWAVE')

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=current_app.config['DB_HOST'],
            database=current_app.config['DB_NAME'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            options=f"-c timezone=Asia/Seoul"
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

def get_user_by_email(email):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, email, password_hash, language, notification_method
            FROM users
            WHERE email = %s
        """, (email,))
        user = cur.fetchone()
        if user:
            return {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'password_hash': user[3],
                'language': user[4],
                'notification_method': user[5]
            }
        return None
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def upsert_subscription(name, email, password_hash, topics, language='en', notification_method='email', active=True):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        topic_ids = [int(t) for t in topics]
        cur.execute("SELECT id FROM topics WHERE id = ANY(%s)", (topic_ids,))
        valid_topics = [row[0] for row in cur.fetchall()]
        if len(valid_topics) != len(topic_ids):
            invalid_ids = set(topic_ids) - set(valid_topics)
            raise ValueError(f"Invalid topic IDs: {', '.join(map(str, invalid_ids))}")
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        if existing_user:
            user_id = existing_user[0]
            cur.execute(
                "UPDATE users SET name = %s, password_hash = %s, language = %s, notification_method = %s, active = %s WHERE id = %s",
                (name, password_hash, language, notification_method, active, user_id)
            )
        else:
            cur.execute(
                "INSERT INTO users (name, email, password_hash, language, notification_method, active) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (name, email, password_hash, language, notification_method, active)
            )
            user_id = cur.fetchone()[0]
        cur.execute("DELETE FROM user_topics WHERE user_id = %s", (user_id,))
        for topic_id in topic_ids:
            cur.execute(
                "INSERT INTO user_topics (user_id, topic_id) VALUES (%s, %s)",
                (user_id, topic_id)
            )
        conn.commit()
        return user_id
    except ValueError as ve:
        logger.error(f"Value error: {str(ve)}")
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        logger.error(f"Upsert subscription error: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_subscribed_users():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.email, u.name, u.language, u.notification_method,
                   array_agg(ut.topic_id) AS topics
            FROM users u
            JOIN user_topics ut ON u.id = ut.user_id
            GROUP BY u.id
        """)
        users = []
        for row in cur.fetchall():
            users.append({
                'id': row[0],
                'email': row[1],
                'name': row[2],
                'language': row[3],
                'notification_method': row[4],
                'topics': row[5]
            })
        return users
    except Exception as e:
        logger.error(f"Database error in get_subscribed_users: {str(e)}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_recent_papers():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        today = datetime.now()
        days_since_tuesday = (today.weekday() - 1) % 7
        last_tuesday = today - timedelta(days=days_since_tuesday + 7)
        this_monday = today - timedelta(days=today.weekday())
        cur.execute("""
            SELECT id, title, author, ai_summary, created_at,
                   arxiv_id, categories
            FROM thesis
            WHERE created_at BETWEEN %s AND %s
            AND ai_summary IS NOT NULL
        """, (last_tuesday, this_monday))
        papers = []
        for row in cur.fetchall():
            try:
                categories = []
                if row[6]:
                    if isinstance(row[6], str):
                        categories_str = row[6].strip('{}')
                        categories = [cat.strip() for cat in categories_str.split(',')] if categories_str else []
                    elif isinstance(row[6], list):
                        categories = row[6]
                    else:
                        logger.warning(f"Unexpected categories type for paper {row[0]}: {type(row[6])}")
                top_level_categories = set()
                for category in categories:
                    if isinstance(category, str) and '.' in category:
                        top_level = category.split('.')[0]
                        top_level_categories.add(top_level)
                    elif isinstance(category, str):
                        top_level_categories.add(category)
                if top_level_categories:
                    cur.execute("""
                        SELECT DISTINCT topic_id 
                        FROM arxiv_category_mapping 
                        WHERE arxiv_category = ANY(%s)
                    """, (list(top_level_categories),))
                    topic_ids = [r[0] for r in cur.fetchall()]
                else:
                    topic_ids = []
                ai_summary = json.loads(row[3]) if row[3] else {}
                papers.append({
                    'id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'ai_summary': ai_summary,
                    'date': row[4].strftime('%Y-%m-%d'),
                    'topics': topic_ids,
                    'link': f"https://arxiv.org/abs/{row[5]}" if row[5] else "#"
                })
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in ai_summary for paper {row[0]}: {e}")
            except Exception as e:
                logger.error(f"Error processing paper {row[0]}: {e}")
        return papers
    except Exception as e:
        logger.error(f"Database error in get_recent_papers: {str(e)}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
