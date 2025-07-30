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
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import tempfile
load_dotenv()

# Configure Tesseract OCR path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure Poppler path for pdf2image
os.environ['POPPLER_PATH'] = r'C:\poppler\poppler-24.08.0\Library\bin'


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
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
    stored_password = user.get('password')
    password_matches = False
    
    if stored_password:
        # Handle different password storage formats
        if isinstance(stored_password, bytes):
            # Password stored as bytes (bcrypt hash)
            try:
                password_matches = bcrypt.checkpw(password.encode('utf-8'), stored_password)
            except Exception as e:
                print(f"Bcrypt error with bytes: {e}")
        elif isinstance(stored_password, str):
            if stored_password.startswith('$2b$') or stored_password.startswith('$2a$'):
                # Password stored as bcrypt hash string
                try:
                    password_matches = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
                except Exception as e:
                    print(f"Bcrypt error with string: {e}")
            else:
                # Plain text password (legacy - should be migrated)
                password_matches = (password == stored_password)
                print(f"Warning: Plain text password found for user {username}. Consider migrating to bcrypt.")
    
    if password_matches:
        # Create JWT token
        try:
            token = jwt.encode({"sub": user['username']}, SECRET_KEY, algorithm=ALGORITHM)
            return jsonify({
                'message': 'Login successful',
                'username': user['username'],
                'access_token': token,
                'token_type': 'Bearer'
            })
        except Exception as e:
            print(f"JWT encoding error: {e}")
            return jsonify({'error': 'Authentication error'}), 500
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
        if not text:
            return jsonify({'error': 'Please enter some text to summarize.'}), 400
        
        system_prompt = "Extract and organize the key information from the provided text."
        structure_output = "Provide ONLY the summary content as bullet points using markdown format. Do not include any introductory phrases like 'This text is about', 'Here is a summary', etc. Start directly with the first bullet point. Use clear, concise language optimized for quick review."
        
        # Generate summary using Gemini
        response = model.generate_content(f"{system_prompt}{structure_output}{text}")
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
            "LastUpdate": current_date,
            "favorite": False
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
        system_prompt = "Combine and synthesize the provided texts into a consolidated knowledge summary."
        structure_output = "Provide ONLY the summary content as organized bullet points using markdown format. Do not include introductory phrases or explanations. Start directly with the content. Use clear categories and prioritize key information for review."
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
            "LastUpdate": current_date,
            "favorite": False
        }
        # Insert and get inserted_id
        result = super_note_collection.insert_one(supernote_doc)
        # Do not return ObjectId in response (not JSON serializable)
        supernote_doc["_id"] = str(result.inserted_id)
        return jsonify({"supernote": mongo_to_json(supernote_doc)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


# --- Get all notes route ---
@note_bp.route('/api/notes', methods=['GET'])
@cross_origin()
def get_notes():
    try:
        notes = list(note_collection.find({}))
        return jsonify({"notes": mongo_to_json(notes)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Get single note by ID ---
@note_bp.route('/api/note/<note_id>', methods=['GET'])
@cross_origin()
def get_note_by_id(note_id):
    try:
        note = note_collection.find_one({'_id': ObjectId(note_id)})
        if note:
            return jsonify(mongo_to_json(note))
        else:
            return jsonify({'error': 'Note not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Update note by ID ---
@note_bp.route('/api/note/<note_id>', methods=['PUT'])
@cross_origin()
def update_note(note_id):
    try:
        data = request.get_json()
        update_data = {
            'Header': data.get('Header'),
            'Sum': data.get('Sum'),
            'LastUpdate': data.get('LastUpdate')
        }
        
        result = note_collection.update_one(
            {'_id': ObjectId(note_id)}, 
            {'$set': update_data}
        )
        
        if result.matched_count > 0:
            return jsonify({'success': True, 'message': 'Note updated successfully'})
        else:
            return jsonify({'error': 'Note not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Delete note by ID ---
@note_bp.route('/api/note/<note_id>', methods=['DELETE'])
@cross_origin()
def delete_note(note_id):
    try:
        result = note_collection.delete_one({'_id': ObjectId(note_id)})
        if result.deleted_count == 1:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Note not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Get all supernotes route ---
@super_note_bp.route('/api/supernotes', methods=['GET'])
@cross_origin()
def get_supernotes():
    try:
        supernotes = list(super_note_collection.find({}))
        return jsonify({"supernotes": mongo_to_json(supernotes)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Get single supernote by ID ---
@super_note_bp.route('/api/supernote/<supernote_id>', methods=['GET'])
@cross_origin()
def get_supernote_by_id(supernote_id):
    try:
        supernote = super_note_collection.find_one({'_id': ObjectId(supernote_id)})
        if supernote:
            return jsonify(mongo_to_json(supernote))
        else:
            return jsonify({'error': 'Supernote not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Update supernote by ID ---
@super_note_bp.route('/api/supernote/<supernote_id>', methods=['PUT'])
@cross_origin()
def update_supernote(supernote_id):
    try:
        data = request.get_json()
        update_data = {
            'Header': data.get('Header'),
            'Sum': data.get('Sum'),
            'LastUpdate': data.get('LastUpdate')
        }
        
        result = super_note_collection.update_one(
            {'_id': ObjectId(supernote_id)}, 
            {'$set': update_data}
        )
        
        if result.matched_count > 0:
            return jsonify({'success': True, 'message': 'Supernote updated successfully'})
        else:
            return jsonify({'error': 'Supernote not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Create summary from file upload ---
@note_bp.route('/api/create-summary', methods=['POST'])
@cross_origin()
def create_summary():
    try:
        title = request.form.get('title')
        files = request.files.getlist('files')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
            
        # Get username from auth token
        username = get_username_from_token(request)
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
            
        if not files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        # Process uploaded files with Typhoon OCR
        full_text = ""
        
        # Import Typhoon OCR service
        try:
            from ocr.typhoon_ocr_service import typhoon_ocr_service
            use_typhoon_ocr = typhoon_ocr_service.is_available()
            if not use_typhoon_ocr:
                print("Typhoon OCR service not properly configured, falling back to Tesseract")
        except (ImportError, ValueError) as e:
            print(f"Typhoon OCR not available, falling back to Tesseract: {e}")
            use_typhoon_ocr = False
        
        for file in files:
            # Check file extension
            allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
            if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
                return jsonify({'error': 'Only PDF, PNG, JPG, JPEG files are supported.'}), 400
            
            try:
                if use_typhoon_ocr:
                    # Use Typhoon OCR for better accuracy
                    extracted_text = typhoon_ocr_service.process_uploaded_file(
                        file, file.filename, task_type="default"
                    )
                    full_text += extracted_text + "\n"
                else:
                    # Fallback to existing OCR method for PDFs only
                    if not file.filename.lower().endswith('.pdf'):
                        return jsonify({'error': 'Typhoon OCR unavailable. Only PDF files supported with fallback OCR.'}), 400
                    
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                        file.save(temp_file.name)
                        temp_path = temp_file.name
                    
                    try:
                        # Convert PDF pages to images
                        pages = convert_from_path(temp_path, 500, poppler_path=r'C:\poppler\poppler-24.08.0\Library\bin')
                        for page in pages:
                            # Perform OCR on each image
                            text = pytesseract.image_to_string(page)
                            full_text += text + "\n"
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                            
            except Exception as ocr_error:
                return jsonify({'error': f'Error processing file {file.filename}: {str(ocr_error)}'}), 500
        
        if not full_text.strip():
            return jsonify({'error': 'No text could be extracted from the PDF files'}), 400
        
        # Generate summary using the extracted text
        system_prompt = "Extract key points, important information, and relevant insights from the provided content."
        structure_output = "Provide ONLY the summary content as bullet points using markdown format. Do not include any introductory phrases. Start directly with the content organized for easy scanning and review."
        response = model.generate_content(f"{system_prompt} {structure_output} {full_text}")
        summary = response.text
        
        current_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Create document
        note = {
            "Header": title,
            "Topic": "General",
            "Sum": summary,
            "Provider": username,
            "DateTime": current_date,
            "LastUpdate": current_date,
            "favorite": False
        }
        
        # Save to MongoDB
        result = note_collection.insert_one(note)
        note['_id'] = str(result.inserted_id)
        
        return jsonify({"message": "Summary created successfully!", "summary": mongo_to_json(note)})
    except Exception as e:
        return jsonify({"error": f"Error creating summary: {str(e)}"}), 500

# --- Create summary from text input ---
@note_bp.route('/api/create-text-summary', methods=['POST'])
@cross_origin()
def create_text_summary():
    try:
        data = request.get_json()
        title = data.get('title')
        text = data.get('text')
        
        if not title or not text:
            return jsonify({'error': 'Title and text are required'}), 400
            
        # Get username from auth token
        username = get_username_from_token(request)
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Generate summary using Gemini
        system_prompt = "Extract key concepts, important details, and actionable insights from the provided text."
        structure_output = "Provide ONLY the summary content as bullet points using markdown format. Do not include any introductory text or phrases. Start directly with the first bullet point. Organize by topic or importance for easy scanning."
        response = model.generate_content(f"{system_prompt} {structure_output} {text}")
        summary = response.text
        
        current_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Create document
        note = {
            "Header": title,
            "Topic": "General",
            "Sum": summary,
            "Provider": username,
            "DateTime": current_date,
            "LastUpdate": current_date,
            "favorite": False
        }
        
        # Save to MongoDB
        result = note_collection.insert_one(note)
        note['_id'] = str(result.inserted_id)
        
        return jsonify({"message": "Summary created successfully!", "summary": mongo_to_json(note)})
    except Exception as e:
        return jsonify({"error": f"Error creating summary: {str(e)}"}), 500

# --- Toggle favorite status for note ---
@note_bp.route('/api/note/<note_id>/favorite', methods=['POST'])
@cross_origin()
def toggle_note_favorite(note_id):
    try:
        username = get_username_from_token(request)
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
            
        note = note_collection.find_one({'_id': ObjectId(note_id)})
        if not note:
            return jsonify({'error': 'Note not found'}), 404
            
        # Toggle favorite status
        current_favorite = note.get('favorite', False)
        new_favorite = not current_favorite
        
        result = note_collection.update_one(
            {'_id': ObjectId(note_id)},
            {'$set': {'favorite': new_favorite}}
        )
        
        if result.matched_count > 0:
            return jsonify({'success': True, 'favorite': new_favorite})
        else:
            return jsonify({'error': 'Failed to update favorite status'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Delete supernote by ID ---
@super_note_bp.route('/api/supernote/<supernote_id>', methods=['DELETE'])
@cross_origin()
def delete_supernote(supernote_id):
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(supernote_id):
            return jsonify({'success': False, 'error': 'Invalid supernote ID format'}), 400
            
        # Check if supernote exists before deletion
        supernote = super_note_collection.find_one({'_id': ObjectId(supernote_id)})
        if not supernote:
            return jsonify({'success': False, 'error': 'Supernote not found'}), 404
            
        # Delete the supernote
        result = super_note_collection.delete_one({'_id': ObjectId(supernote_id)})
        
        if result.deleted_count == 1:
            return jsonify({'success': True, 'message': 'Supernote deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to delete supernote'}), 500
            
    except Exception as e:
        print(f"Error deleting supernote {supernote_id}: {str(e)}")  # Log the error
        return jsonify({'success': False, 'error': f'Error deleting supernote: {str(e)}'}), 500



# --- Toggle favorite status for supernote ---
@super_note_bp.route('/api/supernote/<supernote_id>/favorite', methods=['POST'])
@cross_origin()
def toggle_supernote_favorite(supernote_id):
    try:
        username = get_username_from_token(request)
        if not username:
            return jsonify({'error': 'Authentication required'}), 401
            
        supernote = super_note_collection.find_one({'_id': ObjectId(supernote_id)})
        if not supernote:
            return jsonify({'error': 'Supernote not found'}), 404
            
        # Toggle favorite status
        current_favorite = supernote.get('favorite', False)
        new_favorite = not current_favorite
        
        result = super_note_collection.update_one(
            {'_id': ObjectId(supernote_id)},
            {'$set': {'favorite': new_favorite}}
        )
        
        if result.matched_count > 0:
            return jsonify({'success': True, 'favorite': new_favorite})
        else:
            return jsonify({'error': 'Failed to update favorite status'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper function to get username from authentication token
def get_username_from_token(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded.get('sub')
    except:
        return None

# Helper function to convert MongoDB ObjectId to string
def mongo_to_json(doc):
    if isinstance(doc, list):
        return [mongo_to_json(d) for d in doc]
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc





