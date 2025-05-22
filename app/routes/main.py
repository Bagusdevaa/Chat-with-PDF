from flask import Blueprint, render_template, redirect, url_for

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

@main.route('/conversation/<document_id>')
def conversation(document_id):
    return render_template('conversation.html', document_id=document_id)
    
@main.route('/login')
def login():
    # Placeholder route for login page - will be implemented in future
    return render_template('login.html')
    
@main.route('/signup')
def signup():
    # Placeholder route for signup page - will be implemented in future
    return render_template('signup.html')

@main.route('/profile')
def profile():
    # Placeholder route for profile page
    return render_template('profile.html')

@main.route('/logout')
def logout():
    # Placeholder route for logout - will be implemented with Flask-Login
    return redirect(url_for('main.index'))