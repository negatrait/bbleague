from flask import Flask
from config import Config
import logging

app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logging.basicConfig(level=logging.DEBUG,
                    handlers=[
                        logging.FileHandler("bbleague.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Import and register blueprints
from routes.home import home_bp
from routes.team import team_bp
from routes.player import player_bp
from routes.error import error_bp

app.register_blueprint(home_bp)
app.register_blueprint(team_bp)
app.register_blueprint(player_bp)
app.register_blueprint(error_bp)

if __name__ == '__main__':
    app.run(debug=True)