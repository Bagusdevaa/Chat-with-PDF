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
    llm = ChatOpenAI(model="gpt-4.1-nano")
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    # Mengonfigurasi memory dengan output_key yang sesuai untuk ConversationalRetrievalChain
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
        output_key='answer'  # Menentukan output_key sesuai dengan kunci yang digunakan ConversationalRetrievalChain
    )
    
    # Mengonfigurasi retriever dengan parameter yang spesifik
    retriever = vectorstore.as_retriever(
        search_type="similarity",  # Menggunakan similarity search
        search_kwargs={"k": 5}     # Mengambil 5 dokumen paling relevan
    )
    
    # Buat custom prompt template yang sangat eksplisit tentang menggunakan konteks dari dokumen
    from langchain.prompts import PromptTemplate
    
    # Template untuk QA dengan history percakapan
    template = """
    Gunakan HANYA informasi berikut untuk menjawab pertanyaan pengguna.
    Jika Anda tidak tahu jawabannya berdasarkan informasi yang diberikan, katakan "Maaf, saya tidak menemukan informasi tentang itu dalam dokumen."
    JANGAN membuat informasi.
    SELALU gunakan informasi dari konteks untuk menjawab.
    
    Konteks dari dokumen:
    {context}
    
    History percakapan:
    {chat_history}
    
    Pertanyaan: {question}
    
    Jawaban berdasarkan konteks dokumen (jawab dalam bahasa yang sama dengan pertanyaan):
    """
    
    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context", "question", "chat_history"],
        template=template
    )
    
    # Mengonfigurasi ConversationalRetrievalChain dengan parameter yang lebih eksplisit
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,  # Mengembalikan dokumen sumber untuk debugging
        combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT},  # Menggunakan custom prompt
        chain_type="stuff",            # Menggunakan metode "stuff" untuk memasukkan konteks
        verbose=True                   # Output verbose untuk debugging
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    
    # Menambahkan pesan terbaru ke chat_history jika belum ada
    if st.session_state.chat_history is None:
        st.session_state.chat_history = []
        
    # Menambahkan pertanyaan user ke chat_history
    user_message = {"role": "user", "content": user_question}
    ai_message = {"role": "assistant", "content": response["answer"]}
    
    # Menambahkan pesan ke chat_history jika menggunakan format baru
    if not isinstance(st.session_state.chat_history, list):
        st.session_state.chat_history = []
    
    st.session_state.chat_history.append(user_message)
    st.session_state.chat_history.append(ai_message)
    
    # Tampilkan history percakapan
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            st.write(user_template.replace(
                "{{MSG}}", message["content"]), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message["content"]), unsafe_allow_html=True)
    
    # Tampilkan dokumen sumber yang digunakan (untuk debugging)
    if 'source_documents' in response and response['source_documents']:
        with st.expander("Dokumen Sumber"):
            for i, doc in enumerate(response['source_documents']):
                st.write(f"**Dokumen {i+1}**")
                st.write(doc.page_content)
                st.write("---")


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDFs",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)

if __name__ == '__main__':
    main()