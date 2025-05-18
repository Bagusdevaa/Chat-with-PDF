from flask import Blueprint, request, jsonify, current_app
import os
import time
import uuid
import datetime
from app.models.pdf_processor import PDFProcessor

api = Blueprint('api', __name__)

# Store user sessions in memory (in production, should use a database)
USER_SESSIONS = {}

@api.route('/ping', methods=['GET'])
def ping():
    """Simple test endpoint"""
    return jsonify({"status": "success", "message": "API is running"})

@api.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload"""
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

@api.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
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
