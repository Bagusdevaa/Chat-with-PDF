from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.documents import Document
from app.response import success_response, error_response
from app import db
from app.controller import usercontroller
from datetime import datetime, timezone
import uuid
import os

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
@auth.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return render_template('signup.html')
    elif request.method == 'POST':
        return usercontroller.register()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return render_template('login.html')
    elif request.method == 'POST':
        response = usercontroller.login()
        return response

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        if not email:
            return error_response('Email is required')
        
        user = User.query.filter_by(email=email).first()
        if not user:
            # Still show success to prevent email enumeration
            return success_response('', 'If your email is registered, you will receive a password reset link.', 200)
            
        # Generate reset token
        token = user.generate_reset_token()
        db.session.commit()
        
        # Here you would send an email with the reset token
        # For now, just return the token in the response for testing
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        # In production, you would use Flask-Mail to send an email
        # mail.send_message(
        #     'Reset Your Password',
        #     sender='noreply@pdfchat.com',
        #     recipients=[user.email],
        #     body=f'Click the link to reset your password: {reset_url}'
        # )
        
        return success_response({'reset_url': reset_url}, 'Password reset link sent. Check your email.', 200)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        return render_template('reset_password.html', token=token)
    elif request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password:
            return error_response('Password is required')
            
        if password != confirm_password:
            return error_response('Passwords do not match')
        
        # Find user by token
        user = User.query.filter_by(reset_token=token).first()
        if not user or not user.verify_reset_token(token):
            return error_response('Invalid or expired token')
        
        user.set_password(password)
        user.clear_reset_token()
        db.session.commit()
        return success_response('', 'Your password has been reset. Please login with your new password.', 200)

@auth.route('/login-test', methods=['GET'])
def login_test():
    """Simple test route for debugging"""
    return "Login test route works!"
