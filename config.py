import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MYSQL_HOST = 'negatrait.mysql.pythonanywhere-services.com'
    MYSQL_USER = 'negatrait'
    MYSQL_PASSWORD = 'bbleaguepassword'
    MYSQL_DB = 'default'
