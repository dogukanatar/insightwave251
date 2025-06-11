import psycopg2
import logging
from datetime import datetime, timedelta
from flask import current_app

logger = logging.getLogger('INSTWAVE')


def get_db_connection():
    """Create and return a new database connection (DB 연결 생성)"""
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


def get_subscribed_users():
    """Get all users with email subscriptions (이메일 구독 사용자 조회)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT u.id, u.email, u.name, array_agg(ut.topic_id) AS topics
            FROM Users u
            JOIN User_topics ut ON u.id = ut.user_id
            GROUP BY u.id
        """)

        users = []
        for row in cur.fetchall():
            users.append({
                'id': row[0],
                'email': row[1],
                'name': row[2],
                'topics': row[3]
            })

        return users

    except Exception as e:
        logger.error(f"Database error in get_subscribed_users: {str(e)}")
        return []
    finally:
        cur.close()
        conn.close()


def insert_subscription(name, email, topics):
    """Insert new user subscription with validation"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Convert a list of strings to a list of integers
        topic_ids = [int(t) for t in topics]

        # Verify if the subject ID exists (using the list of integers)
        cur.execute("SELECT id FROM Topics WHERE id = ANY(%s::bigint[])", (topic_ids,))
        valid_topics = [row[0] for row in cur.fetchall()]

        if len(valid_topics) != len(topic_ids):
            invalid_ids = set(topic_ids) - set(valid_topics)
            raise ValueError(f"Invalid topic IDs: {', '.join(map(str, invalid_ids))}")

        # Insert user
        cur.execute(
            "INSERT INTO Users (name, email) VALUES (%s, %s) RETURNING id",
            (name, email)
        )
        user_id = cur.fetchone()[0]

        # Insert user topics
        for topic_id in topic_ids:
            cur.execute(
                "INSERT INTO User_topics (user_id, topic_id) VALUES (%s, %s)",
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
        logger.error(f"Insert subscription error: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()


def get_recent_papers():
    """Get papers with topics from last week """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        today = datetime.now()

        last_tuesday = today - timedelta(days=today.weekday() + 6)
        this_monday = today - timedelta(days=today.weekday())

        cur.execute("""
            SELECT t.id, t.title, t.author, t.ai_summary, t.created_at,
                   array_agg(top.id) AS topic_ids,
                   t.arxiv_id
            FROM thesis t
            JOIN paper_topics pt ON t.id = pt.paper_id
            JOIN topics top ON pt.topic_id = top.id
            WHERE t.created_at BETWEEN %s AND %s
            AND t.ai_summary IS NOT NULL
            GROUP BY t.id, t.arxiv_id
        """, (last_tuesday, this_monday))

        papers = []
        for row in cur.fetchall():
            try:
                ai_summary = json.loads(row[3]) if row[3] else {}
                papers.append({
                    'id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'ai_summary': ai_summary,
                    'date': row[4].strftime('%Y-%m-%d'),
                    'topics': row[5],
                    'link': f"https://arxiv.org/abs/{row[6]}" if row[6] else "#"
                })
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in ai_summary for paper {row[0]}")
        return papers
    except Exception as e:
        logger.error(f"Database error in get_recent_papers: {str(e)}")
        return []
    finally:
        cur.close()
        conn.close()
