from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
from datetime import datetime
from routes.user_route import user_bp , team_bp, member_bp, note_bp ,  super_note_bp


app = Flask(__name__, template_folder='../frontend/templates')
app.secret_key = 'your-secret-key'  # Required for flash messages
CORS(app)


# Register blueprints for API routes
app.register_blueprint(user_bp)
app.register_blueprint(team_bp)
app.register_blueprint(member_bp)
app.register_blueprint(note_bp)
app.register_blueprint(super_note_bp)


if __name__ == '__main__':
    app.run(debug=True)
