import mysql.connector
from mysql.connector import Error
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        logger.debug("Attempting to connect to the database")
        conn = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        logger.debug("Database connection successful")
        return conn
    except mysql.connector.InterfaceError as ie:
        logger.error(f"Database interface error: {ie}")
    except mysql.connector.DatabaseError as de:
        logger.error(f"Database error: {de}")
    except mysql.connector.OperationalError as oe:
        logger.error(f"Operational error: {oe}")
    except mysql.connector.IntegrityError as ie:
        logger.error(f"Integrity error: {ie}")
    except Error as e:
        logger.error(f"Database connection error: {e}")
    return None