# User Authentication Setup Guide

This document explains how to properly implement user authentication for the PDF Chat Assistant application.

## Current Authentication Status

Currently, the application uses a mock user for templates and doesn't have actual authentication. The system is prepared to integrate Flask-Login for proper authentication.

## Requirements

- Flask-Login (already added to requirements.txt)
- A database for storing user credentials (SQLAlchemy recommended)

## Implementation Steps

1. **Install Required Packages**

```bash
pip install flask-login flask-sqlalchemy
```

2. **Create User Model**

Create a new file at `app/models/user.py`:

```python
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

3. **Configure Flask-Login in `__init__.py`**

Replace the mock user with actual Flask-Login implementation:

```python
from flask_login import LoginManager
from app.models.user import db, User

def create_app():
    # ... existing initialization ...
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    # ... rest of the function ...
```

4. **Implement Login/Signup Routes**

Update the routes in `main.py`:

```python
from flask import request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app.models.user import User, db

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
            
        login_user(user, remember=('remember_me' in request.form))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
        
    return render_template('login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        user = User(username=request.form['username'], email=request.form['email'])
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
        
    return render_template('signup.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
```

5. **Create Database and Tables**

Create a script to initialize the database:

```python
# init_db.py
from app import create_app
from app.models.user import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database created successfully!")
```

## Security Considerations

- Always hash passwords using Werkzeug's security functions
- Use HTTPS in production
- Implement CSRF protection
- Consider adding rate limiting for login attempts
- Implement password complexity requirements
- Add email verification for new accounts

## Next Steps

- Add account recovery functionality
- Implement user roles and permissions
- Add social authentication options
