# MultiPDF Chat App

> Lets chat with your PDFs documents

## Introduction

The MultiPDF Chat App is a Python application that allows you to chat with multiple PDF documents. You can ask questions about the PDFs using natural language, and the application will provide relevant responses based on the content of the documents. This app utilizes a language model to generate accurate answers to your queries. Please note that the app will only respond to questions related to the loaded PDFs.

## How It Works

![MultiPDF Chat App Diagram](./docs/PDF-LangChain.jpg)

The application follows these steps to provide responses to your questions:

1.  **PDF Loading:** The app reads multiple PDF documents and extracts their text content.
2.  **Text Chunking:** The extracted text is divided into smaller chunks that can be processed effectively.
3.  **Language Model:** The application utilizes a language model to generate vector representations (embeddings) of the text chunks.
4.  **Similarity Matching:** When you ask a question, the app compares it with the text chunks and identifies the most semantically similar ones.
5.  **Response Generation:** The selected chunks are passed to the language model, which generates a response based on the relevant content of the PDFs.

## API Options

This application has been implemented with two different API options for generating embeddings: Hugging Face and OpenAI API.

### Hugging Face

* **Details:** Uses local Hugging Face models for generating embeddings.
* **Pros:**
    * Provides full control over the embedding model.
    * Allows customization and fine-tuning of the model.
    * Ofcoure it is **FREE**
* **Cons:**
    * Significantly slower embedding generation (e.g., up to 10 minutes for a large dataset).
    * Requires substantial computational resources.
    * May require manual optimization for performance.

### OpenAI API

* **Details:** Uses OpenAI's API for generating embeddings.
* **Pros:**
    * Extremely fast embedding generation (e.g., approximately 4 seconds).
    * Leverages OpenAI's optimized infrastructure.
    * Easy to use and integrate.
* **Cons:**
    * Incurs API usage costs.
    * Less control over the embedding model.

**Note:** You can switch between these API options by modifying the configuration in the code (provide specific instruction if necessary). When using the OpenAI API, ensure that you have configured your API key correctly in the `.env` file.

## Dependencies and Installation

To install the MultiPDF Chat App, please follow these steps:

1.  Clone the repository to your local machine.

2.  Install the required dependencies by running the following command:

    ```
    pip install -r requirements.txt
    ```

3.  Obtain an API key from OpenAI and add it to the `.env` file in the project directory.

    ```commandline
    OPENAI_API_KEY=your_secret_api_key
    ```

## Usage

To use the MultiPDF Chat App, follow these steps:

1.  Ensure that you have installed the required dependencies and added the OpenAI API key to the `.env` file (if using OpenAI API).

2.  Run the `app.py` file using the Streamlit CLI. Execute the following command:

    ```
    streamlit run app.py
    ```

3.  The application will launch in your default web browser, displaying the user interface.

4.  Load multiple PDF documents into the app by following the provided instructions.

5.  Ask questions in natural language about the loaded PDFs using the chat interface.

## License

The MultiPDF Chat App is released under the [MIT License](https://opensource.org/licenses/MIT).
