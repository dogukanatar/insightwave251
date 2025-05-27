# app.py
from flask import Flask, render_template, request, jsonify
from scheduler import SchedulerManager
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
    """Handle form submission (mock version)"""
    user_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'topics': request.form.getlist('topics')
    }
    logger.info(f"New subscription: {user_data}")
    # TODO: Add real database insert
    return jsonify({'status': 'success', 'message': 'Subscription received!'})

@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    """Ensure scheduler shutdown on app exit"""
    scheduler_manager.shutdown()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
