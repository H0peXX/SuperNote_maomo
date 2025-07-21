# SuperNote Maomo

A text summarization application that uses Google's Gemini 2.5-flash model to generate concise summaries and stores them in MongoDB.

## Features

- Text summarization using Gemini 2.5-flash model
- MongoDB integration for storing summaries
- Clean and simple web interface
- Datetime tracking for each summary

## Data Structure

Summaries are stored in MongoDB with the following format:
```json
{
    "Header": "Summary Title",
    "Topic": "Topic Category",
    "Sum": "Generated Summary Text",
    "Provider": "User Name",
    "DateTime": "DD/MM/YYYY HH:MM:SS",
    "LastUpdate": "DD/MM/YYYY HH:MM:SS"
}
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate    # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   cd backend
   python app.py
   ```

4. Access the application at http://127.0.0.1:5000

## Technologies Used

- Flask: Web framework
- MongoDB: Database
- Google Gemini: AI model for summarization
- Python 3.x

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

2. Start the application:

Option 1 - Using run-dev.ps1 (Recommended):
```powershell
.\run-dev.ps1
```
This will automatically start both backend and frontend in separate windows.

Option 2 - Manual start:

In Terminal 1 (Backend):
```bash
python backend/app.py
```
Backend runs on: http://127.0.0.1:5000

In Terminal 2 (Frontend):
```bash
cd frontend
python -m http.server 8000
```
Frontend runs on: http://localhost:8000

To stop servers:
- For run-dev.ps1: Close both PowerShell windows
- For manual start: Press Ctrl+C in each terminal

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
