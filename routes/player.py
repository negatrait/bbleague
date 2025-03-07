from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection
import json
import logging

player_bp = Blueprint('player', __name__)
logger = logging.getLogger(__name__)

@player_bp.route('/add_player/<int:team_id>', methods=['GET', 'POST'])
def add_player(team_id):
    # Your existing add_player logic here
    pass

@player_bp.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    # Your existing delete_player logic here
    pass