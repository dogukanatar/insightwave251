# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from config import Config
from scheduler import SchedulerManager
from services.database import upsert_subscription, get_db_connection, get_recent_papers
from services.auth import authenticate_user
from services.content_generator import generate_email_content
from services.email import EmailService, KakaoService
from werkzeug.security import generate_password_hash
import logging
import re
from datetime import datetime, timedelta

# Initialize Flask
app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('INSTWAVE')

# Initialize scheduler
scheduler_manager = SchedulerManager(app)
scheduler_manager.start()

# Email regex for validation
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

# Routes
@app.route('/')
def home():
    """Redirect to login if not authenticated, else to dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not re.match(EMAIL_REGEX, email):
            flash('Invalid email format', 'error')
            return render_template('register.html')

        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,20}$', password):
            flash('Password must be 8-20 characters with letters and numbers', 'error')
            return render_template('register.html')

        try:
            password_hash = generate_password_hash(password)

            user_id = upsert_subscription(
                name=email.split('@')[0],
                email=email,
                password_hash=password_hash,
                topics=[1, 3, 4],  # AI/ML, CS, Math
                language='en',
                notification_method='email',
                active=True
            )

            session['user_id'] = user_id
            session['user_email'] = email
            session['user_language'] = 'en'

            flash('Registration successful! Set your preferences below.', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.exception("Registration failed")
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_language'] = user.get('language', 'en')
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        topics = request.form.getlist('topics')
        language = request.form.get('language', 'en')
        notification_method = request.form.get('notification_method', 'email')
        active = 'active' in request.form

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                UPDATE users 
                SET language = %s, 
                    notification_method = %s,
                    active = %s
                WHERE id = %s
            """, (language, notification_method, active, user_id))

            cur.execute("DELETE FROM user_topics WHERE user_id = %s", (user_id,))
            for topic_id in topics:
                cur.execute(
                    "INSERT INTO user_topics (user_id, topic_id) VALUES (%s, %s)",
                    (user_id, topic_id)
                )

            conn.commit()
            flash('Preferences updated successfully!', 'success')

            session['user_language'] = language
        except Exception as e:
            logger.error(f"Failed to update preferences: {str(e)}")
            flash('Failed to update preferences', 'error')
        finally:
            cur.close()
            conn.close()

    today = datetime.now()
    days_until_tuesday = (1 - today.weekday() + 7) % 7
    next_tuesday = today + timedelta(days=days_until_tuesday)
    next_tuesday_str = next_tuesday.strftime('%Y-%m-%d')

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 获取用户信息
        cur.execute("""
            SELECT id, email, language, notification_method, active
            FROM users
            WHERE id = %s
        """, (user_id,))
        user = cur.fetchone()

        cur.execute("""
            SELECT topic_id FROM user_topics WHERE user_id = %s
        """, (user_id,))
        user_topics = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT id, label FROM topics")
        all_topics = [{'id': row[0], 'label': row[1]} for row in cur.fetchall()]

        return render_template('dashboard.html',
                               email=user[1],
                               language=user[2],
                               notification_method=user[3],
                               active=user[4],
                               user_topics=user_topics,
                               all_topics=all_topics,
                               next_tuesday=next_tuesday_str)
    except Exception as e:
        logger.error(f"Failed to fetch user preferences: {str(e)}")
        flash('Failed to load preferences', 'error')
        return render_template('dashboard.html')
    finally:
        cur.close()
        conn.close()


@app.route('/send_weekly_digest_now', methods=['POST'])
def send_weekly_digest_now():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    conn = None
    cur = None
    try:
        user_id = session['user_id']
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
            flash('User not found', 'error')
            return redirect(url_for('dashboard'))

        user = {
            'id': user_row[0],
            'email': user_row[1],
            'name': user_row[2],
            'language': user_row[3],
            'notification_method': user_row[4],
            'topics': user_row[5]
        }

        papers = get_recent_papers()

        email_content = generate_email_content(papers, user)

        if user['notification_method'] in ['email', 'both']:
            success = EmailService.send_research_digest(user, email_content)
            if success:
                flash('Weekly digest sent to your email!', 'success')
            else:
                flash('Failed to send email. Please try again later.', 'error')

        if user['notification_method'] in ['kakao', 'both']:
            success = KakaoService.send_research_digest(user, email_content)
            if success:
                flash('Weekly digest sent via Kakao!', 'success')
            else:
                flash('Failed to send Kakao notification.', 'error')

        return redirect(url_for('dashboard'))


    except Exception as e:
        logger.error(f"Error sending weekly digest: {str(e)}")
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('dashboard'))
    finally:
        if cur: cur.close()
        if conn: conn.close()


@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
