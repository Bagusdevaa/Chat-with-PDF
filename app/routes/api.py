from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user, login_required
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import time
import uuid
import datetime
from app.models.pdf_processor import PDFProcessor
from app.models.documents import Document
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app import db, response
from werkzeug.utils import secure_filename
from datetime import datetime, timezone

api = Blueprint('api', __name__)

# Store user sessions in memory (in production, should use a database)
USER_SESSIONS = {}

# Utility functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def get_user_from_jwt():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

@api.route('/ping', methods=['GET'])
def ping():
    """Simple test endpoint"""
    return jsonify({"status": "success", "message": "API is running"})

@api.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload (legacy endpoint)"""
    print("Upload request received")
    
    if 'pdf_file' not in request.files:
        print("No file part in request")
        return jsonify({"error": "No file part"}), 400
    
    pdf_file = request.files['pdf_file']
    print(f"File received: {pdf_file.filename}")
    
    if pdf_file.filename == '':
        print("Empty filename")
        return jsonify({"error": "No file selected"}), 400
    
    if not pdf_file.filename.endswith('.pdf'):
        print("Not a PDF file")
        return jsonify({"error": "File must be a PDF"}), 400

@api.route('/documents/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a PDF document with authentication"""
    try:
        user = get_user_from_jwt()
        
        if 'file' not in request.files:
            return response.error_response('No file part', 400)
            
        file = request.files['file']
        
        if file.filename == '':
            return response.error_response('No selected file', 400)
            
        if not allowed_file(file.filename):
            return response.error_response('Only PDF files are allowed', 400)
        
        # Create a unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = f"{str(uuid.uuid4())}.pdf"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the file
        file.save(file_path)
        
        # Create a document record in the database
        document = Document(
            user_id=user.id,
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            upload_date=datetime.now(timezone.utc),
            session_id=str(uuid.uuid4())
        )
        
        db.session.add(document)
        db.session.commit()
        
        return response.success_response({
            'document_id': document.id,
            'filename': document.original_filename,
            'upload_date': document.upload_date.isoformat(),
            'session_id': document.session_id
        }, 'Document uploaded successfully', 201)
        
    except Exception as e:
        return response.error_response(str(e))

@api.route('/documents', methods=['GET'])
@jwt_required()
def get_documents():
    """Get all documents for the current user"""
    try:
        user = get_user_from_jwt()
        
        documents = Document.query.filter_by(user_id=user.id).all()
        
        result = []
        for doc in documents:
            result.append({
                'id': doc.id,
                'filename': doc.original_filename,
                'upload_date': doc.upload_date.isoformat(),
                'processed': doc.processed,
                'page_count': doc.page_count
            })
        
        return response.success_response(result, 'Documents retrieved successfully', 200)
        
    except Exception as e:
        return response.error_response(str(e))

@api.route('/documents/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get a single document by ID"""
    try:
        user = get_user_from_jwt()
        
        document = Document.query.filter_by(id=document_id, user_id=user.id).first()
        
        if not document:
            return response.error_response('Document not found', 404)
        
        return response.success_response({
            'id': document.id,
            'filename': document.original_filename,
            'upload_date': document.upload_date.isoformat(),
            'processed': document.processed,
            'page_count': document.page_count
        }, 'Document retrieved successfully', 200)
        
    except Exception as e:
        return response.error_response(str(e))
    
    try:
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        print(f"Generated session ID: {session_id}")
        
        # Save PDF file for viewing first
        uploads_dir = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        pdf_path = os.path.join(uploads_dir, f"{session_id}.pdf")
        pdf_file.save(pdf_path)
        print(f"PDF saved to {pdf_path}")
        
        # Now reopen the file for processing
        try:
            with open(pdf_path, 'rb') as saved_pdf:
                raw_text = PDFProcessor.get_pdf_text(saved_pdf)
                text_chunks = PDFProcessor.get_text_chunks(raw_text)
                vectorstore = PDFProcessor.get_vectorstore(text_chunks)
                conversation_chain = PDFProcessor.get_conversation_chain(vectorstore)
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500
        
        # Store session data
        USER_SESSIONS[session_id] = {
            'conversation': conversation_chain,
            'chat_history': [],
            'pdf_name': pdf_file.filename,
            'upload_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Return the response with proper URL for the PDF
        return jsonify({
            "success": True, 
            "session_id": session_id,
            "pdf_name": pdf_file.filename,
            "pdf_path": f"/static/uploads/{session_id}.pdf"  # Adjusted path for Flask's static folder
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/documents/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    """Delete a document"""
    try:
        user = get_user_from_jwt()
        
        document = Document.query.filter_by(id=document_id, user_id=user.id).first()
        
        if not document:
            return response.error_response('Document not found', 404)
        
        # Delete the file from storage
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database (this will cascade delete conversations and messages)
        db.session.delete(document)
        db.session.commit()
        
        return response.success_response({}, 'Document deleted successfully', 200)
        
    except Exception as e:
        return response.error_response(str(e))
        
# Conversation routes
@api.route('/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    """Create a new conversation for a document"""
    try:
        user = get_user_from_jwt()
        data = request.json
        
        if not data or 'document_id' not in data:
            return response.error_response('Document ID is required', 400)
        
        document_id = data['document_id']
        title = data.get('title', 'New Conversation')
        
        # Verify document exists and belongs to user
        document = Document.query.filter_by(id=document_id, user_id=user.id).first()
        
        if not document:
            return response.error_response('Document not found', 404)
        
        # Create conversation
        conversation = Conversation(
            user_id=user.id,
            document_id=document_id,
            title=title,
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        return response.success_response({
            'id': conversation.id,
            'title': conversation.title,
            'created_at': conversation.created_at.isoformat()
        }, 'Conversation created successfully', 201)
        
    except Exception as e:
        return response.error_response(str(e))

@api.route('/conversations/<int:document_id>', methods=['GET'])
@jwt_required()
def get_conversations(document_id):
    """Get all conversations for a document"""
    try:
        user = get_user_from_jwt()
        
        document = Document.query.filter_by(id=document_id, user_id=user.id).first()
        
        if not document:
            return response.error_response('Document not found', 404)
        
        conversations = Conversation.query.filter_by(document_id=document_id).all()
        
        result = []
        for conv in conversations:
            result.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat()
            })
        
        return response.success_response(result, 'Conversations retrieved successfully', 200)
        
    except Exception as e:
        return response.error_response(str(e))

@api.route('/conversation/<int:conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_conversation_messages(conversation_id):
    """Get all messages in a conversation"""
    try:
        user = get_user_from_jwt()
        
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=user.id).first()
        
        if not conversation:
            return response.error_response('Conversation not found', 404)
        
        messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
        
        result = []
        for msg in messages:
            result.append({
                'id': msg.id,
                'content': msg.content,
                'role': msg.role,
                'created_at': msg.created_at.isoformat()
            })
        
        return response.success_response(result, 'Messages retrieved successfully', 200)
        
    except Exception as e:
        return response.error_response(str(e))

@api.route('/conversation/<int:conversation_id>/message', methods=['POST'])
@jwt_required()
def create_message(conversation_id):
    """Add a message to a conversation"""
    try:
        user = get_user_from_jwt()
        data = request.json
        
        if not data or 'content' not in data or 'role' not in data:
            return response.error_response('Content and role are required', 400)
        
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=user.id).first()
        
        if not conversation:
            return response.error_response('Conversation not found', 404)
        
        # Create message
        message = Message(
            conversation_id=conversation_id,
            content=data['content'],
            role=data['role'],
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return response.success_response({
            'id': message.id,
            'content': message.content,
            'role': message.role,
            'created_at': message.created_at.isoformat()
        }, 'Message created successfully', 201)
        
    except Exception as e:
        return response.error_response(str(e))

@api.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages (legacy endpoint)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    session_id = data.get('session_id')
    user_question = data.get('question')
    
    if not session_id or not user_question:
        return jsonify({"error": "Session ID and question are required"}), 400
    
    if session_id not in USER_SESSIONS:
        return jsonify({"error": "Session not found or expired"}), 404
    
    try:
        # Start timer to measure response time
        start_time = time.time()
        
        # Get response from conversation chain
        print(f"Processing question for session {session_id}: {user_question[:50]}...")
        response = USER_SESSIONS[session_id]['conversation']({'question': user_question})
        chat_history = response.get('chat_history', [])
        
        # Update session chat history
        USER_SESSIONS[session_id]['chat_history'] = chat_history
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Get the bot's response (last message in chat history)
        bot_response = chat_history[-1].content
        
        return jsonify({
            "response": bot_response,
            "response_time": f"{response_time:.2f}"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
