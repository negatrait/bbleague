from flask import Blueprint, render_template
import logging

error_bp = Blueprint('error', __name__)
logger = logging.getLogger(__name__)

@error_bp.app_errorhandler(404)
def page_not_found(e):
    logger.error(f"404 error: {e}")
    return render_template('404.html'), 404

@error_bp.app_errorhandler(500)
def server_error(e):
    logger.error(f"500 error: {e}")
    return render_template('500.html'), 500