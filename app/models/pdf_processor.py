from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
import os

class PDFProcessor:
    @staticmethod
    def get_pdf_text(pdf_file):
        """Extract text from PDF file with improved handling"""
        text = ""
        try:
            pdf_reader = PdfReader(pdf_file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    # Membersihkan teks dari karakter yang tidak diinginkan
                    cleaned_text = ' '.join(page_text.split())
                    text += cleaned_text + "\n\n"  # Tambahkan pemisah antar halaman
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            raise
        return text

    @staticmethod
    def get_text_chunks(text):
        """Split text into chunks using RecursiveCharacterTextSplitter for better results"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=400,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        return chunks

    @staticmethod
    def get_vectorstore(text_chunks):
        """Create vector store from text chunks"""
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        return vectorstore

    @staticmethod
    def get_conversation_chain(vectorstore):
        """Create conversation chain with vector store and improved prompt"""
        llm = ChatOpenAI(temperature=0)  # Lower temperature for more consistent responses
        
        # Custom prompt template to enhance retrieval of all information
        prompt_template = """
        Kamu adalah asisten AI yang membantu menganalisis dokumen.
        Berdasarkan konteks berikut:
        {context}
        
        Jawab pertanyaan berikut dengan lengkap, mencakup SEMUA informasi yang tersedia dalam dokumen. 
        Jika ditanya tentang daftar atau item-item seperti project, pengalaman, atau keterampilan, 
        pastikan untuk mencantumkan SEMUA item yang ada dalam dokumen, tidak boleh ada yang terlewat.
        
        Pertanyaan: {question}
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "question"]
        )
        
        memory = ConversationBufferMemory(
            memory_key='chat_history', return_messages=True
        )
        
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 8}),  # Retrieve more documents
            memory=memory,
            combine_docs_chain_kwargs={"prompt": PROMPT}
        )
        return conversation_chain