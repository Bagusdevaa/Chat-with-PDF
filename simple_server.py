import os
from flask import Flask, render_template, request, jsonify

# Create Flask app
app = Flask(__name__)

# Ensure upload directory exists
os.makedirs('static/uploads', exist_ok=True)

@app.route('/')
def index():
    """Render index page"""
    return render_template('index.html')

@app.route('/ping', methods=['GET'])
def ping():
    """Simple test endpoint"""
    return jsonify({"status": "success", "message": "Server is running"})

@app.route('/pdf-test')
def pdf_test():
    """Serve the PDF.js test page"""
    return app.send_static_file('pdf_test.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload"""
    print("Upload request received")
    
    if 'pdf_file' not in request.files:
        print("No file part in request")
        return jsonify({"error": "No file part"}), 400
    
    pdf_file = request.files['pdf_file']
    print(f"File received: {pdf_file.filename}")
    
    if pdf_file.filename == '':
        print("Empty filename")
        return jsonify({"error": "No file selected"}), 400
    
    if not pdf_file.filename.endswith('.pdf'):
        print("Not a PDF file")
        return jsonify({"error": "File must be a PDF"}), 400
    
    try:
        # Generate a unique filename
        session_id = os.urandom(16).hex()
        print(f"Generated session ID: {session_id}")
        
        # Save PDF file for viewing
        pdf_path = os.path.join('static', 'uploads', f"{session_id}.pdf")
        pdf_file.save(pdf_path)
        print(f"PDF saved to {pdf_path}")
        
        # Return the response
        return jsonify({
            "success": True, 
            "session_id": session_id,
            "pdf_name": pdf_file.filename,
            "pdf_path": f"/{pdf_path}"  # Add leading slash for proper URL path
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Simple mock chat response for testing"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    return jsonify({
        "response": "This is a test response. AI processing is disabled in this simplified version.",
        "response_time": "0.1"
    })

if __name__ == '__main__':
    print("Starting Flask server...")
    print(f"Current working directory: {os.getcwd()}")
    app.run(debug=True)
