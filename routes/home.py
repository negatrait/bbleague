from flask import Blueprint, render_template, flash
from db import get_db_connection
import logging
import mysql.connector

home_bp = Blueprint('home', __name__)
logger = logging.getLogger(__name__)

@home_bp.route('/')
def home():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error. Please try again later.", "error")
            return render_template('index.html', teams=[])
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, name, race FROM teams')
        teams = cursor.fetchall()
        
        return render_template('index.html', teams=teams)
    except mysql.connector.Error as db_err:
        logger.error(f"Database error in home route: {db_err}")
        flash("An error occurred while loading teams from the database.", "error")
        return render_template('index.html', teams=[])
    except Exception as e:
        logger.error(f"Unexpected error in home route: {e}")
        flash("An unexpected error occurred. Please try again later.", "error")
        return render_template('index.html', teams=[])
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()