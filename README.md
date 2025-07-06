# Maomo - Collaborative Note-Taking Platform

🚀 **A modern collaborative note-taking platform with AI-powered features**

Maomo is a full-stack application that enables teams to collaborate on notes with real-time editing, AI-powered fact-checking, and intelligent content processing.

## ✨ Features

### 🤝 **Team Collaboration**
- Create and manage teams with role-based permissions
- Invite members via email
- Organize content with topics and tags
- Real-time collaborative note editing

### 🤖 **AI-Powered Features**
- Intelligent text formatting and cleanup
- Automatic summarization
- AI fact-checking with visual indicators
- Quiz generation from content
- Content enhancement suggestions

### 📝 **Advanced Note Management**
- Rich text editing with markdown support
- Version history and change tracking
- Comments and discussions
- Status management (draft, published, archived)
- Search and filtering capabilities

### 🔐 **Security & Authentication**
- JWT-based authentication
- Role-based access control
- Secure API endpoints
- Session management

## 🏗️ Architecture

- **Backend**: FastAPI (Python) with async/await patterns
- **Frontend**: Streamlit with modern UI components
- **Database**: MongoDB with fallback to mock database for testing
- **AI Integration**: Google Gemini API for content processing
- **Authentication**: JWT tokens with bcrypt password hashing

## 📖 Project Documentation

This project's documentation is available in two formats:

### 1. Markdown (this file)
You can view this README.md file in several ways:
- **VS Code**: `code README.md`
- **Notepad**: `notepad README.md`
- **Web Browser with GitHub Preview**:
  - Install a Markdown Viewer extension
  - Or view on GitHub's website

### 2. HTML Documentation
For a more interactive experience with better formatting:

#### From Repository Root:
```bash
# Using Python's built-in server
python -m http.server 8000
```
Then open in browser: `http://localhost:8000/docs/project_documentation.html`

#### From Deployed Version:
Access the documentation at our team's documentation site:
- Development: `https://dev-docs.maomo.com`
- Staging: `https://staging-docs.maomo.com`
- Production: `https://docs.maomo.com`

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- (Optional) MongoDB for production use

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/maomo.git
   cd maomo
   ```

2. **Install dependencies**
   ```bash
   pip install fastapi uvicorn pymongo motor python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv email-validator websockets loguru streamlit streamlit-option-menu requests google-generativeai
   ```

3. **Set up environment variables**
   ```bash
   cp .env.template .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   # Database Configuration
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=maomo_db
   
   # JWT Configuration
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # AI Configuration (Optional)
   GEMINI_API_KEY=your-gemini-api-key-here
   
   # Frontend Configuration
   BACKEND_URL=http://localhost:8000
   FRONTEND_URL=http://localhost:8501
   ```

## 🚀 How to Run the Application for Testing

You need to start both the backend server and the frontend application separately. Please follow these steps:

### 1. Start the Backend Server

This server runs the FastAPI backend with MongoDB support or mock database fallback.

- From the project root, run:

```bash
python run_server.py
```

This script will:

- Load environment variables from `.env`
- Start FastAPI with Uvicorn on http://localhost:8000
- Use MongoDB if available; otherwise, fallback on the mock database for testing

**Important:** If you prefer manual start:

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

### 2. Start the Frontend Application

The current functional frontend uses Streamlit.

- Run:

```bash
streamlit run frontend/app.py
```

This will start the frontend at http://localhost:8501, connecting to the backend at http://localhost:8000 by default (configured via `.env`).

---

### 3. Test the Application

- Open http://localhost:8501 in your browser.
- Register a new user account.
- Create teams and topics.
- Start taking collaborative notes.
- Use AI features if configured.

---

If you want to try the new modern frontend (in development under `frontend-modern`), it will have separate instructions once completed.

---

### 4. Access Points
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 Usage Guide

### Understanding the Dashboard

1. **Stats Overview**
   - **Total Notes**: Shows all notes you have access to across teams
   - **Active Teams**: Number of teams you're part of
   - **Fact Checks**: Total fact checks performed across all notes
   - **AI Enhancements**: Count of AI-enhanced content versions

2. **Recent Activity**
   - Latest modified notes with timestamps
   - Recent team changes and updates
   - Pending fact checks needing review
   - New comments on your notes
   - AI enhancement suggestions

3. **Team Overview**
   - Member count and roles
   - Activity metrics per team
   - Collaboration statistics
   - Recent changes by team members

4. **Quick Actions**
   - Create new note
   - Start fact check process
   - Upload PDF for processing
   - Manage team settings
   - Access AI tools

### Getting Started

1. **Register an Account**
   - Access the login page
   - Click "Sign Up" tab
   - Enter your details
   - Verify your email (if enabled)

2. **Create or Join a Team**
   - Go to Teams section
   - Create new team OR
   - Accept team invitation
   - Set up team preferences

3. **Organize Content**
   - Create topics for organization
   - Add descriptive tags
   - Set up workspaces
   - Configure access permissions

4. **Start Collaborating**
   - Create new notes
   - Invite team members
   - Use AI enhancements
   - Monitor fact checks

### Team Management

- **Invite Members**: Use the team management interface to invite users by email
- **Role Management**: Assign roles (Owner, Admin, Member) with different permissions
- **Team Settings**: Configure team preferences and access controls

### AI Features

- **Fact Checking**: Click "Fact Check" on any note to verify information
- **AI Enhancement**: Use "AI Enhance" to improve note content
- **Content Processing**: Upload PDFs for automatic text extraction and processing
- **Quiz Generation**: Generate quizzes from your notes for learning

## 🔄 Features Status

### Currently Missing Features

1. **Chatbot Integration**
   - AI-powered chat assistance
   - Context-aware responses
   - Team-specific knowledge base
   - Command execution via chat

2. **Mobile Support**
   - Native mobile apps
   - Responsive design improvements
   - Offline capabilities
   - Push notifications

3. **Advanced Collaboration**
   - Real-time cursor tracking
   - Presence indicators
   - Voice/video chat
   - Screen sharing

4. **Enhanced File Support**
   - Multiple file types beyond PDF
   - File version control
   - Media file processing
   - Cloud storage integration

5. **Analytics & Reporting**
   - Team activity reports
   - Usage statistics
   - AI usage metrics
   - Performance analytics

### Planned Features

1. **Smart Assistant**
   - AI-powered writing assistance
   - Content recommendations
   - Automated tagging
   - Smart search suggestions

2. **Integration Ecosystem**
   - Calendar integration
   - Task management
   - Third-party apps
   - API marketplace

3. **Advanced Security**
   - End-to-end encryption
   - Two-factor authentication
   - SSO integration
   - Audit logging

4. **Enhanced AI Features**
   - Custom AI models
   - Training on team data
   - Multi-language support
   - Advanced analytics

5. **Team Collaboration**
   - Project management
   - Timeline views
   - Kanban boards
   - Resource tracking

## 🔧 Development

### Project Structure

```
maomo/
├── backend/                    # FastAPI backend
│   ├── auth/                  # Authentication modules
│   ├── models/                # Pydantic schemas
│   ├── routers/               # API route handlers
│   └── main.py               # FastAPI application
├── database/                  # Database modules
│   ├── mongodb.py            # MongoDB connection
│   └── mock_db.py            # Mock database for testing
├── frontend-modern/           # Modern frontend (Active)
│   ├── css/                  # Stylesheets
│   │   ├── styles.css       # Base styles
│   │   ├── components.css   # Component styles
│   │   └── animations.css   # Animations
│   ├── js/                   # JavaScript modules
│   │   ├── pages/           # Page components
│   │   ├── components/      # Reusable components
│   │   ├── utils/           # Helper functions
│   │   ├── api.js           # API client
│   │   └── app.js           # Main application
│   └── index.html           # Main HTML file
├── frontend/                  # Legacy Streamlit frontend
│   ├── app.py                # Streamlit app
│   └── utils/                # Frontend utilities
├── tests/                     # Test suites
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── .env.template             # Environment template
├── requirements.txt          # Python dependencies
└── run_server.py            # Server startup script
```

### API Documentation

The FastAPI backend automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Database

The application supports both MongoDB and a mock database:
- **MongoDB**: For production use with full persistence
- **Mock Database**: Automatic fallback for testing without MongoDB

### Testing

Run the test script to verify everything works:
```bash
python test_backend.py
```

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure you're running from the project root directory
   - Check that all dependencies are installed
   - Try using `python run_server.py` instead of manual startup

2. **Database connection issues**
   - The app automatically falls back to mock database if MongoDB is unavailable
   - For production, ensure MongoDB is running on the configured URL

3. **AI features not working**
   - Ensure `GEMINI_API_KEY` is set in your `.env` file
   - Some AI features work in demo mode without an API key

4. **Port conflicts**
   - Backend runs on port 8000, frontend on port 8501
   - Change ports in configuration if needed

### Getting Help

- Check the API documentation at http://localhost:8000/docs
- Review the application logs for error messages
- Ensure all environment variables are properly set

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Streamlit for the rapid frontend development
- Google Gemini for AI capabilities
- MongoDB for robust data storage

---

**Built with ❤️ for collaborative knowledge sharing**
