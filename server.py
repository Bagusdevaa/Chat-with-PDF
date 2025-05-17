import os
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import datetime
import time
import uuid
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session

# Store user sessions in memory (in production, use a database)
USER_SESSIONS = {}

def get_pdf_text(pdf_file):
    """Extract text from PDF file"""
    text = ""
    try:
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        raise
    return text

def get_text_chunks(text):
    """Split text into chunks"""
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    """Create vector store from text chunks"""
    embeddings = OpenAIEmbeddings()
    # Alternative: embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    """Create conversation chain with vector store"""
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True
    )
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

@app.route('/')
def index():
    """Render index page"""
    return render_template('index.html')

@app.route('/ping', methods=['GET'])
def ping():
    """Simple test endpoint"""
    return jsonify({"status": "success", "message": "Server is running"})

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
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        print(f"Generated session ID: {session_id}")
          # Save PDF file for viewing first
        pdf_path = os.path.join('static', 'uploads', f"{session_id}.pdf")
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        pdf_file.save(pdf_path)
        
        # Now reopen the file for processing
        with open(pdf_path, 'rb') as saved_pdf:
            raw_text = get_pdf_text(saved_pdf)
            text_chunks = get_text_chunks(raw_text)
            vectorstore = get_vectorstore(text_chunks)
            conversation_chain = get_conversation_chain(vectorstore)
        
        # Store session data
        USER_SESSIONS[session_id] = {
            'conversation': conversation_chain,
            'chat_history': [],
            'pdf_name': pdf_file.filename,
            'upload_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
          # Return the response with proper URL for the PDF
        return jsonify({
            "success": True, 
            "session_id": session_id,
            "pdf_name": pdf_file.filename,
            "pdf_path": f"/{pdf_path}"  # Add leading slash for proper URL path
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    session_id = data.get('session_id')
    user_question = data.get('question')
    
    if not session_id or not user_question:
        return jsonify({"error": "Session ID and question are required"}), 400
    
    if session_id not in USER_SESSIONS:
        return jsonify({"error": "Session not found or expired"}), 404
    
    try:
        # Start timer to measure response time
        start_time = time.time()
        
        # Get response from conversation chain
        response = USER_SESSIONS[session_id]['conversation']({'question': user_question})
        chat_history = response['chat_history']
        
        # Update session chat history
        USER_SESSIONS[session_id]['chat_history'] = chat_history
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Get the bot's response (last message in chat history)
        bot_response = chat_history[-1].content
        
        return jsonify({
            "response": bot_response,
            "response_time": f"{response_time:.2f}"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        # Ensure upload directory exists
        os.makedirs('static/uploads', exist_ok=True)
        print("Upload directory created/verified at static/uploads")
        
        # Print current working directory for debugging
        print(f"Current working directory: {os.getcwd()}")
        
        # Run the Flask app
        print("Starting Flask server...")
        app.run(debug=True)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
