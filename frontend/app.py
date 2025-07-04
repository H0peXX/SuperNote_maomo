import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
import json
from datetime import datetime

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Maomo - Collaborative Notes",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .team-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .fact-check-verified {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #28a745;
    }
    .fact-check-questionable {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #ffc107;
    }
    .fact-check-inaccurate {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #dc3545;
    }
    .collaboration-indicator {
        position: fixed;
        top: 1rem;
        right: 1rem;
        background: #28a745;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

# Authentication functions
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_team' not in st.session_state:
        st.session_state.current_team = None
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = None
    if 'current_note' not in st.session_state:
        st.session_state.current_note = None
    if 'editing_mode' not in st.session_state:
        st.session_state.editing_mode = False

def make_authenticated_request(method, endpoint, **kwargs):
    """Make an authenticated request to the backend"""
    if not st.session_state.authenticated or not st.session_state.token:
        st.error("Not authenticated. Please log in.")
        return None
    
    headers = {
        "Authorization": f"Bearer {st.session_state.token}",
        "Content-Type": "application/json"
    }
    
    if 'headers' in kwargs:
        kwargs['headers'].update(headers)
    else:
        kwargs['headers'] = headers
    
    try:
        response = requests.request(method, f"{BACKEND_URL}{endpoint}", **kwargs)
        if response.status_code == 401:
            st.session_state.authenticated = False
            st.session_state.token = None
            st.session_state.user = None
            st.error("Session expired. Please log in again.")
            st.rerun()
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

def login_page():
    """Display login/registration page"""
    st.markdown('<div class="main-header">Welcome to Maomo</div>', unsafe_allow_html=True)
    st.markdown("### Collaborative Note-Taking with AI")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/auth/login",
                        json={"email": email, "password": password}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.authenticated = True
                        
                        # Get user info
                        user_response = make_authenticated_request("GET", "/api/auth/me")
                        if user_response and user_response.status_code == 200:
                            st.session_state.user = user_response.json()
                        
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                except Exception as e:
                    st.error(f"Login error: {e}")
    
    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            full_name = st.text_input("Full Name")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")
            
            if submit:
                if password != confirm_password:
                    st.error("Passwords don't match")
                else:
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/api/auth/register",
                            json={
                                "username": username,
                                "email": email,
                                "full_name": full_name,
                                "password": password
                            }
                        )
                        if response.status_code == 201:
                            st.success("Registration successful! Please log in.")
                        else:
                            error_data = response.json()
                            st.error(f"Registration failed: {error_data.get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Registration error: {e}")

def sidebar_navigation():
    """Display sidebar navigation"""
    with st.sidebar:
        # User info
        if st.session_state.user:
            st.markdown(f"**Welcome, {st.session_state.user['full_name']}!**")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.token = None
                st.session_state.user = None
                st.session_state.current_team = None
                st.session_state.current_topic = None
                st.rerun()
        
        # Navigation menu
        selected = option_menu(
            "Navigation",
            ["Dashboard", "Teams", "Topics", "Notes", "AI Tools", "Settings"],
            icons=["house", "people", "folder", "journal-text", "robot", "gear"],
            menu_icon="cast",
            default_index=0,
        )
        
        return selected

def dashboard_page():
    """Display dashboard page with live metrics"""
    st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)
    
    # Current state indicator
    if st.session_state.current_team:
        st.success(f"📍 Current Team: **{st.session_state.current_team['name']}**")
        if st.session_state.current_topic:
            st.info(f"📁 Current Topic: **{st.session_state.current_topic['name']}**")
    else:
        st.warning("⚠️ No team selected. Please select a team to get started.")
    
    # Load and display metrics
    teams_response = make_authenticated_request("GET", "/api/teams/")
    teams_count = len(teams_response.json()) if teams_response and teams_response.status_code == 200 else 0
    
    notes_count = 0
    topics_count = 0
    if st.session_state.current_team:
        topics_response = make_authenticated_request("GET", f"/api/topics/team/{st.session_state.current_team['id']}")
        if topics_response and topics_response.status_code == 200:
            topics = topics_response.json()
            topics_count = len(topics)
            # Count notes across all topics
            for topic in topics:
                notes_response = make_authenticated_request("GET", f"/api/notes/?topic_id={topic['id']}")
                if notes_response and notes_response.status_code == 200:
                    notes_count += len(notes_response.json())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("My Teams", teams_count, "")
    
    with col2:
        st.metric("Topics", topics_count, "")
    
    with col3:
        st.metric("Notes", notes_count, "")
    
    with col4:
        st.metric("AI Processes", "∞", "Available")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Upload PDF", use_container_width=True):
            st.session_state.page = "AI Tools"
            st.rerun()
    
    with col2:
        if st.button("👥 Create Team", use_container_width=True):
            st.session_state.page = "Teams"
            st.rerun()
    
    with col3:
        if st.button("📁 Create Topic", use_container_width=True):
            if st.session_state.current_team:
                st.session_state.page = "Topics"
                st.rerun()
            else:
                st.error("Please select a team first")
    
    with col4:
        if st.button("📝 New Note", use_container_width=True):
            if st.session_state.current_topic:
                st.session_state.page = "Notes"
                st.rerun()
            else:
                st.error("Please select a topic first")
    
    # Recent activity (if we have teams)
    if teams_count > 0:
        st.subheader("Recent Activity")
        if st.session_state.current_team:
            st.write(f"🏢 **Current workspace:** {st.session_state.current_team['name']}")
            if topics_count > 0:
                st.write(f"📂 **Available topics:** {topics_count}")
            if notes_count > 0:
                st.write(f"📝 **Total notes:** {notes_count}")
        else:
            st.info("💡 **Tip:** Select a team from the Teams page to see your workspace activity.")
    else:
        st.subheader("Get Started")
        st.info("🚀 **Welcome to Maomo!** Create your first team to start collaborating on notes with AI-powered features.")

def teams_page():
    """Display teams management page"""
    st.markdown('<div class="main-header">Teams</div>', unsafe_allow_html=True)
    
    # Get user teams
    response = make_authenticated_request("GET", "/api/teams/")
    if response and response.status_code == 200:
        teams = response.json()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("My Teams")
            if teams:
                for team in teams:
                    with st.container():
                        st.markdown(f"""
                        <div class="team-card">
                            <h3>{team['name']}</h3>
                            <p>{team.get('description', 'No description')}</p>
                            <small>Members: {len(team.get('members', []))} | Created: {team['created_at'][:10]}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button(f"Select {team['name']}", key=f"select_{team['id']}"):
                                st.session_state.current_team = team
                                st.session_state.current_topic = None
                                st.success(f"Selected team: {team['name']}")
                        with col_b:
                            if st.button(f"View Topics", key=f"topics_{team['id']}"):
                                st.session_state.current_team = team
                                st.session_state.page = "Topics"
                                st.rerun()
                        with col_c:
                            if st.button(f"Settings", key=f"settings_{team['id']}"):
                                st.session_state.current_team = team
                                # Open team settings modal or section
            else:
                st.info("No teams found. Create your first team!")
        
        with col2:
            st.subheader("Create New Team")
            with st.form("create_team"):
                team_name = st.text_input("Team Name")
                team_description = st.text_area("Description")
                submit = st.form_submit_button("Create Team")
                
                if submit:
                    response = make_authenticated_request(
                        "POST", "/api/teams/",
                        json={
                            "name": team_name,
                            "description": team_description
                        }
                    )
                    if response and response.status_code == 201:
                        st.success("Team created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create team")

def topics_page():
    """Display topics management page"""
    st.markdown('<div class="main-header">Topics</div>', unsafe_allow_html=True)
    
    if not st.session_state.current_team:
        st.info("Please select a team first to view topics.")
        return
    
    st.subheader(f"Topics for {st.session_state.current_team['name']}")
    
    # Get topics for current team
    response = make_authenticated_request("GET", f"/api/topics/team/{st.session_state.current_team['id']}")
    if response and response.status_code == 200:
        topics = response.json()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Team Topics")
            if topics:
                for topic in topics:
                    with st.expander(f"📁 {topic['name']}", expanded=False):
                        st.write(f"**Description:** {topic.get('description', 'No description')}")
                        if topic.get('tags'):
                            st.write(f"**Tags:** {', '.join(topic['tags'])}")
                        st.write(f"**Created:** {topic['created_at'][:10]}")
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button(f"Select Topic", key=f"select_topic_{topic['id']}"):
                                st.session_state.current_topic = topic
                                st.success(f"Selected topic: {topic['name']}")
                        with col_b:
                            if st.button(f"View Notes", key=f"notes_{topic['id']}"):
                                st.session_state.current_topic = topic
                                st.session_state.page = "Notes"
                                st.rerun()
                        with col_c:
                            if st.button(f"Edit", key=f"edit_{topic['id']}"):
                                st.session_state.editing_topic = topic
            else:
                st.info("No topics found. Create your first topic!")
        
        with col2:
            st.subheader("Create New Topic")
            with st.form("create_topic"):
                topic_name = st.text_input("Topic Name")
                topic_description = st.text_area("Description")
                topic_tags = st.text_input("Tags (comma-separated)")
                submit = st.form_submit_button("Create Topic")
                
                if submit:
                    tags_list = [tag.strip() for tag in topic_tags.split(",") if tag.strip()]
                    response = make_authenticated_request(
                        "POST", "/api/topics/",
                        json={
                            "name": topic_name,
                            "description": topic_description,
                            "tags": tags_list,
                            "team_id": st.session_state.current_team['id']
                        }
                    )
                    if response and response.status_code == 201:
                        st.success("Topic created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create topic")
    else:
        st.error("Failed to load topics")

def notes_page():
    """Display notes page with enhanced editing capabilities"""
    st.markdown('<div class="main-header">Notes</div>', unsafe_allow_html=True)
    
    if not st.session_state.current_team:
        st.info("Please select a team first to view notes.")
        return
    
    if not st.session_state.current_topic:
        st.info("Please select a topic first to view notes.")
        return
    
    st.subheader(f"Notes for Topic: {st.session_state.current_topic['name']}")
    
    # Get notes for current topic
    response = make_authenticated_request("GET", f"/api/notes/?topic_id={st.session_state.current_topic['id']}")
    if response and response.status_code == 200:
        notes = response.json()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Topic Notes")
            if notes:
                for note in notes:
                    with st.expander(f"📝 {note['title']}", expanded=False):
                        st.markdown(note['content'])
                        st.write(f"**Status:** {note['status']}")
                        st.write(f"**Created:** {note['created_at'][:10]}")
                        
                        # Fact-checking indicators
                        if note.get('fact_checks'):
                            st.write("**Fact Checks:**")
                            for fact_check in note['fact_checks']:
                                status_class = f"fact-check-{fact_check['status']}"
                                st.markdown(f"<div class='{status_class}'>{fact_check['claim']}: {fact_check['status'].upper()}</div>", unsafe_allow_html=True)
                        
                        col_a, col_b, col_c, col_d = st.columns(4)
                        with col_a:
                            if st.button(f"Edit", key=f"edit_note_{note['id']}"):
                                st.session_state.current_note = note
                                st.session_state.editing_mode = True
                        with col_b:
                            if st.button(f"Fact Check", key=f"fact_check_{note['id']}"):
                                # Trigger AI fact-checking
                                fact_check_response = make_authenticated_request(
                                    "POST", f"/api/notes/{note['id']}/fact-checks"
                                )
                                if fact_check_response and fact_check_response.status_code == 200:
                                    st.success("Fact-checking completed!")
                                    st.rerun()
                        with col_c:
                            if st.button(f"AI Enhance", key=f"enhance_{note['id']}"):
                                # Trigger AI enhancement
                                enhance_response = make_authenticated_request(
                                    "POST", "/api/ai/enhance-note",
                                    json={
                                        "text": note['content'],
                                        "language": "English",
                                        "operation": "enhance"
                                    }
                                )
                                if enhance_response and enhance_response.status_code == 200:
                                    result = enhance_response.json()
                                    st.info("AI Enhancement Suggestion:")
                                    st.markdown(result['result'])
                        with col_d:
                            if st.button(f"Comments ({len(note.get('comments', []))})", key=f"comments_{note['id']}"):
                                st.session_state.show_comments = note['id']
            else:
                st.info("No notes found. Create your first note!")
        
        with col2:
            if st.session_state.editing_mode and st.session_state.current_note:
                st.subheader("Edit Note")
                with st.form("edit_note"):
                    note_title = st.text_input("Title", value=st.session_state.current_note['title'])
                    note_content = st.text_area("Content", value=st.session_state.current_note['content'], height=300)
                    note_status = st.selectbox("Status", ["draft", "published", "archived"], 
                                             index=["draft", "published", "archived"].index(st.session_state.current_note['status']))
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("Save Changes"):
                            response = make_authenticated_request(
                                "PUT", f"/api/notes/{st.session_state.current_note['id']}",
                                json={
                                    "title": note_title,
                                    "content": note_content,
                                    "status": note_status
                                }
                            )
                            if response and response.status_code == 200:
                                st.success("Note updated successfully!")
                                st.session_state.editing_mode = False
                                st.session_state.current_note = None
                                st.rerun()
                            else:
                                st.error("Failed to update note")
                    with col_cancel:
                        if st.form_submit_button("Cancel"):
                            st.session_state.editing_mode = False
                            st.session_state.current_note = None
                            st.rerun()
            else:
                st.subheader("Create New Note")
                with st.form("create_note"):
                    note_title = st.text_input("Note Title")
                    note_content = st.text_area("Content", height=300)
                    note_status = st.selectbox("Status", ["draft", "published", "archived"])
                    submit = st.form_submit_button("Create Note")
                    
                    if submit:
                        response = make_authenticated_request(
                            "POST", "/api/notes/",
                            json={
                                "title": note_title,
                                "content": note_content,
                                "topic_id": st.session_state.current_topic['id'],
                                "status": note_status
                            }
                        )
                        if response and response.status_code == 201:
                            st.success("Note created successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to create note")
    else:
        st.error("Failed to load notes")

def ai_tools_page():
    """Display AI tools page - enhanced version of original app"""
    st.markdown('<div class="main-header">AI Tools</div>', unsafe_allow_html=True)
    
    # PDF Upload section
    uploaded_file = st.file_uploader("📤 Upload a PDF file", type=["pdf"])
    
    # Language selection
    col1, col2 = st.columns(2)
    with col1:
        language_choice = st.selectbox("🌐 Output Language", 
            ["English", "Thai", "Japanese", "Chinese", "Korean", "Spanish", "Other..."]
        )
        
    with col2:
        custom_language = ""
        if language_choice == "Other...":
            custom_language = st.text_input("Enter your desired language")
            language = custom_language.strip() if custom_language.strip() else "English"
        else:
            language = language_choice
    
    # Processing options
    st.subheader("Processing Options")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        format_text = st.checkbox("Format Text", value=True)
    with col2:
        summarize = st.checkbox("Summarize", value=True)
    with col3:
        fact_check = st.checkbox("Fact Check", value=False)
    with col4:
        generate_quiz = st.checkbox("Generate Quiz", value=False)
    
    if uploaded_file:
        if st.button("🚀 Process PDF"):
            # Process with backend API
            with st.spinner("Processing PDF..."):
                files = {"file": uploaded_file.getvalue()}
                data = {
                    "language": language,
                    "operation": "format"
                }
                
                response = make_authenticated_request(
                    "POST", "/api/ai/process-pdf",
                    files=files,
                    data=data
                )
                
                if response and response.status_code == 200:
                    result = response.json()
                    
                    st.subheader("✨ Processed Results")
                    
                    if format_text:
                        st.markdown("### 📄 Formatted Text")
                        st.markdown(result["result"])
                        st.download_button(
                            "💾 Download Formatted Text",
                            result["result"],
                            file_name="formatted_text.md"
                        )
                    
                    # Additional processing would go here
                else:
                    st.error("Failed to process PDF")

def settings_page():
    """Display settings page"""
    st.markdown('<div class="main-header">Settings</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Profile", "Preferences", "API Keys"])
    
    with tab1:
        st.subheader("Profile Settings")
        if st.session_state.user:
            with st.form("profile_form"):
                username = st.text_input("Username", value=st.session_state.user['username'])
                email = st.text_input("Email", value=st.session_state.user['email'])
                full_name = st.text_input("Full Name", value=st.session_state.user['full_name'])
                
                if st.form_submit_button("Update Profile"):
                    response = make_authenticated_request(
                        "PUT", "/api/users/me",
                        json={
                            "username": username,
                            "email": email,
                            "full_name": full_name
                        }
                    )
                    if response and response.status_code == 200:
                        st.success("Profile updated successfully!")
                        st.session_state.user = response.json()
                    else:
                        st.error("Failed to update profile")
    
    with tab2:
        st.subheader("Preferences")
        st.selectbox("Default Language", ["English", "Thai", "Japanese", "Chinese"])
        st.checkbox("Enable Real-time Notifications")
        st.checkbox("Auto-save Notes")
        
    with tab3:
        st.subheader("API Configuration")
        st.info("API key management will be available here")

def main():
    """Main application function"""
    init_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        # Sidebar navigation
        page = sidebar_navigation()
        
        # Store current page in session state
        st.session_state.page = page
        
        # Route to appropriate page
        if page == "Dashboard":
            dashboard_page()
        elif page == "Teams":
            teams_page()
        elif page == "Topics":
            topics_page()
        elif page == "Notes":
            notes_page()
        elif page == "AI Tools":
            ai_tools_page()
        elif page == "Settings":
            settings_page()

if __name__ == "__main__":
    main()
