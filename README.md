# SuperNote Application (maomo)

A Flask-based note-taking application that allows users to create, manage, and organize their notes efficiently.

## Features

- User authentication system
- Note creation and management
- SQLite database integration
- Secure data handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/H0peXX/SuperNote_maomo.git
cd SuperNote_maomo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Update the database configuration in `connect.py`:
- Change the username and password to match your database settings

## Quick Start

1. Activate virtual environment (Windows):
```powershell
.venv\Scripts\Activate.ps1
```

2. Run backend (Terminal 1):
```bash
python app.py
```
Backend runs on: http://127.0.0.1:5000

3. Run frontend (Terminal 2):
```bash
cd frontend
python -m http.server 8000
```
Frontend runs on: http://localhost:8000

To stop servers: Press Ctrl+C in each terminal

## Tech Stack

- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- Flask-WTF 1.2.1
- SQLite Database

## Development

To contribute to this project:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open source and available under the MIT License.
