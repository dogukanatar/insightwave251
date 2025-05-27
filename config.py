# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SCHEDULER_TIMEZONE = 'Asia/Seoul'
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')
    MOCK_MODE = True  # Flag for mock data
