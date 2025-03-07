import mysql.connector
from mysql.connector import Error
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        return conn
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None