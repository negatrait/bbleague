import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'your-username'
    MYSQL_PASSWORD = 'your-password'
    MYSQL_DB = 'bbroster'
