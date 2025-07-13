from flask import Flask
from flask_cors import CORS
from routes.user_route import user_bp
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app, 
    resources={
        r"/*": {
            "origins": ["http://localhost:8000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": [
                "Content-Type",
                "Authorization",
                "Access-Control-Allow-Origin",
                "Referer",
                "User-Agent",
                "sec-ch-ua",
                "sec-ch-ua-mobile",
                "sec-ch-ua-platform",
                "Sec-Fetch-Mode"
            ]
        }
    },
    supports_credentials=True
)  # important

app.register_blueprint(user_bp)

load_dotenv()

if __name__ == '__main__':
    app.run(debug=True)
