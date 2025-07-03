from flask import Flask
from app.routes.auth import auth

def create_app():
    app = Flask(__name__)
    app.secret_key = 'jangan dikasih tahu'
    app.register_blueprint(auth)

    return app
