import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection
import json
import logging

team_bp = Blueprint('team', __name__)
logger = logging.getLogger(__name__)

@team_bp.route('/create_team', methods=['GET', 'POST'])
def create_team():
    conn = None
    cursor = None
    try:
        logger.debug("Received request to create a new team")
        try:
            file_path = "static/json/roster_template.json"
            with open(file_path, 'r') as f:
                data = json.load(f)
            races = data['rosters']
            logger.debug(f"Loaded roster template: {races}")
        except FileNotFoundError as e:
            logger.error(f"Error in create_team route: {e}")
            logger.debug(f"Roster template not found")
        
        if request.method == 'POST':
            team_name = request.form['team_name']
            team_race = request.form['team_race']
            logger.debug(f"Form data - team_name: {team_name}, team_race: {team_race}")
            
            # Get the selected race data
            selected_race = next((race for race in races if race['name'] == team_race), None)
            if not selected_race:
                flash(f"Race '{team_race}' not found in templates.", "error")
                return render_template('create_team.html', races=races)
            
            logger.debug(f"Selected race: {selected_race}")
            
            try:
                conn = get_db_connection()
                if conn is None:
                    flash("Database connection error. Please try again later.", "error")
                    return render_template('create_team.html', races=races)
                
                cursor = conn.cursor()
                
                # Insert the team
                cursor.execute('INSERT INTO teams (name, race, reroll_cost, apothecary) VALUES (%s, %s, %s, %s)', 
                               (team_name, team_race, selected_race['reroll_cost'], selected_race['apothecary']))
                
                team_id = cursor.lastrowid
                logger.debug(f"Inserted team with ID: {team_id}")
                
                # Add default players based on roster template
                for position in selected_race['positions']:
                    cursor.execute('''
                        INSERT INTO players (team_id, position, ma, st, ag, pa, av, skills, cost)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        team_id, 
                        position['position'],
                        position['ma'],
                        position['st'],
                        position['ag'],
                        position['pa'],
                        position['av'],
                        ','.join(position['skills']),
                        position['cost']
                    ))
                
                conn.commit()
                flash(f"Team '{team_name}' created successfully!", "success")
                return redirect(url_for('team.view_team', team_id=team_id))
            
            except mysql.connector.Error as db_err:
                logger.error(f"Database error during team creation: {db_err}")
                flash("An error occurred while creating the team.", "error")
            except Exception as e:
                logger.error(f"Error in create_team route: {e}")
                flash("An unexpected error occurred. Please try again later.", "error")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        
        return render_template('create_team.html', races=races)
    except Exception as e:
        logger.error(f"Error in create_team route: {e}")
        flash("An error occurred while loading the team creation page.", "error")
        return redirect(url_for('home.home'))

@team_bp.route('/view_team/<int:team_id>')
def view_team(team_id):
    conn = None
    cursor = None
    try:
        logger.debug(f"Received request to view team_id: {team_id}")
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error. Please try again later.", "error")
            return redirect(url_for('home.home'))
        
        cursor = conn.cursor(dictionary=True)
        
        # Get team details
        cursor.execute('SELECT * FROM teams WHERE id = %s', (team_id,))
        team = cursor.fetchone()
        if not team:
            flash(f"Team with ID {team_id} not found.", "error")
            return redirect(url_for('home.home'))
        
        logger.debug(f"Team details: {team}")
        
        # Get team players
        cursor.execute('SELECT * FROM players WHERE team_id = %s', (team_id,))
        players = cursor.fetchall()
        logger.debug(f"Team players: {players}")
        
        # Calculate team value
        team_value = sum(player['cost'] for player in players)
        logger.debug(f"Team value: {team_value}")
        
        return render_template('view_team.html', team=team, players=players, team_value=team_value)
    except mysql.connector.Error as db_err:
        logger.error(f"Database error in view_team route: {db_err}")
        flash("An error occurred while loading the team details.", "error")
        return redirect(url_for('home.home'))
    except Exception as e:
        logger.error(f"Unexpected error in view_team route: {e}")
        flash("An unexpected error occurred. Please try again later.", "error")
        return redirect(url_for('home.home'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()