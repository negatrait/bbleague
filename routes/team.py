from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection
import json
import logging

team_bp = Blueprint('team', __name__)
logger = logging.getLogger(__name__)

@team_bp.route('/create_team', methods=['GET', 'POST'])
def create_team():
    # Your existing create_team logic here
    pass

@team_bp.route('/view_team/<int:team_id>')
def view_team(team_id):
    # Your existing view_team logic here
    pass