from flask import Flask
from flask_cors import CORS
from routes.user_route import user_bp
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app, origins=["http://localhost:8000"], supports_credentials=True)  # important

app.register_blueprint(user_bp)

load_dotenv()

if __name__ == '__main__':
    app.run(debug=True)
