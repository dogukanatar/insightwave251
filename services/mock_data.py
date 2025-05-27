# services/mock_data.py
from datetime import datetime
import random

MOCK_USERS = [
    {
        "id": 1,
        "email": "liuyuheng0035@gmail.com",
        "name": "Test User",
        "preferences": {
            "channels": ["email"],
            "topics": [0, 2, 4]
        }
    }
]

def get_subscribed_users():
    """Get all subscribed users (mock version)"""
    return [u for u in MOCK_USERS if 'email' in u['preferences']['channels']]

def get_recent_papers():
    """Get recent papers for email (mock version)"""
    return [generate_daily_content(['AI']) for _ in range(3)]

def generate_daily_content(topics):
    """Generate mock paper data"""
    return {
        "title": f"Breakthrough in {random.choice(['AI', 'Physics'])}",
        "authors": [f"Researcher {chr(65+i)}" for i in range(3)],
        "date": datetime.now().strftime("%Y-%m-%d"),
        "link": f"https://arxiv.org/abs/{random.randint(1000,9999)}"
    }
