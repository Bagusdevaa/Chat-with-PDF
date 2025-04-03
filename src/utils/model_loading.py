import os
from langchain.llms import HuggingFaceHub
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

def load_huggingface_model(model_name="hkunlp/instructor-xl"):
    model_path = os.path.join("models", "huggingface_model", model_name)
    llm = HuggingFaceHub(repo_id=model_path)
    return llm

def get_conversation_chain(vectorstore):
    llm = load_huggingface_model()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain