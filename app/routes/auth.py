from app import create_app
from flask import Blueprint, request, jsonify
from app.models.user import User
from app.response import success_response, error_response
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    pass


@auth.route('/login', methods=['POST'])
def login():
    pass
