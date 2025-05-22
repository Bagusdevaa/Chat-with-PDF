from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.user import User
import os
from app import response, db

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

# def login():
#     try:
#         pass
#     except Exception as e:
#         pass