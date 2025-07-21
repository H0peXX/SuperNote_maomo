# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python backend/app.py"

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; python -m http.server 8000"
