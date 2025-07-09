from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///supernote.db'
db = SQLAlchemy(app)

@app.route('/')
def home():
    return 'SuperNote Application'

if __name__ == '__main__':
    app.run(debug=True)
