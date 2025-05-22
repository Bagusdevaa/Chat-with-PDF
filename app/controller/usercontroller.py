from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token


def singleobject(data):
    data = {
        'id': data.id,
        'name': data.name,
        'email': data.email,
        'level': data.level
    }
    return data

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

        expires = datetime.timedelta(days=1)
        expires_refresh = datetime.timedelta(days=10)

        # Use user ID as the identity (subject) for the token
        access_token = create_access_token(identity=str(user.id), expires_delta=expires)
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=expires_refresh)

        return response.success_response({
            'data': data,
            'access_token': access_token,
            'refresh_token': refresh_token
        }, "Login successful", 200)
    except Exception as e:
        return response.error_response(str(e))