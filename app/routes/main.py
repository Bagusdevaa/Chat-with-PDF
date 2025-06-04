from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.documents import Document
from app.models.conversation import Conversation
from app.models.user import User
import time
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Add timestamp for cache busting
    timestamp = str(int(time.time()))
    response = make_response(render_template('landing.html', timestamp=timestamp))
    
    # Add aggressive no-cache headers for landing page
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = 'Mon, 01 Jan 1990 00:00:00 GMT'
    
    return response

@main.route('/static/js/<path:filename>')
def serve_js_with_no_cache(filename):
    """Serve JavaScript files with no-cache headers"""
    from flask import current_app
    
    # Get the static folder path
    static_folder = current_app.static_folder
    js_folder = os.path.join(static_folder, 'js')
    
    # Create response with the JavaScript file
    response = make_response(send_from_directory(js_folder, filename))
    
    # Add aggressive no-cache headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache' 
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = 'Mon, 01 Jan 1990 00:00:00 GMT'
    response.headers['Content-Type'] = 'application/javascript'
    
    return response

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/documents')
def documents():
    return render_template('documents.html')

@main.route('/profile')
def profile():
    return render_template('profile.html')

@main.route('/conversation/<int:conversation_id>')
def conversation(conversation_id):
    """View conversation page"""
    try:
        # Get conversation with document info
        conversation = Conversation.query.get_or_404(conversation_id)
        document = Document.query.get_or_404(conversation.document_id)
        
        return render_template('conversation.html', 
                             conversation=conversation, 
                             document=document)
    except Exception as e:
        flash('Conversation not found', 'error')
        return redirect(url_for('main.documents'))

@main.route('/chat/<int:document_id>')
def chat_with_document(document_id):
    """Create or get existing conversation for a document and redirect to conversation page"""
    try:
        # Find existing conversation for this document
        conversation = Conversation.query.filter_by(document_id=document_id).first()
        
        if not conversation:
            # Create new conversation if none exists
            document = Document.query.get_or_404(document_id)
            conversation = Conversation(
                user_id=document.user_id,
                document_id=document_id,
                title=f"Chat with {document.original_filename}"
            )
            from app import db
            db.session.add(conversation)
            db.session.commit()
        return redirect(url_for('main.conversation', conversation_id=conversation.id))
    except Exception as e:
        flash('Failed to start conversation', 'error')
        return redirect(url_for('main.documents'))