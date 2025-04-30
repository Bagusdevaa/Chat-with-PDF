import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
from datetime import datetime

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
    # embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-xl")
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


def display_chat_history():
    """Fungsi khusus untuk menampilkan riwayat chat."""
    if st.session_state.chat_history is None:
        return
        
    # Buat container untuk semua pesan chat
    chat_container = st.container()
    
    with chat_container:
        # Tambahkan div container di awal
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for i, message in enumerate(st.session_state.chat_history):
            # Format waktu saat ini
            current_time = datetime.now().strftime("%H:%M")
            
            if i % 2 == 0:
                st.markdown(
                    user_template.replace("{{MSG}}", message.content).replace("{{TIME}}", current_time),
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    bot_template.replace("{{MSG}}", message.content).replace("{{TIME}}", current_time),
                    unsafe_allow_html=True
                )
        
        # Tutup container
        st.markdown('</div>', unsafe_allow_html=True)


def handle_userinput(user_question):
    """Fungsi untuk menangani pertanyaan pengguna."""
    if user_question:
        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history']
        display_chat_history()


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDFs",
                       page_icon=":books:",
                       layout="wide")  # Untuk tampilan yang lebih lebar
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    # Layout dengan dua kolom
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat with multiple PDFs")
        
        # Container untuk pesan
        display_chat_history()  # Menampilkan riwayat tanpa perlu parameter None
            
        # Input pengguna di bagian bawah
        user_question = st.text_input("Ask a question about your documents:", key="question_input")
        if user_question:
            handle_userinput(user_question)
            # Reset input field setelah pertanyaan dikirim
            st.session_state.question_input = ""

    with col2:
        st.subheader("📄 Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        
        if st.button("Process Documents"):
            if pdf_docs:
                with st.spinner("Processing documents..."):
                    # get pdf text
                    raw_text = get_pdf_text(pdf_docs)
                    st.success(f"Successfully processed {len(pdf_docs)} document(s)")
                    
                    # get the text chunks
                    text_chunks = get_text_chunks(raw_text)
                    st.info(f"Created {len(text_chunks)} text chunks")

                    # create vector store
                    with st.spinner("Creating vector store..."):
                        vectorstore = get_vectorstore(text_chunks)
                        st.success("Vector store created!")

                    # create conversation chain
                    st.session_state.conversation = get_conversation_chain(vectorstore)
                    st.success("Ready to chat! Ask a question on the left.")
            else:
                st.error("Please upload at least one PDF document")


if __name__ == '__main__':
    main()