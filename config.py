import os
import secrets

class Config:
    # Generate a random secret key if one doesn't exist
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'negatrait.mysql.pythonanywhere-services.com'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'negatrait'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'bbleaguepassword'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'negatrait$default'
