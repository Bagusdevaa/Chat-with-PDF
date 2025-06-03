from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.documents import Document
from app.models.conversation import Conversation
from app.models.user import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('landing.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/documents')
def documents():
    return render_template('documents.html')

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

@main.route('/profile')
def profile():
    # Placeholder route for profile page
    return render_template('profile.html')