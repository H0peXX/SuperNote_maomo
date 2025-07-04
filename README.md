# maomo

cd front

pip install streamlit requests
pip install PyMuPDF
pip install google-generativeai

streamlit run app.py

cd backend
pip install fastapi uvicorn pydantic python-multipart PyMuPDF google-generativeai
pip install pdf2image
uvicorn main:app --reload --port 8000




docker compose up

for login pgadmin
user: admin@admin.com
pass: admin

for server
server: 172.18.0.1
port: 5432
name: maomo
POSTGRES_USER: admin
POSTGRES_PASSWORD: admin
POSTGRES_DB: maomo