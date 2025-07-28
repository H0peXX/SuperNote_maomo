from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
from datetime import datetime
from routes.user_route import user_bp , team_bp, member_bp, note_bp ,  super_note_bp


app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = 'your-secret-key'  # Required for flash messages
CORS(app)

# Routes for serving HTML pages
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/create-summary')
def create_summary():
    return render_template('create_summary.html')

@app.route('/create-text-summary')
def create_text_summary():
    return render_template('create_text_summary.html')

@app.route('/view-summary/<summary_id>')
def view_summary(summary_id):
    return render_template('view_summary.html')

@app.route('/edit-summary/<summary_id>')
def edit_summary(summary_id):
    return render_template('edit_summary.html')

# Register blueprints for API routes
app.register_blueprint(user_bp)
app.register_blueprint(team_bp)
app.register_blueprint(member_bp)
app.register_blueprint(note_bp)
app.register_blueprint(super_note_bp)


if __name__ == '__main__':
    app.run(debug=True)
