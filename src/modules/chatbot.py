import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks import get_openai_callback

class Chatbot:

    def __init__(self, model_name, temperature, vectors):
        """
        Método construtor que inicializa algumas variáveis do chat.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.vectors = vectors

    qaTemplate = """
        You are a helpful AI assistant named Robby. The user gives you a file its content is represented by the following pieces of context, use them to answer the question at the end.
        If you don't know the answer, just say you don't know. Do NOT try to make up an answer.
        If the question is not related to the context, politely respond that you are tuned to only answer questions that are related to the context.
        Use as much detail as possible when responding.

        context: {context}
        =========
        question: {question}
        ======
        """
    
    qaPrompt = PromptTemplate(template=qaTemplate, input_variables=["context", "question"])

    def conversationalChat(self, query):
        """
        Cria um chat usando a biblioteca LangChain
        """
        llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)

        retriever = self.vectors.as_retriever()

        chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, combine_docs_chain_kwargs={'prompt': self.qaPrompt})

        chainInput = {"question": query, "chat_history": st.session_state["history"]}
        result = chain(chainInput)

        st.session_state["history"].append((query, result["answer"]))
        return result["answer"]