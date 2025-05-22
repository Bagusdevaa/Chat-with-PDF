from flask import jsonify, make_response

def success_response(data=None, message="Success", status_code=200):
    response = {
        "status": "success",
        "message": message,
        "data": data
    }
    return make_response(jsonify(response), status_code)

def error_response(message="Error", status_code=400):
    response = {
        "status": "error",
        "message": message
    }
    return make_response(jsonify(response), status_code)