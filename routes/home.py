from flask import Blueprint, render_template, flash
from db import get_db_connection
import logging

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
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        flash("An error occurred while loading teams.", "error")
        return render_template('index.html', teams=[])
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()