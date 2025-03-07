from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import json
from config import Config
import logging
from mysql.connector import Error

app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logging.basicConfig(level=logging.DEBUG,
                    handlers=[
                        logging.FileHandler("bbleague.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        return conn
    except Error as e:
        logger.error(f"Database connection error: {e}")
        print(f"Connection error: {e}")  # For debugging
        return None

@app.route('/')
def home():
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error. Please try again later.", "error")
            return render_template('index.html', teams=[])
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, name, race FROM teams')
        teams = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('index.html', teams=teams)
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        flash("An error occurred while loading teams.", "error")
        return render_template('index.html', teams=[])

@app.route('/create_team', methods=['GET', 'POST'])
def create_team():
    conn = None
    cursor = None
    teams = []

    try:
        with open('static/json/roster_template.json') as f:
            data = json.load(f)
            races = data['rosters']

        if request.method == 'POST':
            team_name = request.form['team_name']
            team_race = request.form['team_race']
            
            # Get the selected race data
            selected_race = None
            for race in races:
                if race['name'] == team_race:
                    selected_race = race
                    break
            
            if not selected_race:
                flash(f"Race '{team_race}' not found in templates.", "error")
                return render_template('create_team.html', races=races)
            
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
                
                # Add default players based on roster template
                # For this example, we'll add one of each position type
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
                return redirect(url_for('view_team', team_id=team_id))
                
            except mysql.connector.Error as e:
                logger.error(f"Database error during team creation: {e}")
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
        return redirect(url_for('home'))


@app.route('/view_team/<int:team_id>')
def view_team(team_id):
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error. Please try again later.", "error")
            return redirect(url_for('home'))
            
        cursor = conn.cursor(dictionary=True)
        
        # Get team details
        cursor.execute('SELECT * FROM teams WHERE id = %s', (team_id,))
        team = cursor.fetchone()
        
        if not team:
            flash(f"Team with ID {team_id} not found.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for('home'))
        
        # Get team players
        cursor.execute('SELECT * FROM players WHERE team_id = %s', (team_id,))
        players = cursor.fetchall()
        
        # Calculate team value
        team_value = sum(player['cost'] for player in players)
        
        cursor.close()
        conn.close()
        
        return render_template('view_team.html', team=team, players=players, team_value=team_value)
    except Exception as e:
        logger.error(f"Error in view_team route: {e}")
        flash("An error occurred while loading the team details.", "error")
        return redirect(url_for('home'))

@app.route('/add_player/<int:team_id>', methods=['GET', 'POST'])
def add_player(team_id):
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error. Please try again later.", "error")
            return redirect(url_for('view_team', team_id=team_id))
            
        cursor = conn.cursor(dictionary=True)
        
        # Get team details
        cursor.execute('SELECT * FROM teams WHERE id = %s', (team_id,))
        team = cursor.fetchone()
        
        if not team:
            flash(f"Team with ID {team_id} not found.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for('home'))
        
        # Load roster template for the team's race
        with open('static/json/roster_template.json') as f:
            roster_data = json.load(f)
            
        # Find the appropriate race roster
        team_roster = None
        for roster in roster_data['rosters']:
            if roster['name'] == team['race']:
                team_roster = roster
                break
                
        if not team_roster:
            flash(f"Roster template for {team['race']} not found.", "error")
            return redirect(url_for('view_team', team_id=team_id))
            
        if request.method == 'POST':
            position_name = request.form['position']
            
            # Find the position in the roster
            selected_position = None
            for pos in team_roster['positions']:
                if pos['position'] == position_name:
                    selected_position = pos
                    break
                    
            if not selected_position:
                flash(f"Position {position_name} not found for {team['race']}.", "error")
                cursor.close()
                conn.close()
                return redirect(url_for('view_team', team_id=team_id))
                
            # Count current players of this position
            cursor.execute('SELECT COUNT(*) as count FROM players WHERE team_id = %s AND position = %s', 
                          (team_id, position_name))
            current_count = cursor.fetchone()['count']
            
            if current_count >= selected_position['max_count']:
                flash(f"Maximum number of {position_name}s ({selected_position['max_count']}) reached.", "error")
                cursor.close()
                conn.close()
                return redirect(url_for('view_team', team_id=team_id))
                
            # Add the player
            player_name = request.form['player_name']
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
            cursor.close()
            conn.close()
            return redirect(url_for('view_team', team_id=team_id))
            
        cursor.close()
        conn.close()
        return render_template('add_player.html', team=team, positions=team_roster['positions'])
    except Exception as e:
        logger.error(f"Error in add_player route: {e}")
        flash("An error occurred while adding a player.", "error")
        return redirect(url_for('view_team', team_id=team_id))

@app.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error. Please try again later.", "error")
            return redirect(url_for('home'))
            
        cursor = conn.cursor(dictionary=True)
        
        # Get player's team_id before deletion
        cursor.execute('SELECT team_id FROM players WHERE id = %s', (player_id,))
        player = cursor.fetchone()
        
        if not player:
            flash(f"Player with ID {player_id} not found.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for('home'))
            
        team_id = player['team_id']
        
        # Delete the player
        cursor.execute('DELETE FROM players WHERE id = %s', (player_id,))
        conn.commit()
        
        flash("Player successfully removed from the team.", "success")
        cursor.close()
        conn.close()
        return redirect(url_for('view_team', team_id=team_id))
    except Exception as e:
        logger.error(f"Error in delete_player route: {e}")
        flash("An error occurred while deleting the player.", "error")
        return redirect(url_for('home'))

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database with teams and players tables."""
    try:
        conn = get_db_connection()
        if conn is None:
            print("Failed to connect to database.")
            return
            
        cursor = conn.cursor()
        
        # Drop tables if they exist
        cursor.execute('DROP TABLE IF EXISTS players')
        cursor.execute('DROP TABLE IF EXISTS teams')
        
        # Create teams table
        cursor.execute('''
            CREATE TABLE teams (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                race VARCHAR(50) NOT NULL,
                reroll_cost INT NOT NULL DEFAULT 50000,
                apothecary BOOLEAN NOT NULL DEFAULT true,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create players table
        cursor.execute('''
            CREATE TABLE players (
                id INT AUTO_INCREMENT PRIMARY KEY,
                team_id INT NOT NULL,
                name VARCHAR(100) DEFAULT NULL,
                position VARCHAR(50) NOT NULL,
                ma INT NOT NULL,
                st INT NOT NULL,
                ag INT NOT NULL,
                pa INT NOT NULL,
                av INT NOT NULL,
                skills TEXT,
                cost INT NOT NULL,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
            )
        ''')
        
        # Create sample data
        cursor.execute('''
            INSERT INTO teams (name, race, reroll_cost, apothecary)
            VALUES 
            ('Reikland Reavers', 'Human', 50000, true),
            ('Orcland Raiders', 'Orc', 60000, true)
        ''')
        
        # Get sample roster data
        with open('static/json/roster_template.json') as f:
            roster_data = json.load(f)
            
        # Add players for Reikland Reavers (Humans)
        human_positions = next((r['positions'] for r in roster_data['rosters'] if r['name'] == 'Human'), [])
        for pos in human_positions:
            player_count = min(2, pos['max_count'])  # Add up to 2 of each position for sample data
            for i in range(player_count):
                cursor.execute('''
                    INSERT INTO players (team_id, name, position, ma, st, ag, pa, av, skills, cost)
                    VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    f"Human {pos['position']} {i+1}",
                    pos['position'],
                    pos['ma'],
                    pos['st'],
                    pos['ag'],
                    pos['pa'],
                    pos['av'],
                    ','.join(pos['skills']),
                    pos['cost']
                ))
                
        # Add players for Orcland Raiders (Orcs)
        orc_positions = next((r['positions'] for r in roster_data['rosters'] if r['name'] == 'Orc'), [])
        for pos in orc_positions:
            player_count = min(2, pos['max_count'])  # Add up to 2 of each position for sample data
            for i in range(player_count):
                cursor.execute('''
                    INSERT INTO players (team_id, name, position, ma, st, ag, pa, av, skills, cost)
                    VALUES (2, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    f"Orc {pos['position']} {i+1}",
                    pos['position'],
                    pos['ma'],
                    pos['st'],
                    pos['ag'],
                    pos['pa'],
                    pos['av'],
                    ','.join(pos['skills']),
                    pos['cost']
                ))
                
        conn.commit()
        cursor.close()
        conn.close()
        print('Database initialized with sample data.')
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
