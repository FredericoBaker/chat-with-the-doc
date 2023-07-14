import os
import streamlit as st
from io import StringIO
import re
import sys
from modules.history import ChatHistory
from modules.layout import Layout
from modules.utilities import Utilities
from modules.sidebar import Sidebar

def reloadModule(moduleName):
    import importlib
    import sys
    if moduleName in sys.modules:
        importlib.reload(sys.modules[moduleName])
    return sys.modules[moduleName]

historyModule = reloadModule('modules.history')
layoutModule = reloadModule('modules.layout')
utilitiesModule = reloadModule('modules.utilities')
sidebarModule = reloadModule('modules.sidebar')

ChatHistory = historyModule.ChatHistory
Layout = layoutModule.Layout
Utilities = utilitiesModule.Utilities
Sidebar = sidebarModule.Sidebar

st.set_page_config(layout="wide", page_icon="📧", page_title="Chat with your gmail")

layout, sidebar, utilities = Layout(), Sidebar(), Utilities()

st.markdown("<h1 style='text-align: center;'> Ask anything about your gmail messages!</h1>", unsafe_allow_html=True)

userApiKey = utilities.loadApiKey()

if not userApiKey:
    layout.show_api_key_missing()
else:
    os.environ["OPENAI_API_KEY"] = userApiKey
    uploadedFile = utilities.loadGmailMessages()
    fileContainer = st.expander("Your email messages:")
    fileContainer.write(uploadedFile)

    if uploadedFile:
        sidebar.show_options()

        history = ChatHistory()
        try:
            chatbot = utilities.setupEmailChatbot('email_data.json', st.session_state["model"], st.session_state["temperature"])
            st.session_state["chatbot"] = chatbot

            if st.session_state["ready"]:
                responseContainer, promptContainer = st.container(), st.container()

                with promptContainer:
                    isReady, userInput = layout.prompt_form_email()

                    history.initialize('email_data.json')

                    if st.session_state["reset_chat"]:
                        history.reset('email_data.json')
                    
                    if isReady:
                        history.append("user", userInput)

                        old_stdout = sys.stdout
                        sys.stdout = captured_output = StringIO()

                        output = st.session_state["chatbot"].conversationalChat(userInput)

                        sys.stdout = old_stdout

                        history.append("assistant", output)
                
                history.generateMessages(responseContainer)

        except Exception as e:
            st.error(f"Error: {str(e)}")