# PDFChat - Chat with PDF Documents

> A web application for interacting with PDF documents using AI

## Introduction

PDFChat is a Flask web application that enables you to chat with PDF documents. You can ask questions about PDF content using natural language, and the application will provide relevant responses based on the document's content. This application utilizes Large Language Models (LLMs) to generate accurate answers to your questions with a modern and responsive interface built with Bootstrap and a purple gradient theme.

## How It Works

![PDFChat App Diagram](./docs/PDF-LangChain.jpg)

The application follows these steps to respond to your questions:

1. **PDF Loading:** The application reads PDF documents and extracts their text content.
2. **Text Chunking:** The extracted text is divided into smaller chunks that can be effectively processed using RecursiveCharacterTextSplitter.
3. **Vectorization:** The application uses language models to generate vector representations (embeddings) of the text chunks.
4. **Similarity Matching:** When you ask a question, the application compares it with the text chunks and identifies the most semantically similar ones.
5. **Response Generation:** The selected chunks are passed to the language model, which generates a response based on the relevant content from the PDF.

## Key Features

- **Split-Screen Interface:** PDF viewer on the left and chat interface on the right
- **PDF Navigation:** Intuitive PDF page controls with zoom functionality
- **Modern UI:** Purple gradient theme with clean, responsive design
- **Chat Export:** Ability to export chat history
- **PDF Download:** Option to download the currently viewed PDF
- **Responsive Design:** Adaptable layout for various screen sizes

## Technologies Used

### Backend
- **Flask:** Lightweight and flexible Python web framework
- **LangChain:** Framework for building applications with Large Language Models
- **FAISS:** Library for efficient vector search
- **OpenAI API:** For embeddings and response generation

### Frontend
- **Bootstrap:** CSS framework for responsive UI
- **PDF.js:** JavaScript library for displaying PDFs in browsers
- **Vanilla JavaScript:** For UI interactivity without additional frameworks

**Note:** When using the OpenAI API, ensure that you have configured your API key correctly in the `.env` file.

## Dependencies and Installation

To install PDFChat, please follow these steps:

1. Clone the repository to your local machine.

2. Install the required dependencies by running the following command:

    ```
    pip install -r requirements.txt
    ```

3. Obtain an API key from OpenAI and add it to the `.env` file in the project directory.

    ```
    OPENAI_API_KEY=your_secret_api_key
    ```

## Usage Instructions

To use PDFChat, follow these steps:

1. Ensure you have installed all required dependencies and added your OpenAI API key to the `.env` file.

2. Run the application using one of the following methods:

   ```
   # Using Python directly
   python run.py
   
   # Or using the batch file
   start_pdfchat.bat
   ```

3. The application will run at http://localhost:5000

4. Upload your PDF document and start chatting with the AI about the document's content.

## Project Structure

```
PDFChat/
│
├── app/                      # Main application code
│   ├── __init__.py           # Flask app initialization
│   ├── models/               # Data processing models and functions
│   │   ├── __init__.py
│   │   └── pdf_processor.py  # PDF and LLM processing
│   ├── routes/               # Route handlers
│   │   ├── __init__.py
│   │   ├── api.py            # API endpoints
│   │   └── main.py           # Main routes
│   ├── static/               # Static assets
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/          # Folder for uploaded files
│   └── templates/            # HTML templates
│
├── config.py                 # Application configuration
├── run.py                    # Application entry point
├── requirements.txt          # Project dependencies
└── README.md                 # Documentation
```

## Troubleshooting

If you encounter any issues when running the application:

1. Make sure your OpenAI API key is correctly set in the `.env` file
2. Check that all dependencies are installed with `pip install -r requirements.txt`
3. Look for detailed error messages in the console
4. For Windows-specific socket errors, the application runs with `use_reloader=False` by default
5. See `README_TROUBLESHOOTING.md` for more detailed solutions

## License

PDFChat is released under the [MIT License](https://opensource.org/licenses/MIT).
