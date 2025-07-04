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

4. **Start the application**

   **Option A: Quick Start (Recommended)**
   ```bash
   python run_server.py
   ```
   This starts the backend server. Then in a new terminal:
   ```bash
   streamlit run frontend/app.py
   ```

   **Option B: Manual Start**
   
   Start backend:
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   Start frontend (in new terminal):
   ```bash
   streamlit run frontend/app.py
   ```

5. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 Usage Guide

### Getting Started

1. **Register an Account**
   - Open http://localhost:8501
   - Click on "Register" tab
   - Fill in your details and create an account

2. **Create Your First Team**
   - Navigate to "Teams" page
   - Click "Create New Team"
   - Enter team name and description

3. **Organize with Topics**
   - Select your team
   - Go to "Topics" page
   - Create topics to organize your notes
   - Add tags for better categorization

4. **Start Taking Notes**
   - Select a topic
   - Go to "Notes" page
   - Create your first note
   - Use AI features for enhancement

### Team Management

- **Invite Members**: Use the team management interface to invite users by email
- **Role Management**: Assign roles (Owner, Admin, Member) with different permissions
- **Team Settings**: Configure team preferences and access controls

### AI Features

- **Fact Checking**: Click "Fact Check" on any note to verify information
- **AI Enhancement**: Use "AI Enhance" to improve note content
- **Content Processing**: Upload PDFs for automatic text extraction and processing
- **Quiz Generation**: Generate quizzes from your notes for learning

## 🔧 Development

### Project Structure

```
maomo/
├── backend/                 # FastAPI backend
│   ├── auth/               # Authentication modules
│   ├── models/             # Pydantic schemas
│   ├── routers/            # API route handlers
│   └── main.py            # FastAPI application
├── database/               # Database modules
│   ├── mongodb.py         # MongoDB connection
│   └── mock_db.py         # Mock database for testing
├── frontend/               # Streamlit frontend
│   ├── app.py             # Main Streamlit app
│   └── utils/             # Frontend utilities
├── .env.template          # Environment template
├── requirements.txt       # Python dependencies
└── run_server.py         # Server startup script
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
