from flask import Flask, request, jsonify, session, redirect
from config import Config
from scheduler import SchedulerManager
from services.database import get_db_connection, get_recent_papers
from services.core_services import AuthService, ContentService, EmailService, KakaoService
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import re
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('INSTWAVE')

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,20}$'

scheduler_manager = SchedulerManager(app)
scheduler_manager.start()

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify(success=False, message="Email and password are required"), 400

    if not re.match(EMAIL_REGEX, email):
        return jsonify(success=False, message="Invalid email format"), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, password_hash, language, notification_method, active FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            return jsonify(success=False, message="User not found"), 404

        if not check_password_hash(user[3], password):
            return jsonify(success=False, message="Invalid password"), 401

        session['user_id'] = user[0]
        session['user_email'] = user[2]

        return jsonify(success=True, user={
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'language': user[4],
            'notification_method': user[5],
            'active': user[6]
        }), 200

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return jsonify(success=False, message="Internal server error"), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    topics = data.get('topics', [])

    if not name or not email or not password:
        return jsonify(success=False, message="All fields are required"), 400

    if not re.match(EMAIL_REGEX, email):
        return jsonify(success=False, message="Invalid email format"), 400

    if not re.match(PASSWORD_REGEX, password):
        return jsonify(success=False, message="Password must be 8-20 characters with letters and numbers"), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return jsonify(success=False, message="Email already exists"), 409

        password_hash = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (name, email, password_hash, language, notification_method, active) VALUES (%s, %s, %s, 'en', 'email', TRUE) RETURNING id",
            (name, email, password_hash)
        )
        user_id = cur.fetchone()[0]

        for topic_id in topics:
            cur.execute("INSERT INTO user_topics (user_id, topic_id) VALUES (%s, %s)", (user_id, topic_id))

        conn.commit()
        session['user_id'] = user_id
        session['user_email'] = email

        return jsonify(success=True, user_id=user_id), 201

    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        return jsonify(success=False, message="Registration failed"), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

FRONTEND_URL = "http://localhost:3000"

@app.route('/api/kakao_auth', methods=['GET'])
def api_kakao_auth():
    if 'user_id' not in session:
        return jsonify(success=False, message="Unauthorized"), 401
    try:
        auth_url = KakaoService.generate_auth_url(str(session['user_id']))
        return jsonify(success=True, auth_url=auth_url)
    except Exception as e:
        logger.error(f"Kakao auth failed: {str(e)}")
        return jsonify(success=False, message="Failed to start Kakao authorization"), 500


@app.route('/api/auth/kakao/callback')
def api_kakao_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    if error:
        logger.error(f"Kakao authorization denied: {error}")
        return redirect(f"{FRONTEND_URL}/dashboard?kakao_error={error}")
    if not code or not state:
        logger.error("Invalid Kakao callback request")
        return redirect(f"{FRONTEND_URL}/dashboard?kakao_error=invalid_request")
    try:
        if KakaoService.handle_authorization(code, state):
            return redirect(f"{FRONTEND_URL}/dashboard?kakao_success=1")
        else:
            return redirect(f"{FRONTEND_URL}/dashboard?kakao_error=connection_failed")
    except Exception as e:
        logger.error(f"Kakao callback error: {str(e)}")
        return redirect(f"{FRONTEND_URL}/dashboard?kakao_error=internal_error")

@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    if 'user_id' not in session:
        return jsonify(success=False, message="Unauthorized"), 401

    user_id = session['user_id']

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, language, notification_method, active FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()

        if not user:
            return jsonify(success=False, message="User not found"), 404

        cur.execute("SELECT 1 FROM kakao_tokens WHERE user_id = %s", (user_id,))
        kakao_connected = cur.fetchone() is not None

        cur.execute("SELECT topic_id FROM user_topics WHERE user_id = %s", (user_id,))
        user_topics = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT id, label FROM topics")
        all_topics = [{'id': row[0], 'label': row[1]} for row in cur.fetchall()]

        today = datetime.now()
        days_until_tuesday = (1 - today.weekday() + 7) % 7
        next_tuesday = today + timedelta(days=days_until_tuesday)
        next_tuesday_str = next_tuesday.strftime('%Y-%m-%d')

        return jsonify(success=True, data={
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'language': user[3],
            'notification_method': user[4],
            'active': user[5],
            'user_topics': user_topics,
            'all_topics': all_topics,
            'next_tuesday': next_tuesday_str,
            'kakao_connected': kakao_connected
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch dashboard data: {str(e)}")
        return jsonify(success=False, message="Internal server error"), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/topics', methods=['GET'])
def api_topics():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, label FROM topics")
        topics = [{'id': row[0], 'label': row[1]} for row in cur.fetchall()]
        return jsonify(success=True, topics=topics)
    except Exception as e:
        logger.error(f"Failed to get topics: {str(e)}")
        return jsonify(success=False, message="Failed to get topics"), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/update_preferences', methods=['POST'])
def api_update_preferences():
    if 'user_id' not in session:
        return jsonify(success=False, message="Unauthorized"), 401

    user_id = session['user_id']
    data = request.get_json()

    topics = data.get('topics', [])
    language = data.get('language', 'en')
    notification_method = data.get('notification_method', 'email')
    active = data.get('active', True)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE users 
            SET language = %s, notification_method = %s, active = %s
            WHERE id = %s
        """, (language, notification_method, active, user_id))

        cur.execute("DELETE FROM user_topics WHERE user_id = %s", (user_id,))
        for topic_id in topics:
            cur.execute("INSERT INTO user_topics (user_id, topic_id) VALUES (%s, %s)", (user_id, topic_id))

        conn.commit()
        return jsonify(success=True, message="Preferences updated"), 200

    except Exception as e:
        logger.error(f"Failed to update preferences: {str(e)}")
        return jsonify(success=False, message="Update failed"), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/send_digest_now', methods=['POST'])
def api_send_digest_now():
    if 'user_id' not in session:
        return jsonify(success=False, message="Unauthorized"), 401

    user_id = session['user_id']
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.email, u.name, u.language, u.notification_method,
                   array_agg(ut.topic_id) AS topics
            FROM users u
            JOIN user_topics ut ON u.id = ut.user_id
            WHERE u.id = %s
            GROUP BY u.id
        """, (user_id,))
        user_row = cur.fetchone()

        if not user_row:
            return jsonify(success=False, message="User not found"), 404

        user = {
            'id': user_row[0],
            'email': user_row[1],
            'name': user_row[2],
            'language': user_row[3],
            'notification_method': user_row[4],
            'topics': user_row[5]
        }

        papers = get_recent_papers()
        email_content = ContentService.generate_email_content(papers, user)

        results = {"email": False, "kakao": False}

        if user['notification_method'] in ['email', 'both']:
            success = EmailService.send_research_digest(user, email_content)
            results["email"] = success

        if user['notification_method'] in ['kakao', 'both']:
            success = KakaoService.send_research_digest(user, email_content)
            results["kakao"] = success

        if all(results.values()):
            return jsonify(success=True, message="Digest sent successfully via all selected methods")
        elif any(results.values()):
            sent_methods = [k for k, v in results.items() if v]
            return jsonify(success=True, message=f"Digest sent via {', '.join(sent_methods)} but failed for others")
        else:
            return jsonify(success=False, message="Failed to send digest via any method")

    except Exception as e:
        logger.error(f"Error sending weekly digest: {str(e)}")
        return jsonify(success=False, message="An error occurred. Please try again."), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify(success=True, message="Logged out"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
