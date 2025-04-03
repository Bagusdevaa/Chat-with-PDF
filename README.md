# PDFChat Project

PDFChat is a Streamlit application that allows users to interact with multiple PDF documents through a conversational interface. The application processes uploaded PDF files, extracts their text, and enables users to ask questions about the content using a local Hugging Face model.

## Project Structure

```
PDFChat
├── models
│   └── huggingface_model
│       └── [downloaded_model_files]
├── src
│   ├── app.py
│   ├── htmlTemplates.py
│   └── utils
│       ├── __init__.py
│       ├── pdf_processing.py
│       ├── text_processing.py
│       └── model_loading.py
├── requirements.txt
├── .env
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd PDFChat
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Download the necessary Hugging Face model and place it in the `models/huggingface_model` directory.

4. Set up your environment variables in the `.env` file as needed.

## Usage

1. Run the application:
   ```
   streamlit run src/app.py
   ```

2. Open your web browser and navigate to `http://localhost:8501`.

3. Upload your PDF documents using the file uploader in the sidebar.

4. Ask questions about the content of the PDFs in the input box and receive responses from the model.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.