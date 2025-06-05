# app.py
from flask import Flask, render_template, request, jsonify
from scheduler import SchedulerManager
from services.database import insert_subscription
import logging

# Initialize Flask
app = Flask(__name__)
app.config.from_object('config.Config')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('INSTWAVE')

# Initialize scheduler
scheduler_manager = SchedulerManager(app)
scheduler_manager.start()

# Routes
@app.route('/')
def subscribe_page():
    """Render subscription form page"""
    return render_template('subscribe.html')


@app.route('/submit', methods=['POST'])
def handle_subscription():
    """Handle form submission"""
    name = request.form.get('name')
    email = request.form.get('email')
    topics = request.form.getlist('topics')

    logger.debug(f"Received subscription: name={name}, email={email}, topics={topics}")

    if not name or not email or len(topics) < 3:
        error_msg = f"Invalid input: name={name}, email={email}, topics_count={len(topics)}"
        logger.warning(error_msg)
        return jsonify({'status': 'error', 'message': error_msg}), 400

    try:
        user_id = insert_subscription(name, email, topics)
        logger.info(f"New subscription saved: ID={user_id}")
        return jsonify({
            'status': 'success',
            'message': 'Subscription received!',
            'user_id': user_id
        })
    except ValueError as ve:
        error_msg = f"Invalid topics: {str(ve)}"
        logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 400
    except Exception as e:
        error_msg = f"Subscription failed: {str(e)}"
        logger.exception(error_msg)
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
