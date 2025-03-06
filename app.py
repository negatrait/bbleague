from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
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
    return render_template('index.html')

@app.route('/create_team', methods=['GET', 'POST'])
def create_team():
    if request.method == 'POST':
        team_name = request.form['team_name']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO teams (name) VALUES (%s)', (team_name,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))
    return render_template('create_team.html')

@app.route('/view_team/<int:team_id>')
def view_team(team_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM teams WHERE id = %s', (team_id,))
    team = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('view_team.html', team=team)

if __name__ == '__main__':
    app.run(debug=True)
