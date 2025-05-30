from flask import request, session
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_login import login_user
from app.models.user import User
import os
from app import response, db
from datetime import datetime, timedelta, timezone

def singleobject(data):
    data = {
        'id': data.id,
        'username': data.username,
        'email': data.email
    }
    return data

def register():
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check for required fields
        if not username:
            return response.error_response('Username is required')
        
        if not email:
            return response.error_response('Email is required')
            
        if not password:
            return response.error_response('Password is required')

        # Create user object
        user = User(
            username = username,
            email = email
        )

        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return response.success_response('', 'Account created successfully', 200)

    except Exception as e:
        return response.error_response(str(e))

def login():
    try:
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user:
            return response.error_response("User not found", 404)
        
        if not user.check_password(password):
            return response.error_response("Invalid password", 401)
        
        data = singleobject(user)

        expires = datetime.timedelta(days = 1)
        expires_refresh = datetime.timedelta(days = 10)        # Use user ID as the identity (subject for the token)
        access_token = create_access_token(identity=str(user.id), expires_delta=expires)
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=expires_refresh)
        
        # Update last login timestamp
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Log in the user with Flask-Login
        login_user(user)
        
        return response.success_response({
            'data' : data,
            'access_token' : access_token,
            'refresh_token' : refresh_token,
        }, 'Login successful', 200)

    except Exception as e:
        return response.error_response(str(e))