import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template, pdf_success_template
from langchain.llms import HuggingFaceHub
import datetime
import time


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    # Get current time for this message
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Show user message immediately
    if st.session_state.chat_placeholder:
        st.session_state.chat_placeholder.markdown(
            user_template.replace("{{MSG}}", user_question).replace("{{TIME}}", current_time),
            unsafe_allow_html=True
        )
        
        # Show typing indicator
        typing_placeholder = st.session_state.chat_placeholder.empty()
        typing_placeholder.markdown("""
        <div class="chat-message bot" style="background-color: #594339; padding: 1rem; border-radius: 10px; margin-bottom: 15px;">
            <div style="display: flex; align-items: center;">
                <div style="min-width: 50px; margin-right: 10px;">
                    <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #D2B48C;">
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="color: #D2B48C; margin-right: 10px; font-weight: 500;">AI sedang mengetik</div>
                    <span style="background-color: #D2B48C; width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 5px; animation: pulse 1s infinite;"></span>
                    <span style="background-color: #D2B48C; width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 5px; animation: pulse 1s infinite 0.2s;"></span>
                    <span style="background-color: #D2B48C; width: 8px; height: 8px; border-radius: 50%; display: inline-block; animation: pulse 1s infinite 0.4s;"></span>
                </div>
            </div>
        </div>
        <style>
        @keyframes pulse {
            0% { opacity: 0.2; transform: scale(0.8); }
            50% { opacity: 1; transform: scale(1); }
            100% { opacity: 0.2; transform: scale(0.8); }
        }
        </style>
        """, unsafe_allow_html=True)

    # Start timer to measure response time
    start_time = time.time()
        
    # Process the question and get response
    try:
        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history']
        
        # Calculate response time
        response_time = time.time() - start_time
        response_time_str = f"{response_time:.2f} detik"
        
        # Clear typing indicator
        if st.session_state.chat_placeholder:
            typing_placeholder.empty()
        
        # Get the bot's response (last message in chat history)
        bot_response = st.session_state.chat_history[-1].content
        
        # Show bot response with response time
        if st.session_state.chat_placeholder:
            st.session_state.chat_placeholder.markdown(
                bot_template.replace("{{MSG}}", bot_response + f"<div style='font-size: 11px; color: #D2B48C; margin-top: 10px; text-align: right;'>Response time: {response_time_str}</div>")
                .replace("{{TIME}}", current_time),
                unsafe_allow_html=True
            )
    except Exception as e:
        # Handle errors gracefully
        if st.session_state.chat_placeholder:
            typing_placeholder.empty()
            error_message = f"""
            <div class="chat-message bot" style="background: linear-gradient(135deg, #8D6E63 0%, #7D5E53 100%);">
                <div class="avatar">
                    <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png">
                </div>
                <div class="message">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="font-weight: 600; color: #D2B48C; margin-right: 8px;">AI Assistant</div>
                        <div style="height: 8px; width: 8px; background-color: #FF5252; border-radius: 50%;"></div>
                    </div>
                    <p>Maaf, saya mengalami masalah saat memproses pertanyaan Anda. Silakan coba lagi.</p>
                    <p style="font-size: 12px; color: #FFC107;">Error: {str(e)}</p>
                    <div class="timestamp">{current_time}</div>
                </div>
            </div>
            """
            st.session_state.chat_placeholder.markdown(error_message, unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(
        page_title="PDF Chat Assistant",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.write(css, unsafe_allow_html=True)
    
    # Initialize session states - all in one block to avoid race conditions
    session_vars = [
        "conversation", "chat_history", "pdf_processed", 
        "pdf_process_time", "pdf_names", "chat_placeholder"
    ]
    
    for var in session_vars:
        if var not in st.session_state:
            if var in ["pdf_processed"]:
                st.session_state[var] = False
            elif var in ["pdf_process_time"]:
                st.session_state[var] = ""
            elif var in ["pdf_names"]:
                st.session_state[var] = []
            else:
                st.session_state[var] = None# Get current datetime
    current_datetime = datetime.datetime.now()
    formatted_date = current_datetime.strftime("%A, %d %B %Y")
    formatted_time = current_datetime.strftime("%H:%M:%S")
    
    # Create columns for main area and sidebar
    col1, col2 = st.columns([7, 3])
    
    # Main content area
    with col1:
        # Attractive header with theme
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #5D4037 0%, #3C2A21 100%); padding:20px; border-radius:15px; margin-bottom:20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);">
            <h1 style="color:#FFF8DC; text-align:center; font-size:36px; font-weight:700;">📚 PDF Chat Assistant 📚</h1>
            <p style="color:#D2B48C; text-align:center; font-size:18px; margin-top:10px;">{formatted_date} | {formatted_time}</p>
            <p style="color:#D2B48C; text-align:center; font-size:16px; margin-top:5px; opacity:0.8;">Upload PDF dan ajukan pertanyaan tentang dokumen Anda</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a container for the chat interface
        chat_container = st.container()
        
        # Placeholder for chat messages
        if "chat_placeholder" not in st.session_state or st.session_state.chat_placeholder is None:
            st.session_state.chat_placeholder = chat_container.container()
        
        # Initialize welcome message if no chat history
        if st.session_state.chat_history is None:
            welcome_msg = f"""
            <div class="chat-message bot" style="animation: fadeIn 1s ease-in-out;">
                <div class="avatar">
                    <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png">
                </div>
                <div class="message">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="font-weight: 600; color: #D2B48C; margin-right: 8px;">AI Assistant</div>
                        <div style="height: 8px; width: 8px; background-color: #4CAF50; border-radius: 50%;"></div>
                    </div>
                    <p>Selamat datang di PDF Chat Assistant! 👋</p>
                    <p>Saya siap membantu Anda dengan dokumen PDF Anda. Untuk memulai:</p>
                    <ol>
                        <li>Upload file PDF di sidebar</li>
                        <li>Klik tombol "Process"</li>
                        <li>Ajukan pertanyaan tentang dokumen Anda</li>
                    </ol>
                    <p>Setelah dokumen diproses, Anda dapat mengajukan pertanyaan apa saja tentang konten PDF tersebut.</p>
                    <div class="timestamp">{current_datetime.strftime("%H:%M:%S")}</div>
                </div>
            </div>
            """
            st.session_state.chat_placeholder.markdown(welcome_msg, unsafe_allow_html=True)
        else:
            # Display chat history
            for i, message in enumerate(st.session_state.chat_history):
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                
                if i % 2 == 0:
                    st.session_state.chat_placeholder.markdown(user_template.replace(
                        "{{MSG}}", message.content).replace("{{TIME}}", current_time), unsafe_allow_html=True)
                else:
                    st.session_state.chat_placeholder.markdown(bot_template.replace(
                        "{{MSG}}", message.content).replace("{{TIME}}", current_time), unsafe_allow_html=True)
        
        # Create a stylish separator
        st.markdown("""<div style="border-top: 1px solid rgba(210, 180, 140, 0.3); margin: 20px 0;"></div>""", unsafe_allow_html=True)
          # Create a stylish input field with button
        st.markdown("""
        <div style="margin-bottom: 10px;">
            <p style="color: #D2B48C; font-size: 16px; font-weight: 500;">Ajukan pertanyaan tentang dokumen Anda:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Input and send button in columns for better layout
        input_col1, input_col2 = st.columns([5, 1])
        with input_col1:
            # Use text_input without key to avoid conflicts
            user_question = st.text_input("User question", label_visibility="collapsed", placeholder="Ketik pertanyaan Anda di sini...")
        with input_col2:
            # Simple button without key to avoid conflicts
            send_button = st.button("Send", type="primary", disabled=not st.session_state.pdf_processed)
        
        # Handle user input using simpler logic
        if send_button and user_question and st.session_state.pdf_processed and st.session_state.conversation is not None:
            handle_userinput(user_question)
        elif user_question and send_button and not st.session_state.pdf_processed:
            st.warning("⚠️ Silakan upload dan proses file PDF terlebih dahulu untuk mengajukan pertanyaan!")
        
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #8D6E63 0%, #5D4037 100%); padding:15px; border-radius:10px; margin-bottom:20px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);">
            <h3 style="color:#FFF8DC; text-align:center; font-weight:600;">📄 Dokumen Anda</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Informative message for file upload
        st.markdown("""
        <div style="background: rgba(93, 64, 55, 0.4); padding:12px; border-radius:8px; margin-bottom:15px;">
            <p style="color:#D2B48C; font-size:14px; margin:0;">Upload file PDF Anda dan klik "Process" untuk mulai berinteraksi.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader with instructions
        pdf_docs = st.file_uploader(
            "Upload PDF files", accept_multiple_files=True, type=["pdf"])
        
        # Process button with enhanced styles
        process_btn = st.button("Process Documents", type="primary", use_container_width=True)
        
        # Show success notification
        if st.session_state.pdf_processed:
            st.markdown(
                pdf_success_template.replace("{{TIME}}", st.session_state.pdf_process_time),
                unsafe_allow_html=True
            )
            
            # Show list of processed PDFs
            if st.session_state.pdf_names:
                st.markdown("""
                <div style="background: rgba(93, 64, 55, 0.4); padding:12px; border-radius:8px; margin-top:15px;">
                    <p style="color:#D2B48C; font-size:14px; font-weight:500; margin-bottom:8px;">Dokumen yang diproses:</p>
                </div>
                """, unsafe_allow_html=True)
                
                for i, pdf_name in enumerate(st.session_state.pdf_names):
                    st.markdown(f"""
                    <div style="display:flex; align-items:center; background:rgba(93, 64, 55, 0.2); padding:8px; border-radius:6px; margin-bottom:5px;">
                        <div style="margin-right:8px; color:#D2B48C; font-weight:bold;">{i+1}.</div>
                        <div style="color:#FFF8DC; font-size:14px; word-break:break-word;">{pdf_name}</div>
                    </div>
                    """, unsafe_allow_html=True)
          # Handle processing
        if process_btn:
            if pdf_docs:
                with st.spinner("Sedang memproses dokumen..."):
                    try:
                        # Simpan nama file PDF
                        pdf_names = [pdf.name for pdf in pdf_docs]
                        st.session_state.pdf_names = pdf_names
                        
                        # Proses PDF
                        raw_text = get_pdf_text(pdf_docs)
                        text_chunks = get_text_chunks(raw_text)
                        vectorstore = get_vectorstore(text_chunks)
                        
                        # Buat conversation chain
                        st.session_state.conversation = get_conversation_chain(vectorstore)
                        
                        # Set status PDF processed
                        st.session_state.pdf_processed = True
                        st.session_state.pdf_process_time = datetime.datetime.now().strftime("%H:%M:%S")
                        
                        # Reset chat history untuk memulai percakapan baru
                        st.session_state.chat_history = None
                        
                        # Tampilkan pesan sukses
                        success_msg = f"""
                        <div class="chat-message bot" style="animation: fadeIn 1s ease-in-out;">
                            <div class="avatar">
                                <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png">
                            </div>
                            <div class="message">
                                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                                    <div style="font-weight: 600; color: #D2B48C; margin-right: 8px;">AI Assistant</div>
                                    <div style="height: 8px; width: 8px; background-color: #4CAF50; border-radius: 50%;"></div>
                                </div>
                                <p>✅ Dokumen berhasil diproses!</p>
                                <p>Saya telah mempelajari konten dari {len(pdf_names)} dokumen PDF:</p>
                                <ul>
                                    {"".join([f"<li>{name}</li>" for name in pdf_names])}
                                </ul>
                                <p>Silakan ajukan pertanyaan tentang dokumen-dokumen tersebut.</p>
                                <div class="timestamp">{datetime.datetime.now().strftime("%H:%M:%S")}</div>
                            </div>
                        </div>
                        """
                        # Reset chat placeholder dan tampilkan pesan sukses
                        if st.session_state.chat_placeholder:
                            st.session_state.chat_placeholder.empty()
                        st.session_state.chat_placeholder = chat_container.container()
                        st.session_state.chat_placeholder.markdown(success_msg, unsafe_allow_html=True)
                        
                        # Gunakan rerun dengan aman
                        st.rerun()
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {str(e)}")
            else:
                st.warning("⚠️ Silakan upload file PDF terlebih dahulu!")
                
        # Add information section at the bottom of sidebar
        st.markdown("""<div style="border-top: 1px solid rgba(210, 180, 140, 0.3); margin: 20px 0;"></div>""", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(93, 64, 55, 0.4); padding:12px; border-radius:8px; margin-top:15px;">
            <p style="color:#D2B48C; font-size:14px; font-weight:500; margin-bottom:8px;">Tentang PDF Chat Assistant</p>
            <p style="color:#FFF8DC; font-size:12px; margin-bottom:5px;">Aplikasi ini menggunakan teknologi AI untuk membantu Anda menganalisis dan mendapatkan informasi dari dokumen PDF.</p>
            <p style="color:#FFF8DC; font-size:12px;">Ditenagai oleh LangChain dan OpenAI.</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
