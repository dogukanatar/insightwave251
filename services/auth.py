import logging
from werkzeug.security import check_password_hash
from .database import get_db_connection, get_user_by_email

logger = logging.getLogger('INSTWAVE')

def authenticate_user(email, password):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, email, password_hash, language, notification_method 
            FROM users 
            WHERE email = %s
        """, (email,))
        user = cur.fetchone()
        if user and check_password_hash(user[3], password):
            return {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'language': user[4],
                'notification_method': user[5]
            }
        return None
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return None
    finally:
        cur.close()
        conn.close()
