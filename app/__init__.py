from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)

    from models.user import User
    from models.summaries import Summary

    from routes.auth import auth_bp
    from routes.generate import gen_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(gen_bp)

    return app