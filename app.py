from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import json
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    conn = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name, race FROM teams')
    teams = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', teams=teams)

@app.route('/create_team', methods=['GET', 'POST'])
def create_team():
    with open('static/json/roster_template.json') as f:
        data = json.load(f)
        races = data['rosters']

    if request.method == 'POST':
        team_name = request.form['team_name']
        team_race = request.form['team_race']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO teams (name, race) VALUES (%s, %s)', (team_name, team_race))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))

    return render_template('create_team.html', races=races)

@app.route('/view_team/<int:team_id>')
def view_team(team_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM teams WHERE id = %s', (team_id,))
    team = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('view_team.html', team=team)

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop tables if they exist
    cursor.execute('DROP TABLE IF EXISTS teams')
    
    # Create tables
    cursor.execute('''
        CREATE TABLE teams (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            race VARCHAR(50) NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print('Database initialized.')

if __name__ == '__main__':
    app.run(debug=True)
