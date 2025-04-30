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
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        # Dapatkan waktu saat ini untuk setiap pesan
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content).replace("{{TIME}}", current_time), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content).replace("{{TIME}}", current_time), unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDFs",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "pdf_processed" not in st.session_state:
        st.session_state.pdf_processed = False
    if "pdf_process_time" not in st.session_state:
        st.session_state.pdf_process_time = ""

    # Tampilkan tanggal dan waktu saat ini
    current_datetime = datetime.datetime.now()
    formatted_date = current_datetime.strftime("%A, %d %B %Y")
    formatted_time = current_datetime.strftime("%H:%M:%S")
    
    # Menampilkan header yang lebih menarik dengan tema coklat dan tanggal dan waktu
    st.markdown(f"""
    <div style="background-color:#5D4037; padding:10px; border-radius:10px; margin-bottom:20px">
        <h1 style="color:#FFF8DC; text-align:center">📚 PDF Chat Assistant 📚</h1>
        <p style="color:#D2B48C; text-align:center; font-size:16px">{formatted_date} | {formatted_time}</p>
    </div>
    """, unsafe_allow_html=True)
    
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.markdown("""
        <div style="background-color:#8D6E63; padding:5px; border-radius:5px; margin-bottom:10px">
            <h3 style="color:#FFF8DC; text-align:center">Your Documents</h3>
        </div>
        """, unsafe_allow_html=True)
        
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        
        process_btn = st.button("Process", type="primary")
        
        # Tampilkan notifikasi sukses di sidebar jika PDF telah diproses
        if st.session_state.pdf_processed:
            st.markdown(
                pdf_success_template.replace("{{TIME}}", st.session_state.pdf_process_time),
                unsafe_allow_html=True
            )
            
        if process_btn:
            if pdf_docs:
                with st.spinner("Processing your documents..."):
                    # get pdf text
                    raw_text = get_pdf_text(pdf_docs)

                    # get the text chunks
                    text_chunks = get_text_chunks(raw_text)

                    # create vector store
                    vectorstore = get_vectorstore(text_chunks)

                    # create conversation chain
                    st.session_state.conversation = get_conversation_chain(
                        vectorstore)
                    
                    # Set status PDF processed ke True
                    st.session_state.pdf_processed = True
                    
                    # Simpan waktu proses selesai
                    st.session_state.pdf_process_time = datetime.datetime.now().strftime("%H:%M:%S")
            else:
                st.warning("⚠️ Silakan upload file PDF terlebih dahulu!")


if __name__ == '__main__':
    main()
