from bson import ObjectId
from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from db.connect import *
from flask_cors import CORS
import bcrypt
import jwt
import os
from flask_cors import cross_origin
import google.generativeai as genai
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from ocr.typhoon_ocr.ocr_utils import ocr_document

load_dotenv()


# Gemini setup with 2.5-flash model
genai.configure(api_key=f"{os.getenv('GENAI_API_KEY')}")
model = genai.GenerativeModel('gemini-2.5-flash')  # Using Gemini 2.5-flash for faster responses

# Test Gemini connection
try:
    test_response = model.generate_content("Test connection to Gemini API.")
    print("Gemini API connection successful.")
except Exception as e:
    print(f"Gemini API connection failed: {e}")


# JWT settings
SECRET_KEY = f"{os.getenv('SECRET_KEY')}"  # Change this to a secure key in production
ALGORITHM = "HS256"



# Create blueprints for user, team, member, and note table routes
user_bp = Blueprint('user', __name__)
team_bp = Blueprint('team', __name__)
member_bp = Blueprint('member', __name__)
note_bp = Blueprint('note', __name__)
super_note_bp = Blueprint('super_note', __name__)

# Configure CORS for the blueprints
CORS(user_bp, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://localhost:5000"],
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
})
CORS(team_bp, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://localhost:5000"],
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
})
CORS(member_bp, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://localhost:5000"],
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
})

CORS(note_bp, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://localhost:5000"],
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
})
CORS(super_note_bp, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://localhost:5000"],
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
})

# --- Get session status ---
@user_bp.route('/api/session', methods=['GET'])
def check_session():
    # Get the token from the Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'logged_in': False})
    
    token = auth_header.split(' ')[1]
    try:
        # Decode and verify the JWT token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = decoded.get('sub')
        if username:
            return jsonify({'logged_in': True, 'username': username})
    except:
        pass
    
    return jsonify({'logged_in': False})


# --- Get first user (for test/demo) ---
@user_bp.route('/api/user', methods=['GET'])
def get_user():
    document = user_collection.find_one()
    if document and "username" in document:
        return jsonify({"username": document["username"]})
    else:
        return jsonify({"error": "No user found or 'username' field missing."}), 404


# --- Login route ---
@user_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = user_collection.find_one({'username': username})
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    # Compare password with hash in database
    stored_hash = user.get('password')
    if stored_hash and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        # Create JWT token
        token = jwt.encode({"sub": user['username']}, SECRET_KEY, algorithm=ALGORITHM)
        return jsonify({
            'message': 'Login successful',
            'username': user['username'],
            'access_token': token,
            'token_type': 'Bearer'
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401



# --- Signup route ---
@user_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    fname = data.get('fname')
    lname = data.get('lname')
    email = data.get('email')
    dob = data.get('dob')  # Expecting string (e.g. 'YYYY-MM-DD')
    create_at = data.get('create_at')  # Optional ISO datetime string
    print("Received data:", data)

    if not username or not password or not email:
        return jsonify({'error': 'Username, password, and email are required'}), 400

    existing_user = user_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409

    # Parse DOB
    dob_date = None
    if dob:
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'DOB must be in YYYY-MM-DD format'}), 400

    # Parse or set create_at
    if create_at:
        try:
            create_at_date = datetime.strptime(create_at, '%Y-%m-%dT%H:%M:%S')
        except Exception:
            create_at_date = datetime.utcnow()
    else:
        create_at_date = datetime.utcnow()

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user = {
        'username': username,
        'password': hashed_password.decode('utf-8'),
        'first_name': fname,
        'last_name': lname,
        'email': email,
        'dob': dob_date,
        'create_at': create_at_date,
    }

    user_collection.insert_one(new_user)

    return jsonify({'message': 'User created successfully', 'username': username}), 201


# --- Create team route ---
@team_bp.route('/api/team', methods=['POST'])
def create_team():
    data = request.get_json()
    team_name = data.get('team_name')
    team_description = data.get('team_description')
    team_members = data.get('team_members', [])

    if not team_name or not team_description:
        return jsonify({'error': 'Team name and description are required'}), 400

    new_team = {
        'team_name': team_name,
        'team_description': team_description,
        'created_at': datetime.utcnow()
    }

    team_collection.insert_one(new_team)
    member_collection.insert_many([
        {'team_name': team_name, 'member_email': team_members} 
    ])

    return jsonify({
        'message': 'Team created successfully',
        'team_name': team_name,
        'team_description': team_description
    }), 201



# --- Get all teams route (GET) ---
@team_bp.route('/api/teams', methods=['GET'])
def get_teams():
    teams = list(team_collection.find({}, {'_id': 0, 'team_name': 1}))
    return jsonify({'teams': teams})





# --- Summarize text input ---
@note_bp.route('/api/summarize', methods=['POST'])
@cross_origin()
def summarize():
    try:
        data = request.get_json()
        text = data.get('text')
        option_prompt = data.get('optionPrompt', '') 
        if not text:
            return jsonify({'error': 'Please enter some text to summarize.'}), 400
        
        system_prompt = "Your job is to summarize the provided text in a clear and concise way, maintaining the key points."
        structure_output = "Respond in text format only, without any additional formatting or HTML tags."
        prompt = (
        f"{system_prompt}\n\n"
        f"{structure_output}\n\n"
        f"{text}\n\n"
        f"This is the user's option: {option_prompt}.\n"
        "If the option relates to input formatting or instructions, please follow it."
        )
        response = model.generate_content(prompt)
        summary = response.text
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': f"Error generating summary: {str(e)}"}), 500
    


# --- Save summary input ---
@note_bp.route('/save', methods=['POST'])
@cross_origin()
def save():
    try:
        data = request.get_json()
        summary = data.get('summary')
        header = data.get('header')
        topic = data.get('topic')
        provider = data.get('provider')
        current_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
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
        note_collection.insert_one(note)
        # Return only success message
        return jsonify({"message": "Summary saved successfully!"})
    except Exception as e:
        return jsonify({"error": f"Error saving to database: {str(e)}"}), 500
    

# --- Get note by header (POST) ---
@note_bp.route('/api/note', methods=['POST'])
def get_note():
    data = request.get_json()
    header = data.get('Header')
    if not header:
        return jsonify({'error': 'Header is required'}), 400
    note = note_collection.find_one({'Header': header})
    if note:
        return jsonify(mongo_to_json(note))
    else:
        return jsonify({'error': 'Note not found'}), 404


# --- Get all note headers,Topic (for dropdown) ---
@note_bp.route('/api/headers', methods=['GET'])
def get_headers():
    topics = note_collection.distinct('Topic')
    return jsonify({'headers': topics})

@note_bp.route('/api/notes_by_topic', methods=['POST'])
@cross_origin()
def notes_by_topic():
    data = request.get_json()
    topic = data.get('Topic')
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    notes = list(note_collection.find({'Topic': topic}))
    return jsonify({'notes': mongo_to_json(notes)})



#PDF input
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# input_text from OCR
@note_bp.route('/api/notes_ocr', methods=['POST'])
@cross_origin()
def upload_and_process_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(note_bp.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # Step 1: OCR
        extracted_text = ocr_document(
            pdf_or_image_path=filepath,
            task_type="default",
            target_image_dim=1800,
            target_text_length=8000,
            page_num=1
        )

        # Step 2: Summarize with Gemini
        summary = summarize(extracted_text)

        # Step 3: Save to MongoDB
        note = {
            "original_text": extracted_text,
            "summary": summary,
            "filename": filename,
            "created_at": datetime.utcnow()
        }
        note_collection.insert_one(note)

        # Step 4: Respond to client
        return jsonify({
            "ocr_result": extracted_text,
            "summary": summary,
            "filename": filename
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


# --- Summarize text route ---
@super_note_bp.route('/api/supernote', methods=['POST'])
@cross_origin()
def make_supernote():
    try:
        data = request.get_json()
        notes = data.get('notes', [])
        if not notes or not isinstance(notes, list):
            return jsonify({'error': 'No notes provided'}), 400
        # Combine all Sum fields
        combined_sum = ' '.join([n.get('Sum', '') for n in notes])
        combined_header = ', '.join([n.get('Header', '') for n in notes])
        combined_topic = notes[0].get('Topic', '') if notes else ''
        combined_provider = ', '.join([n.get('Provider', '') for n in notes])
        # Summarize and correct with Gemini
        system_prompt = "Your job is combine and summarize the provided text in a clear and concise way, maintaining the key points."
        structure_output = "Respond in text format only, without any additional formatting or HTML tags."
        prompt = f"{system_prompt} {structure_output}'{combined_topic}': {combined_sum}"
        response = model.generate_content(prompt)
        supernote_sum = response.text
        current_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        supernote_doc = {
            "Header": combined_header,
            "Topic": combined_topic,
            "Sum": supernote_sum,
            "Provider": combined_provider,
            "DateTime": current_date,
            "LastUpdate": current_date
        }
        # Insert and get inserted_id
        result = super_note_collection.insert_one(supernote_doc)
        # Do not return ObjectId in response (not JSON serializable)
        supernote_doc["_id"] = str(result.inserted_id)
        return jsonify({"supernote": mongo_to_json(supernote_doc)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


# --- Get all supernotes route ---
@super_note_bp.route('/api/supernotes', methods=['GET'])
@cross_origin()
def get_supernotes():
    try:
        supernotes = list(super_note_collection.find({}))
        return jsonify({"supernotes": mongo_to_json(supernotes)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
def mongo_to_json(doc):
    if isinstance(doc, list):
        return [mongo_to_json(d) for d in doc]
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

# --- Delete supernote by id ---
@super_note_bp.route('/api/supernote/<id>', methods=['DELETE'])
@cross_origin()
def delete_supernote(id):
    try:
        result = super_note_collection.delete_one({'_id': ObjectId(id)})
        if result.deleted_count == 1:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Supernote not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

 
