import os
import secrets

class Config:
    # Generate a random secret key if one doesn't exist
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'password'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'bbleague'