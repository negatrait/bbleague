from flask import Flask
from config import Config
import logging
from logging.handlers import TimedRotatingFileHandler

app = Flask(__name__)
app.config.from_object(Config)

# Setup logging with log rotation
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log_handler = TimedRotatingFileHandler('bbleague.log', when='midnight', interval=1, backupCount=30)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.DEBUG)

app_logger = logging.getLogger(__name__)
app_logger.setLevel(logging.DEBUG)
app_logger.addHandler(log_handler)
app_logger.addHandler(logging.StreamHandler())

# Import and register blueprints
from routes.home import home_bp
from routes.team import team_bp
from routes.player import player_bp
from routes.error import error_bp

app.register_blueprint(home_bp)
app.register_blueprint(team_bp)
app.register_blueprint(player_bp)
app.register_blueprint(error_bp)

# Import and register commands
from commands.init_db import init_db
app.cli.command('init-db')(init_db)

if __name__ == '__main__':
    app.run(debug=True)