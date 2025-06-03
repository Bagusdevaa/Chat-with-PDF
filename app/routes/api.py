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
from app.controller import usercontroller
from werkzeug.utils import secure_filename
from datetime import datetime, timezone

api = Blueprint('api', __name__)

# Store user sessions in memory (in production, should use a database)
USER_SESSIONS = {}

# ============ AUTH API ENDPOINTS ============
@api.route('/auth/register', methods=['POST'])
def api_auth_register():
    """API endpoint for user registration"""
    return usercontroller.register()

@api.route('/auth/signup', methods=['POST'])
def api_auth_signup():
    """API endpoint for user signup (alias for register)"""
    return usercontroller.register()

@api.route('/auth/login', methods=['POST'])
def api_auth_login():
    """API endpoint for user login"""
    return usercontroller.login()

@api.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile information"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return response.error_response('User not found', 404)
        
        # Calculate user stats
        documents_count = Document.query.filter_by(user_id=user.id).count()
        
        # Calculate storage used (sum of all document file sizes)
        total_size = db.session.query(db.func.sum(Document.file_size)).filter_by(user_id=user.id).scalar() or 0
        storage_used = f"{total_size / (1024 * 1024):.1f} MB"
        
        return response.success_response({
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'avatar': None,  # Implement avatar functionality later
                'created_at': user.created_at.isoformat(),
                'documents_count': documents_count,
                'storage_used': storage_used
            }
        }, 'Profile retrieved successfully', 200)
        
    except Exception as e:
        return response.error_response(str(e))

@api.route('/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile information"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return response.error_response('User not found', 404)
        
        data = request.json
        
        if not data:
            return response.error_response('No data provided', 400)
        
        # Update user fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter(User.email == data['email'], User.id != user.id).first()
            if existing_user:
                return response.error_response('Email is already taken', 400)
            user.email = data['email']
        
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return response.success_response({}, 'Profile updated successfully', 200)
        
    except Exception as e:
        return response.error_response(str(e))

@api.route('/auth/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return response.error_response('User not found', 404)
        
        data = request.json
        
        if not data or 'current_password' not in data or 'new_password' not in data:
            return response.error_response('Current password and new password are required', 400)
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return response.error_response('Current password is incorrect', 400)
        
        # Set new password
        user.set_password(data['new_password'])
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return response.success_response({}, 'Password updated successfully', 200)
        
    except Exception as e:
        return response.error_response(str(e))

# ============ HEALTH CHECK ============
@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return response.success_response({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }, 'API is running', 200)

@api.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint"""
    return response.success_response('', 'API is running', 200)

# Utility functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def get_user_from_jwt():
    """Helper function to get user from JWT token"""
    try:
        user_identity = get_jwt_identity()
        if user_identity is None:
            return None
        
        # Convert back to integer since we store user ID as string in JWT
        user_id = int(user_identity)
        return User.query.get(user_id)
    except (ValueError, TypeError):
        return None

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
          # Process the PDF for AI conversation
        processed_successfully = False
        try:
            # Process PDF content for AI conversation
            print(f"Processing PDF for AI: {original_filename}")
            with open(file_path, 'rb') as pdf_file:
                raw_text = PDFProcessor.get_pdf_text(pdf_file)
                text_chunks = PDFProcessor.get_text_chunks(raw_text)
                vectorstore = PDFProcessor.get_vectorstore(text_chunks)
                conversation_chain = PDFProcessor.get_conversation_chain(vectorstore)
            
            # Generate session ID for conversation
            session_id = str(uuid.uuid4())
            
            # Store session data for AI conversations
            USER_SESSIONS[session_id] = {
                'conversation': conversation_chain,
                'chat_history': [],
                'pdf_name': original_filename,
                'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            processed_successfully = True
            print(f"PDF processed successfully. Session ID: {session_id}")
            
        except Exception as e:
            print(f"Error processing PDF for AI: {str(e)}")
            # Continue without AI processing - document will still be uploaded
            session_id = str(uuid.uuid4())
        
        # Create a document record in the database
        document = Document(
            user_id=user.id,
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            upload_date=datetime.now(timezone.utc),
            session_id=session_id,
            processed=processed_successfully  # Set processed status based on AI processing success
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
    """Delete a document and all associated conversations and messages"""
    try:
        user = get_user_from_jwt()
        
        document = Document.query.filter_by(id=document_id, user_id=user.id).first()
        
        if not document:
            return response.error_response('Document not found', 404)
        
        # Delete all conversations and their messages for this document
        conversations = Conversation.query.filter_by(document_id=document_id, user_id=user.id).all()
        
        for conversation in conversations:
            # Delete all messages in this conversation first
            Message.query.filter_by(conversation_id=conversation.id).delete()
            # Delete the conversation
            db.session.delete(conversation)
        
        # Delete the file from storage
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete the document from database
        db.session.delete(document)
        db.session.commit()
        
        return response.success_response({}, 'Document deleted successfully', 200)
        
    except Exception as e:
        db.session.rollback()
        return response.error_response(str(e))
        
# Conversation routes
@api.route('/conversations', methods=['GET'])
@jwt_required()
def get_all_conversations():
    """Get all conversations for the current user"""
    try:
        user = get_user_from_jwt()
        
        # Get all conversations for the user
        conversations = Conversation.query.filter_by(user_id=user.id).order_by(Conversation.created_at.desc()).all()
        
        result = []
        for conv in conversations:
            # Get document info
            document = Document.query.get(conv.document_id)
            
            result.append({
                'id': conv.id,
                'title': conv.title,
                'document_id': conv.document_id,
                'document_name': document.original_filename if document else 'Unknown',
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat() if conv.updated_at else conv.created_at.isoformat()
            })
        
        return response.success_response(result, 'Conversations retrieved successfully', 200)
        
    except Exception as e:
        return response.error_response(str(e))

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
            # Clean content on-the-fly for AI responses (to handle legacy raw chunks)
            content = msg.content
            if msg.role == 'assistant':
                content = PDFProcessor.clean_chunk_text(content)
            
            result.append({
                'id': msg.id,
                'content': content,
                'role': msg.role,
                'created_at': msg.created_at.isoformat()
            })
        
        return response.success_response(result, 'Messages retrieved successfully', 200)
        
    except Exception as e:
        return response.error_response(str(e))

# Messages routes
@api.route('/messages', methods=['POST'])
@jwt_required()
def create_message_simple():
    """Create a message (simplified endpoint)"""
    try:
        user = get_user_from_jwt()
        data = request.json
        
        if not data or 'conversation_id' not in data or 'content' not in data or 'role' not in data:
            return response.error_response('Conversation ID, content, and role are required', 400)
        
        conversation_id = data['conversation_id']
          # Verify the conversation belongs to the user
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=user.id).first()
        
        if not conversation:
            return response.error_response('Conversation not found', 404)
        
        # Clean content before storing (especially for AI responses)
        content = data['content']
        if data['role'] == 'assistant':
            # Apply content cleaning for AI responses to remove raw chunks
            content = PDFProcessor.clean_chunk_text(content)
        
        # Create message
        message = Message(
            conversation_id=conversation_id,
            content=content,
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
        
        # Clean content before storing (especially for AI responses)
        content = data['content']
        if data['role'] == 'assistant':
            # Apply content cleaning for AI responses to remove raw chunks
            content = PDFProcessor.clean_chunk_text(content)
        
        # Create message
        message = Message(
            conversation_id=conversation_id,
            content=content,
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

@api.route('/chat/ai-response', methods=['POST'])
@jwt_required()
def get_ai_response():
    """Get AI response for a message in context of a conversation"""
    try:
        user = get_user_from_jwt()
        
        if not user:
            return response.error_response('User not found', 401)
        
        data = request.json
        
        if not data:
            return response.error_response('No data provided', 400)
        
        if not data or 'conversation_id' not in data or 'message' not in data:
            return response.error_response('Conversation ID and message are required', 400)
        
        conversation_id = data['conversation_id']
        user_message = data['message']
        
        # Verify the conversation belongs to the user
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=user.id).first()
        
        if not conversation:
            return response.error_response('Conversation not found', 404)
        
        # Get the document for context
        document = Document.query.get(conversation.document_id)
        
        if not document or not document.session_id:
            return response.error_response('Document not found or not processed', 404)
          # Check if we have a session for this document
        if document.session_id not in USER_SESSIONS:
            # Try to process the document automatically
            try:
                print(f"Session not found for document {document.id}. Processing PDF...")
                
                if not os.path.exists(document.file_path):
                    return response.error_response('Document file not found', 404)
                
                # Process PDF content for AI conversation
                with open(document.file_path, 'rb') as pdf_file:
                    raw_text = PDFProcessor.get_pdf_text(pdf_file)
                    text_chunks = PDFProcessor.get_text_chunks(raw_text)
                    vectorstore = PDFProcessor.get_vectorstore(text_chunks)
                    conversation_chain = PDFProcessor.get_conversation_chain(vectorstore)
                
                # Store session data for AI conversations
                USER_SESSIONS[document.session_id] = {
                    'conversation': conversation_chain,
                    'chat_history': [],
                    'pdf_name': document.original_filename,
                    'upload_time': document.upload_date.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                print(f"PDF processed successfully for session {document.session_id}")
                
            except Exception as process_error:
                print(f"Error processing PDF: {str(process_error)}")
                return response.error_response(f'Could not process document for AI conversation: {str(process_error)}', 500)
        try:
            # Start timer to measure response time
            start_time = time.time()
            
            # Get response from conversation chain
            print(f"Processing question for conversation {conversation_id}: {user_message[:50]}...")
            session_data = USER_SESSIONS[document.session_id]
            conversation_chain = session_data['conversation']
            
            # Check if we have a real langchain conversation chain or fallback mode
            if isinstance(conversation_chain, dict):
                # We're in fallback mode - langchain not available
                if not conversation_chain.get('ready', False):
                    error_msg = conversation_chain.get('error', 'AI functionality not available')
                    print(f"AI functionality not available: {error_msg}")
                    return response.error_response(f'AI functionality is currently unavailable: {error_msg}', 503)
                  # Enhanced text-based response for fallback mode
                vectorstore = conversation_chain.get('vectorstore', {})
                
                if not vectorstore.get('chunks'):
                    bot_response = "Maaf, saya tidak memiliki akses ke konten dokumen untuk menjawab pertanyaan Anda."
                else:
                    # Use enhanced search algorithm
                    relevant_chunks = PDFProcessor.search_relevant_content(vectorstore, user_message)
                    
                    if relevant_chunks:
                        # Generate enhanced response
                        bot_response = PDFProcessor.generate_response(user_message, relevant_chunks)
                    else:
                        bot_response = "Maaf, saya tidak menemukan informasi yang relevan dengan pertanyaan Anda dalam dokumen ini. Silakan coba dengan kata kunci yang berbeda atau lebih spesifik."
                  # Simulate chat history for fallback mode
                session_data['chat_history'].extend([
                    {'role': 'user', 'content': user_message},
                    {'role': 'assistant', 'content': bot_response}
                ])            
            else:
                # Real langchain conversation chain
                chain_response = conversation_chain({'question': user_message})
                
                # Extract the answer from the chain response
                bot_response = chain_response.get('answer', '')
                
                # CRITICAL: Clean the response to remove raw chunks
                bot_response = PDFProcessor.clean_chunk_text(bot_response)
                
                # Get chat history and convert to our format
                chat_history = chain_response.get('chat_history', [])
                
                # Convert LangChain message objects to our format
                formatted_history = []
                for message in chat_history:
                    if hasattr(message, 'content'):
                        role = 'user' if hasattr(message, 'type') and message.type == 'human' else 'assistant'
                        # Also clean content in chat history
                        content = PDFProcessor.clean_chunk_text(message.content) if role == 'assistant' else message.content
                        formatted_history.append({
                            'role': role,
                            'content': content
                        })
                
                # Update session chat history with formatted messages
                session_data['chat_history'] = formatted_history
              # Calculate response time
            response_time = time.time() - start_time
            
            # DEBUG: Log the actual response being sent
            print(f"🔍 DEBUG - AI Response Length: {len(bot_response)}")
            print(f"🔍 DEBUG - Response Preview: {bot_response[:200]}...")
            
            # Check for raw chunk indicators
            raw_indicators = ['chunk', 'page_content', 'metadata', 'source']
            has_raw = any(indicator in bot_response.lower() for indicator in raw_indicators)
            
            if has_raw:
                print("❌ DEBUG - Backend response contains raw chunks!")
                found_indicators = [ind for ind in raw_indicators if ind in bot_response.lower()]
                print(f"❌ DEBUG - Found indicators: {found_indicators}")
            else:
                print("✅ DEBUG - Backend response appears natural")
            
            return response.success_response({
                'response': bot_response,
                'response_time': f"{response_time:.2f}s"
            }, 'AI response generated successfully', 200)
            
        except Exception as e:
            print(f"Error in AI processing: {str(e)}")
            return response.error_response(f'AI processing error: {str(e)}', 500)
        
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
        conversation_chain = USER_SESSIONS[session_id]['conversation']
        
        # Check if we have a real langchain conversation chain or fallback mode
        if isinstance(conversation_chain, dict):
            # We're in fallback mode - langchain not available
            if not conversation_chain.get('ready', False):
                error_msg = conversation_chain.get('error', 'AI functionality not available')
                return jsonify({"error": f"AI functionality is currently unavailable: {error_msg}"}), 503
              # Enhanced text-based response for fallback mode
            vectorstore = conversation_chain.get('vectorstore', {})
            
            if not vectorstore.get('chunks'):
                bot_response = "Maaf, saya tidak memiliki akses ke konten dokumen untuk menjawab pertanyaan Anda."
            else:
                # Use enhanced search algorithm
                relevant_chunks = PDFProcessor.search_relevant_content(vectorstore, user_question)
                
                if relevant_chunks:
                    # Generate enhanced response
                    bot_response = PDFProcessor.generate_response(user_question, relevant_chunks)
                else:
                    bot_response = "Maaf, saya tidak menemukan informasi yang relevan dengan pertanyaan Anda dalam dokumen ini. Silakan coba dengan kata kunci yang berbeda atau lebih spesifik."
            
            # Simulate chat history for fallback mode
            USER_SESSIONS[session_id]['chat_history'].extend([
                {'role': 'user', 'content': user_question},
                {'role': 'assistant', 'content': bot_response}
            ])        
            # Real langchain conversation chain
            chain_response = conversation_chain({'question': user_question})
            
            # Extract the answer from the chain response
            bot_response = chain_response.get('answer', '')
            
            # Get chat history and convert to our format
            chat_history = chain_response.get('chat_history', [])
            
            # Convert LangChain message objects to our format
            formatted_history = []
            for message in chat_history:
                if hasattr(message, 'content'):
                    role = 'user' if hasattr(message, 'type') and message.type == 'human' else 'assistant'
                    formatted_history.append({
                        'role': role,
                        'content': message.content
                    })
            
            # Update session chat history with formatted messages
            USER_SESSIONS[session_id]['chat_history'] = formatted_history
        
        # Calculate response time
        response_time = time.time() - start_time
        
        return jsonify({
            "response": bot_response,
            "response_time": f"{response_time:.2f}"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/documents/<int:document_id>/process', methods=['POST'])
@jwt_required()
def process_document_for_ai(document_id):
    """Process an existing document for AI conversation"""
    try:
        user = get_user_from_jwt()
        
        document = Document.query.filter_by(id=document_id, user_id=user.id).first()
        
        if not document:
            return response.error_response('Document not found', 404)
        
        if not os.path.exists(document.file_path):
            return response.error_response('Document file not found', 404)
        
        try:
            # Process PDF content for AI conversation
            print(f"Processing PDF for AI: {document.original_filename}")
            with open(document.file_path, 'rb') as pdf_file:
                raw_text = PDFProcessor.get_pdf_text(pdf_file)
                text_chunks = PDFProcessor.get_text_chunks(raw_text)
                vectorstore = PDFProcessor.get_vectorstore(text_chunks)
                conversation_chain = PDFProcessor.get_conversation_chain(vectorstore)
            
            # Use existing session_id or create new one
            session_id = document.session_id or str(uuid.uuid4())
            
            # Store session data for AI conversations
            USER_SESSIONS[session_id] = {
                'conversation': conversation_chain,
                'chat_history': [],
                'pdf_name': document.original_filename,
                'upload_time': document.upload_date.strftime("%Y-%m-%d %H:%M:%S")
            }
              # Update document with session_id and processed status
            if not document.session_id:
                document.session_id = session_id
            document.processed = True  # Mark as processed after successful AI processing
            db.session.commit()
            
            print(f"PDF processed successfully. Session ID: {session_id}")
            
            return response.success_response({
                'session_id': session_id,
                'message': 'Document processed successfully for AI conversation'
            }, 'Document processed successfully', 200)
            
        except Exception as e:
            print(f"Error processing PDF for AI: {str(e)}")
            return response.error_response(f'Error processing PDF: {str(e)}', 500)
        
    except Exception as e:
        return response.error_response(str(e))
