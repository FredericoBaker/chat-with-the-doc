import os
import pandas as pd
import streamlit as st
import pdfplumber
import base64
import datetime
import json

import google.auth
from oauth2client import client
from oauth2client import tools
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from modules.chatbot import Chatbot
from modules.emailChatbot import EmailChatbot
from modules.embedder import Embedder
from modules.emailEmbedder import EmailEmbedder

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
                st.sidebar.success("API key loaded!")
            else:
                userApiKey = st.sidebar.text_input(label="Your OpenAI API key", placeholder="sk-...", type="password")
                if userApiKey:
                    st.session_state.api_key = userApiKey

        return userApiKey

    
    @staticmethod
    def loadGmailMessages():
        def connectGmail():
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            creds = None

            if os.path.exists('gmail_credentials/token.json'):
                creds = Credentials.from_authorized_user_file('gmail_credentials/token.json', SCOPES)
                st.sidebar.success("Gmail already connected!")
                return creds
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    connectGmailButton = st.sidebar.button("Connect gmail account")
                    if connectGmailButton:
                        #flow = InstalledAppFlow.from_client_secrets_file('gmail_credentials/credentials.json', SCOPES)
                        #creds = flow.run_local_server(port=0)
                        flow = client.flow_from_clientsecrets('gmail_credentials/credentials.json', SCOPES)
                        creds = tools.run_flow(flow=flow)
                        st.sidebar.success("Gmail connected!")
                        # Save the credentials for the next run
                        with open('gmail_credentials/token.json', 'w') as token:
                            token.write(creds.to_json())
                        return creds
                    
        def get_sender(messagedata):
            for header in messagedata['payload']['headers']:
                if header['name'] == 'From':
                    return header['value']

        def get_date(messagedata):
            for header in messagedata['payload']['headers']:
                if header['name'] == 'Date':
                    return header['value']
                
        def get_subject(messagedata):
            for header in messagedata['payload']['headers']:
                if header['name'] == 'Subject':
                    return header['value']

        def get_body(messagedata):
            if 'parts' in messagedata['payload']:
                if messagedata['payload']['parts'][0]['mimeType'] == 'multipart/alternative':
                    body_raw = messagedata['payload']['parts'][0]['parts'][0]['body']['data']    
                else:
                    body_raw = messagedata['payload']['parts'][0]['body']['data']   
            else:
                body_raw = messagedata['payload']['body']['data']

            body = base64.urlsafe_b64decode(body_raw).decode("utf-8")
            return body
                    
        creds = connectGmail()

        try:
            service = build('gmail', 'v1', credentials=creds)
            data = {}
            data['emailAddress'] = service.users().getProfile(userId='me').execute()['emailAddress']
            data['extractionDate'] = str(datetime.datetime.now())
            data['emailCount'] = 0
            data['messages'] = []

            today = datetime.datetime.today().strftime('%Y/%m/%d')
            delta = datetime.timedelta(days = 60)
            sixtyDaysAgo = (datetime.datetime.today() - delta).strftime('%Y/%m/%d')

            messages = service.users().messages().list(userId='me', q=f'after:{str(sixtyDaysAgo)} before:{str(today)}').execute().get('messages', [])

            for message in messages:
                messagedata = service.users().messages().get(userId='me', id=message['id']).execute()
                sender = get_sender(messagedata)
                date = get_date(messagedata)
                subject = get_subject(messagedata)
                body = get_body(messagedata)

                messagedata = {}
                messagedata['sender'] = sender
                messagedata['date'] = date
                messagedata['subject'] = subject
                messagedata['body'] = body

                data['messages'].append(messagedata)
                data['emailCount'] += 1

            with open('email_data.json', 'w') as outfile:
                json.dump(data, outfile)
            
            return data
        except HttpError as e:
            st.sidebar.error(str(e))

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
    
    @staticmethod
    def setupEmailChatbot(uploadedFileName, model, temperature):
        embeddings = EmailEmbedder()

        with st.spinner("Processing..."):
            vectors = embeddings.getDocEmbeddings(uploadedFileName)
            chatbot = EmailChatbot(model, temperature, vectors)
            
        st.session_state["ready"] = True

        return chatbot