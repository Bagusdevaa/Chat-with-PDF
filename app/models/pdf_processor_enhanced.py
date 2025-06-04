from PyPDF2 import PdfReader
import os
import re
from collections import Counter

# Set langchain as unavailable to avoid hanging imports
LANGCHAIN_AVAILABLE = False
print("PDF Processor loaded in enhanced simple mode")

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
                    # Clean text from unwanted characters
                    cleaned_text = ' '.join(page_text.split())
                    text += cleaned_text + "\n\n"  # Add separator between pages
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            raise
        return text

    @staticmethod
    def get_text_chunks(text):
        """Split text into chunks with sentence-aware splitting"""
        # Enhanced chunking that tries to preserve sentence boundaries
        chunk_size = 1500
        chunk_overlap = 300
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Start new chunk with overlap
                    current_chunk = current_chunk[-chunk_overlap:] + " " + paragraph
                else:
                    # Paragraph is too long, split it by sentences
                    sentences = re.split(r'[.!?]+', paragraph)
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) > chunk_size:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                                current_chunk = sentence
                            else:
                                # Even single sentence is too long, force split
                                chunks.append(sentence[:chunk_size])
                        else:
                            current_chunk += " " + sentence
            else:
                current_chunk += " " + paragraph
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if chunk.strip()]

    @staticmethod
    def get_vectorstore(text_chunks):
        """Create enhanced simple vector store with keyword indexing"""
        # Create keyword index for better searching
        keyword_index = {}
        
        for i, chunk in enumerate(text_chunks):
            # Extract important words (longer than 3 characters, not common words)
            words = re.findall(r'\b[a-zA-Z]{4,}\b', chunk.lower())
            common_words = {'that', 'this', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'would', 'there', 'could', 'other', 'more', 'very', 'what', 'know', 'just', 'first', 'get', 'over', 'think', 'also', 'its', 'our', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call', 'who', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'}
            
            for word in words:
                if word not in common_words:
                    if word not in keyword_index:
                        keyword_index[word] = []
                    keyword_index[word].append(i)
        
        return {
            'chunks': text_chunks,
            'keyword_index': keyword_index,
            'type': 'enhanced_simple',
            'error': 'Enhanced simple mode - keyword-based search'
        }

    @staticmethod
    def get_conversation_chain(vectorstore):
        """Create enhanced conversation chain with better response generation"""
        return {
            'vectorstore': vectorstore,
            'type': 'enhanced_simple',
            'ready': True,
            'error': 'Enhanced mode - intelligent keyword matching'
        }

    @staticmethod
    def search_relevant_content(vectorstore, query, max_chunks=3):
        """Enhanced search function with scoring"""
        if not isinstance(vectorstore, dict) or 'chunks' not in vectorstore:
            return []
            
        chunks = vectorstore['chunks']
        keyword_index = vectorstore.get('keyword_index', {})
        
        # Prepare query words
        query_words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        
        # Score chunks based on keyword matches
        chunk_scores = {}
        
        for word in query_words:
            if word in keyword_index:
                for chunk_idx in keyword_index[word]:
                    if chunk_idx not in chunk_scores:
                        chunk_scores[chunk_idx] = 0
                    # Score based on word frequency and position
                    chunk_scores[chunk_idx] += 1
        
        # Additional scoring based on direct text search
        for i, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            direct_matches = sum(1 for word in query_words if word in chunk_lower)
            if direct_matches > 0:
                if i not in chunk_scores:
                    chunk_scores[i] = 0
                chunk_scores[i] += direct_matches * 0.5
        
        # Sort chunks by score and return top matches
        sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)
        relevant_chunks = []
        
        for chunk_idx, score in sorted_chunks[:max_chunks]:
            relevant_chunks.append({
                'content': chunks[chunk_idx],
                'score': score,
                'index': chunk_idx
            })
        
        return relevant_chunks

    @staticmethod
    def generate_response(query, relevant_chunks):
        """Generate a well-formatted response based on relevant chunks"""
        if not relevant_chunks:
            return "Maaf, saya tidak menemukan informasi yang relevan dengan pertanyaan Anda dalam dokumen ini. Silakan coba dengan kata kunci yang berbeda atau lebih spesifik."
        
        # Determine response type based on query
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['apa', 'what', 'apakah', 'bagaimana', 'how']):
            response_type = 'explanation'
        elif any(word in query_lower for word in ['daftar', 'list', 'sebutkan', 'berapa', 'jumlah']):
            response_type = 'list'
        elif any(word in query_lower for word in ['dimana', 'where', 'kapan', 'when']):
            response_type = 'specific'
        else:
            response_type = 'general'
        
        # Build response based on type
        if response_type == 'list':
            response = "Berdasarkan dokumen, berikut informasi yang saya temukan:\n\n"
            for i, chunk in enumerate(relevant_chunks, 1):
                # Extract list-like items from chunk
                content = chunk['content']
                lines = content.split('\n')
                list_items = [line.strip() for line in lines if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•') or re.match(r'^\d+\.', line.strip()))]
                
                if list_items:
                    response += f"**Bagian {i}:**\n"
                    for item in list_items[:5]:  # Limit to 5 items per chunk
                        response += f"• {item}\n"
                    response += "\n"
                else:
                    # If no clear list items, show the content as a paragraph
                    response += f"**Informasi {i}:** {content[:300]}{'...' if len(content) > 300 else ''}\n\n"
        
        elif response_type == 'explanation':
            response = "Berdasarkan dokumen, berikut penjelasannya:\n\n"
            # Combine the most relevant chunks for explanation
            combined_content = ""
            for chunk in relevant_chunks[:2]:  # Use top 2 chunks for explanation
                combined_content += chunk['content'] + " "
            
            # Clean and format the content
            combined_content = combined_content.strip()
            if len(combined_content) > 800:
                combined_content = combined_content[:800] + "..."
            
            response += combined_content
        
        else:  # general or specific
            response = "Berdasarkan dokumen yang saya analisis:\n\n"
            for i, chunk in enumerate(relevant_chunks, 1):
                content = chunk['content']
                if len(content) > 400:
                    content = content[:400] + "..."
                response += f"**Informasi {i}:**\n{content}\n\n"
        
        # Add confidence indicator
        total_score = sum(chunk['score'] for chunk in relevant_chunks)
        if total_score >= 3:
            confidence = "tinggi"
        elif total_score >= 1.5:
            confidence = "sedang"
        else:
            confidence = "rendah"
        
        response += f"\n*Tingkat kepercayaan jawaban: {confidence}*"
        
        return response
