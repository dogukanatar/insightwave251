# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SCHEDULER_TIMEZONE = 'Asia/Seoul'
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')

# Database configuration added
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')