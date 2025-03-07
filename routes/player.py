from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection
import json
import logging

player_bp = Blueprint('player', __name__)
logger = logging.getLogger(__name__)

@player_bp.route('/add_player/<int:team_id>', methods=['GET', 'POST'])
def add_player(team_id):
    conn = None
    cursor = None
    try:
        logger.debug(f"Received request to add player to team_id: {team_id}")
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error. Please try again later.", "error")
            return redirect(url_for('team.view_team', team_id=team_id))
        
        cursor = conn.cursor(dictionary=True)
        
        # Get team details
        cursor.execute('SELECT * FROM teams WHERE id = %s', (team_id,))
        team = cursor.fetchone()
        if not team:
            flash(f"Team with ID {team_id} not found.", "error")
            return redirect(url_for('home.home'))
        
        logger.debug(f"Team details: {team}")
        
        # Load roster template for the team's race
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, '..', 'static', 'json', 'roster_template.json')
        with open(file_path) as f:
            roster_data = json.load(f)
        
        # Find the appropriate race roster
        team_roster = next((roster for roster in roster_data['rosters'] if roster['name'] == team['race']), None)
        if not team_roster:
            flash(f"Roster template for {team['race']} not found.", "error")
            return redirect(url_for('team.view_team', team_id=team_id))
        
        logger.debug(f"Team roster: {team_roster}")
        
        if request.method == 'POST':
            position_name = request.form['position']
            player_name = request.form['player_name']
            logger.debug(f"Form data - position: {position_name}, player_name: {player_name}")
            
            # Find the position in the roster
            selected_position = next((pos for pos in team_roster['positions'] if pos['position'] == position_name), None)
            if not selected_position:
                flash(f"Position {position_name} not found for {team['race']}.", "error")
                return redirect(url_for('team.view_team', team_id=team_id))
            
            logger.debug(f"Selected position: {selected_position}")
            
            # Count current players of this position
            cursor.execute('SELECT COUNT(*) as count FROM players WHERE team_id = %s AND position = %s', 
                           (team_id, position_name))
            current_count = cursor.fetchone()['count']
            logger.debug(f"Current count of {position_name}: {current_count}")
            
            if current_count >= selected_position['max_count']:
                flash(f"Maximum number of {position_name}s ({selected_position['max_count']}) reached.", "error")
                return redirect(url_for('team.view_team', team_id=team_id))
            
            # Add the player
            cursor.execute('''
                INSERT INTO players (team_id, name, position, ma, st, ag, pa, av, skills, cost)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                team_id,
                player_name,
                position_name,
                selected_position['ma'],
                selected_position['st'],
                selected_position['ag'],
                selected_position['pa'],
                selected_position['av'],
                ','.join(selected_position['skills']),
                selected_position['cost']
            ))
            
            conn.commit()
            flash(f"{position_name} {player_name} added to your team!", "success")
            return redirect(url_for('team.view_team', team_id=team_id))
        
        return render_template('add_player.html', team=team, positions=team_roster['positions'])
    except mysql.connector.Error as db_err:
        logger.error(f"Database error in add_player route: {db_err}")
        flash("An error occurred while adding a player.", "error")
        return redirect(url_for('team.view_team', team_id=team_id))
    except Exception as e:
        logger.error(f"Unexpected error in add_player route: {e}")
        flash("An unexpected error occurred. Please try again later.", "error")
        return redirect(url_for('team.view_team', team_id=team_id))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@player_bp.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    conn = None
    cursor = None
    try:
        logger.debug(f"Received request to delete player_id: {player_id}")
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error. Please try again later.", "error")
            return redirect(url_for('home.home'))
        
        cursor = conn.cursor(dictionary=True)
        
        # Get player's team_id before deletion
        cursor.execute('SELECT team_id FROM players WHERE id = %s', (player_id,))
        player = cursor.fetchone()
        if not player:
            flash(f"Player with ID {player_id} not found.", "error")
            return redirect(url_for('home.home'))
        
        team_id = player['team_id']
        logger.debug(f"Player details: {player}")
        
        # Delete the player
        cursor.execute('DELETE FROM players WHERE id = %s', (player_id,))
        conn.commit()
        
        flash("Player successfully removed from the team.", "success")
        return redirect(url_for('team.view_team', team_id=team_id))
    except mysql.connector.Error as db_err:
        logger.error(f"Database error in delete_player route: {db_err}")
        flash("An error occurred while deleting the player.", "error")
        return redirect(url_for('home.home'))
    except Exception as e:
        logger.error(f"Unexpected error in delete_player route: {e}")
        flash("An unexpected error occurred. Please try again later.", "error")
        return redirect(url_for('home.home'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()