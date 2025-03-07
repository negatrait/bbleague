import json
import logging
from flask import current_app
from db import get_db_connection

logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with teams and players tables."""
    try:
        conn = get_db_connection()
        if conn is None:
            logger.error("Failed to connect to database.")
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
            player_count = min(2, pos['max_count']) # Add up to 2 of each position for sample data
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
            player_count = min(2, pos['max_count']) # Add up to 2 of each position for sample data
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
        logger.info('Database initialized with sample data.')
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()