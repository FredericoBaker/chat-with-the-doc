import os
import pandas as pd
import streamlit as st
import pdfplumber

from modules.chatbot import Chatbot
from modules.embedder import Embedder

class Utilities:

    @staticmethod
    def loadApiKey():
        if not hasattr(st.session_state, "api_key"):
            st.session_state.api_key = None

        if os.path.exists(".env") and os.environ.get("OPENAI_API_KEY") is not None:
            userApiKey = os.environ["OPENAI_API_KEY"]
            st.sidebar.success("API key loaded from .env")
        else:
            if st.session_state.api_key is not None:
                userApiKey = st.session_state.api_key
                st.sidebar.success("API key loaded from previous input")
            else:
                userApiKey = st.sidebar.text_input(label="Your OpenAI API key", placeholder="sk-...", type="password")
                if userApiKey:
                    st.session_state.api_key = userApiKey

        return userApiKey
    
    @staticmethod
    def handleUpload(fileTypes):
        uploadedFile = st.sidebar.file_uploader("upload", type=fileTypes, label_visibility="collapsed")
        if uploadedFile is not None:
            def showCSVFile(uploadedFile):
                fileContainer = st.expander("Your CSV file: ")
                uploadedFile.seek(0)
                shows = pd.read_csv(uploadedFile)
                fileContainer.write(shows)

            def showPDFFile(uploadedFile):
                fileContainer = st.expander("Your PDF file: ")
                with pdfplumber.open(uploadedFile) as pdf:
                    pdfText = ""
                    for page in pdf.pages:
                        pdfText += page.extract_text() + "\n\n"
                fileContainer.write(pdfText)

            def showTXTFile(uploadedFile):
                fileContainer = st.expander("Your TXT file:")
                uploadedFile.seek(0)
                content = uploadedFile.read().decode("utf-8")
                fileContainer.write(content)

            # Pode dar problema -> Qualquer coisa procurar como ler json
            def showJSONFile(uploadedFile):
                fileContainer = st.expander("Your JSON file:")
                uploadedFile.seek(0)
                content = uploadedFile.read().decode("utf-8")
                fileContainer.write(content)

            def getFileExtension(uploadedFile):
                return os.path.splitext(uploadedFile)[1].lower()
            
            fileExtension = getFileExtension(uploadedFile.name)

            if fileExtension == ".csv":
                showCSVFile(uploadedFile)
            if fileExtension == ".pdf":
                showPDFFile(uploadedFile)
            if fileExtension == ".txt":
                showTXTFile(uploadedFile)
            if fileExtension == ".json":
                showJSONFile(uploadedFile)

        else:
            st.session_state["reset_chat"] = True
        
        return uploadedFile
    
    @staticmethod
    def setupChatbot(uploadedFile, model, temperature):
        embeddings = Embedder()

        with st.spinner("Processing..."):
            uploadedFile.seek(0)
            file = uploadedFile.read()
            vectors = embeddings.getDocEmbeddings(file, uploadedFile.name)
            chatbot = Chatbot(model, temperature, vectors)
            
        st.session_state["ready"] = True

        return chatbot