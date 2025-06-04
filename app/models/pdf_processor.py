from PyPDF2 import PdfReader
import os
import re

# Initialize langchain availability flag
LANGCHAIN_AVAILABLE = False

# Try to import langchain components
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.chat_models import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationalRetrievalChain
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
    print("Langchain components imported successfully")
except ImportError as e:
    print(f"Warning: Langchain not available. AI functionality will be limited. Error: {e}")
    # Define dummy classes to prevent NameError
    RecursiveCharacterTextSplitter = None
    OpenAIEmbeddings = None
    FAISS = None
    ChatOpenAI = None
    ConversationBufferMemory = None
    ConversationalRetrievalChain = None
    PromptTemplate = None

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
        if LANGCHAIN_AVAILABLE:
            try:
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=420,
                    length_function=len,
                )
                chunks = text_splitter.split_text(text)
                return chunks
            except Exception as e:
                print(f"Error with langchain text splitter: {e}")
                # Fallback to simple chunking
        
        # Simple chunking fallback
        chunk_size = 1000
        chunk_overlap = 200
        chunks = []
        
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks    
    
    @staticmethod
    def get_vectorstore(text_chunks):
        """Create vector store from text chunks"""
        if not LANGCHAIN_AVAILABLE:
            return {
                'chunks': text_chunks,
                'type': 'simple',
                'error': 'Langchain not available'
            }
            
        try:
            # Check if OpenAI API key is available
            if not os.getenv('OPENAI_API_KEY'):
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
            return vectorstore
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
            # Return simple fallback            
            return {
                'chunks': text_chunks,
                'type': 'simple',
                'error': str(e)
            }    
        
    @staticmethod
    def get_conversation_chain(vectorstore):
        """Create conversation chain with vector store and improved prompt"""
        if not LANGCHAIN_AVAILABLE:
            return {
                'vectorstore': vectorstore,
                'type': 'simple',
                'ready': True,  # Mark as ready for simple fallback mode
                'error': 'Langchain not available - using simple text matching'
            }
            
        # If vectorstore is our simple fallback, return simple chain
        if isinstance(vectorstore, dict) and vectorstore.get('type') == 'simple':
            return {
                'vectorstore': vectorstore,
                'type': 'simple',
                'ready': True,  # Mark as ready for simple fallback mode
                'error': vectorstore.get('error', 'Simple mode - advanced AI not available')
            }
            
        try:
            # Check if OpenAI API key is available
            if not os.getenv('OPENAI_API_KEY'):
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            
            llm = ChatOpenAI(temperature=0.1)  # Lower temperature for more consistent responses
              # Custom prompt template to enhance retrieval of all information
            prompt_template = """
            Kamu adalah asisten AI yang membantu menjawab pertanyaan berdasarkan dokumen yang diberikan. 
            Berikan jawaban yang informatif dan mudah dipahami dalam bahasa yang natural.

            [BEGIN KONTEN DOKUMEN]
            {context}
            [END KONTEN DOKUMEN]

            INSTRUKSI:
            - Jawablah pertanyaan berdasarkan isi dokumen di atas dengan bahasa yang natural dan mudah dipahami
            - Jika informasi yang diminta tidak ada dalam dokumen, jawab dengan: "Informasi tersebut tidak ditemukan dalam dokumen."
            - Berikan jawaban yang terstruktur dan jelas
            - Jangan menambahkan informasi dari pengetahuan luar atau asumsi
            - Gunakan format yang mudah dibaca dengan paragraf atau poin-poin jika diperlukan

            Pertanyaan: {question}
            Jawaban:
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
                retriever=vectorstore.as_retriever(search_type="mmr",
                                                   search_kwargs={
                                                       "k": 6,
                                                       "fetch_k": 20,
                                                       "lambda_mult": 0.7}),  # Retrieve more documents
                memory=memory,
                combine_docs_chain_kwargs={"prompt": PROMPT}
            )
            return conversation_chain
        except Exception as e:
            print(f"Error creating conversation chain: {str(e)}")
            return {
                'vectorstore': vectorstore,
                'type': 'simple',
                'ready': True,  # Mark as ready for simple fallback mode
                'error': str(e)
            }
    
    @staticmethod
    def search_relevant_content(vectorstore, question):
        """
        Search for relevant content chunks based on the question.
        Fallback implementation for when LangChain is not available.
        """
        if not vectorstore or not vectorstore.get('chunks'):
            return []
            
        chunks = vectorstore.get('chunks', [])
        question_lower = question.lower()
        
        # Simple keyword-based scoring
        scored_chunks = []
        
        for i, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            score = 0
            
            # Split question into words for better matching
            question_words = question_lower.split()
            
            # Score based on word matches
            for word in question_words:
                if len(word) > 2:  # Only consider words longer than 2 characters
                    if word in chunk_lower:
                        score += 1
                    # Bonus for exact phrase match
                    if question_lower in chunk_lower:
                        score += 3
            
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # Sort by score and return top chunks
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
          # Return top 3 most relevant chunks
        return [chunk for chunk, score in scored_chunks[:3]]
    
    @staticmethod
    def generate_response(question, relevant_chunks):
        """
        Generate a human-readable response from relevant chunks.
        Fallback implementation for when LangChain is not available.
        """
        if not relevant_chunks:
            return "Maaf, saya tidak menemukan informasi yang relevan dengan pertanyaan Anda dalam dokumen ini."
        
        # Clean and process chunks to make them more readable
        processed_chunks = []
        for chunk in relevant_chunks:
            # Clean the chunk text thoroughly
            cleaned = PDFProcessor.clean_chunk_text(chunk)
            if cleaned and len(cleaned.strip()) > 20:  # Only use substantial chunks
                processed_chunks.append(cleaned)
        
        if not processed_chunks:
            return "Maaf, saya tidak dapat memproses informasi dari dokumen untuk menjawab pertanyaan Anda."
        
        # Simple response formatting based on question type
        question_lower = question.lower()
        
        # Create a natural response
        if any(word in question_lower for word in ['apa', 'what', 'tentang', 'about']):
            intro = "Berdasarkan dokumen, "
        elif any(word in question_lower for word in ['bagaimana', 'how', 'cara']):
            intro = "Dari informasi dalam dokumen, "
        elif any(word in question_lower for word in ['mengapa', 'why', 'kenapa']):
            intro = "Menurut dokumen, "
        else:
            intro = "Informasi yang saya temukan: "
        
        # Combine processed chunks naturally
        if len(processed_chunks) == 1:
            content = processed_chunks[0]
        else:
            # For multiple chunks, create a flowing narrative
            content = processed_chunks[0]
            for chunk in processed_chunks[1:]:
                # Add connecting words for better flow
                content += f" Selain itu, {chunk}"
        
        # Ensure proper ending
        if content and not content.endswith(('.', '!', '?')):
            content += '.'
        
        response = intro + content
        
        # Limit response length and ensure it's not too verbose
        if len(response) > 1200:
            sentences = response.split('. ')
            response = '. '.join(sentences[:3]) + '.'
        
        return response.strip()
    
    @staticmethod
    def clean_chunk_text(chunk):
        """
        Clean raw chunk text to make it more readable.
        """
        # Convert to string if it's not already
        text = str(chunk)
        
        # Remove common PDF artifacts and metadata
        text = re.sub(r'page_content[:\s]*[\'"]?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'metadata[:\s]*\{[^}]*\}', '', text, flags=re.IGNORECASE)
        text = re.sub(r'source[:\s]*[\'"][^\'\"]*[\'"]', '', text, flags=re.IGNORECASE)
        
        # Remove page numbers at start/end
        text = re.sub(r'^\s*\d+\s*\n', '', text)
        text = re.sub(r'\n\s*\d+\s*$', '', text)
        
        # Clean up excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing quotes or brackets
        text = text.strip('\'"[]{}()')
        
        return text.strip()