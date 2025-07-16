from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__, template_folder='../frontend/templates')
app.secret_key = 'your-secret-key'  # Required for flash messages

# MongoDB setup
uri = "mongodb+srv://VanijTarnakij:admin@cluster0.qcym40v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.maomo
notes_collection = db.notes

# Gemini setup with 2.5-flash model
genai.configure(api_key='AIzaSyDL-p6OrYr5fUKdGHmPCbdNImN4-v9BBcg')
model = genai.GenerativeModel('gemini-2.5-flash')  # Using Gemini 2.5-flash for faster responses

@app.route('/')
def index():
    return render_template('summarize.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        text = request.form.get('text')
        if not text:
            return render_template('summarize.html', error="Please enter some text to summarize.")
        
        # Generate summary using Gemini
        response = model.generate_content(f"Please summarize the following text in a clear and concise way, maintaining the key points: {text}")
        summary = response.text
        
        return render_template('summarize.html', summary=summary)
    except Exception as e:
        return render_template('summarize.html', error=f"Error generating summary: {str(e)}")

@app.route('/save', methods=['POST'])
def save():
    try:
        summary = request.form.get('summary')
        header = request.form.get('header')
        topic = request.form.get('topic')
        provider = request.form.get('provider')
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        # Create document
        note = {
            "Header": header,
            "Topic": topic,
            "Sum": summary,
            "Provider": provider,
            "DateTime": current_date,
            "LastUpdate": current_date
        }
        
        # Save to MongoDB
        notes_collection.insert_one(note)
        
        return render_template('summarize.html', message="Summary saved successfully!")
    except Exception as e:
        return render_template('summarize.html', error=f"Error saving to database: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
