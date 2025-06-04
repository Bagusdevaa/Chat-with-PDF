# PDFChat - Intelligent PDF Document Assistant

> A modern web application for interactive conversations with PDF documents using AI

## Introduction

PDFChat is a sophisticated Flask web application that transforms how you interact with PDF documents. Built with a modern tech stack, it allows you to upload PDF files and engage in natural language conversations about their content. The application leverages advanced AI models to understand your questions and provide accurate, contextual responses based on the document's content.

**Key Highlights:**
- 🤖 AI-powered document understanding
- 💬 Real-time chat interface with conversation history
- 📄 Multi-document support with organized management
- 👤 User authentication and profile management
- 🎨 Modern, responsive UI with Tailwind CSS
- 🔒 Secure file handling and user data protection

## How It Works

![PDFChat App Diagram](./docs/PDF-LangChain.jpg)

The application follows these steps to respond to your questions:

1. **PDF Loading:** The application reads PDF documents and extracts their text content.
2. **Text Chunking:** The extracted text is divided into smaller chunks that can be effectively processed using RecursiveCharacterTextSplitter.
3. **Vectorization:** The application uses language models to generate vector representations (embeddings) of the text chunks.
4. **Similarity Matching:** When you ask a question, the application compares it with the text chunks and identifies the most semantically similar ones.
5. **Response Generation:** The selected chunks are passed to the language model, which generates a response based on the relevant content from the PDF.

## Key Features

- **🔐 User Authentication:** Secure registration, login, and profile management
- **📚 Document Management:** Upload, organize, and manage multiple PDF documents
- **💬 Intelligent Chat:** Contextual conversations with PDF content using AI
- **📱 Responsive Design:** Modern UI that works seamlessly across all devices
- **🔄 Conversation History:** Persistent chat sessions with document context
- **👤 User Profiles:** Personal dashboard with account settings and preferences
- **🔒 Secure Storage:** Safe handling of user documents and data
- **⚡ Real-time Responses:** Fast AI-powered answers to your questions
- **📤 Export Features:** Download documents and chat transcripts
- **🎨 Modern Interface:** Clean design built with Tailwind CSS

## Technologies Used

### Backend
- **Flask:** Modern Python web framework with Blueprint organization
- **SQLAlchemy:** ORM for database management with SQLite
- **Flask-JWT-Extended:** JWT token-based authentication
- **LangChain:** Advanced framework for LLM applications
- **FAISS:** High-performance vector similarity search
- **OpenAI API:** GPT models for intelligent document understanding
- **Flask-Migrate:** Database migration management

### Frontend
- **Tailwind CSS:** Utility-first CSS framework for modern styling
- **Vanilla JavaScript:** Clean, modern ES6+ for dynamic interactions
- **Responsive Design:** Mobile-first approach with adaptive layouts
- **Component Architecture:** Modular JavaScript for maintainability

### Infrastructure
- **SQLite:** Lightweight database for development and small deployments
- **File Storage:** Secure local file handling with organized uploads
- **Environment Configuration:** Flexible config management for different environments

**Note:** When using the OpenAI API, ensure that you have configured your API key correctly in the `.env` file.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- OpenAI API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Bagusdevaa/Chat-with-PDF.git
   cd PDFChat
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv pdfchat
   pdfchat\Scripts\activate

   # macOS/Linux
   python3 -m venv pdfchat
   source pdfchat/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration:**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=sqlite:///pdfchat.db
   FLASK_ENV=development
   ```

5. **Initialize the database:**
   ```bash
   flask db upgrade
   ```

6. **Build CSS (if modifying styles):**
   ```bash
   npm install
   npm run build-css
   ```

### Running the Application

**Option 1: Using Python directly**
```bash
python server.py
```

**Option 2: Using Flask CLI**
```bash
flask run
```

**Option 3: Using the batch file (Windows)**
```bash
start_pdfchat.bat
```

The application will be available at `http://localhost:5000`

### First Time Setup

1. **Register an account** at `/register`
2. **Login** with your credentials
3. **Upload a PDF document** from the documents page
4. **Start chatting** with your document!

## Usage Guide

### Getting Started
1. **Create Account:** Register with your email and create a secure password
2. **Upload Documents:** Use the document management interface to upload PDF files
3. **Start Conversations:** Click on any document to begin an AI-powered conversation
4. **Ask Questions:** Type natural language questions about your document content
5. **Manage Profile:** Update your account settings and preferences

### Features Overview
- **Document Library:** Organized view of all your uploaded PDFs
- **Chat Interface:** Intuitive messaging system with AI responses
- **Profile Management:** Update personal information and account settings
- **Conversation History:** Access previous chats and continue where you left off
- **Responsive Design:** Works seamlessly on desktop, tablet, and mobile devices

## Project Structure

```
PDFChat/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory and configuration
│   ├── response.py              # Standardized API response utilities
│   ├── controller/              # Business logic controllers
│   │   └── usercontroller.py    # User management logic
│   ├── models/                  # Database models and data processing
│   │   ├── __init__.py
│   │   ├── user.py              # User authentication model
│   │   ├── documents.py         # Document management model
│   │   ├── conversation.py      # Chat conversation model
│   │   ├── message.py           # Chat message model
│   │   └── pdf_processor.py     # PDF processing and AI integration
│   ├── routes/                  # URL route handlers
│   │   ├── __init__.py
│   │   ├── main.py              # Main page routes
│   │   ├── auth.py              # Authentication routes
│   │   └── api.py               # REST API endpoints
│   ├── static/                  # Static assets
│   │   ├── css/                 # Tailwind CSS files
│   │   ├── js/                  # Frontend JavaScript modules
│   │   ├── img/                 # Images and graphics
│   │   └── uploads/             # User uploaded files
│   └── templates/               # Jinja2 HTML templates
│       ├── landing.html         # Landing page
│       ├── login.html           # Login page
│       ├── signup.html          # Registration page
│       ├── documents.html       # Document management
│       ├── conversation.html    # Chat interface
│       ├── profile.html         # User profile
│       └── *.html               # Other templates
├── migrations/                   # Database migration files
├── docs/                        # Documentation and diagrams
├── config.py                    # Application configuration
├── server.py                    # Application entry point
├── requirements.txt             # Python dependencies
├── package.json                 # Node.js dependencies for CSS
├── tailwind.config.js           # Tailwind CSS configuration
├── start_pdfchat.bat           # Windows batch startup script
└── README.md                   # Project documentation
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `PUT /api/auth/change-password` - Change password

### Documents
- `GET /api/documents` - List user documents
- `POST /api/documents/upload` - Upload new document
- `GET /api/documents/{id}` - Get document details
- `DELETE /api/documents/{id}` - Delete document

### Conversations
- `GET /api/conversations/{document_id}` - Get document conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversation/{id}/messages` - Get conversation messages
- `POST /api/conversation/{id}/message` - Send message

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a Pull Request

### Building CSS
If you modify Tailwind styles:
```bash
npm run build-css
# or for development with watch mode
npm run watch-css
```

### Database Migrations
When you modify models:
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## Security Considerations

- **File Validation:** Only PDF files are accepted with proper validation
- **User Authentication:** JWT token-based secure authentication
- **Data Privacy:** User documents are stored securely and isolated
- **API Security:** Rate limiting and input validation on all endpoints
- **Environment Variables:** Sensitive data stored in environment variables

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the GPT models
- LangChain community for the excellent framework
- Flask and Python ecosystem contributors
- Tailwind CSS for the utility-first CSS framework

---

**Note:** This application requires an OpenAI API key for AI functionality. Make sure to obtain one from [OpenAI's website](https://openai.com/api/) and configure it properly in your environment variables.
