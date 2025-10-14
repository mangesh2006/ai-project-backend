from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)

    CORS(
        app,
        origins=["https://mystudysaathi.vercel.app"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"]
    )   

    from models.user import User
    from models.summaries import Summary

    from routes import auth_bp, gen_bp, get_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(gen_bp)
    app.register_blueprint(get_bp)

    return app