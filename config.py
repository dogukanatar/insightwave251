import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SCHEDULER_TIMEZONE = 'Asia/Seoul'
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    BUCKET_NAME = os.getenv('BUCKET_NAME')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
