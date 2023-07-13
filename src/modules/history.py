import os
import streamlit as st
from streamlit_chat import message

class ChatHistory:

    def __init__(self):
        self.history = st.session_state.get("history", [])
        st.session_state["history"] = self.history

    def defaultGreeting(self):
        return "Hey! 👋"
    
    def defaultPrompt(self, topic):
        return f"Hello! Ask me anything about {topic}!"

    def initializeUserHistory(self):
        st.session_state["user"] = [self.defaultGreeting()]
    
    def initializeAssistantHistory(self, uploadedFile):
        st.session_state["assistant"] = [self.defaultPrompt(uploadedFile.name)]

    def initialize(self, uploadedFile):
        if "user" not in st.session_state:
            self.initializeUserHistory()
        if "assistant" not in st.session_state:
            self.initializeAssistantHistory(uploadedFile)

    def reset(self, uploadedFile):
        st.session_state["history"] = []

        self.initializeUserHistory()
        self.initializeAssistantHistory(uploadedFile)
        st.session_state["reset_chat"] = False

    def append(self, mode, message):
        st.session_state[mode].append(message)

    def generateMessages(self, container):
        if st.session_state["assistant"]:
            with container:
                for i in range(len(st.session_state["assistant"])):
                    message(
                        st.session_state["user"][i],
                        is_user=True,
                        key=f"history_{i}_user",
                        avatar_style="big-smile"
                    )
                    message(
                        st.session_state["assistant"][i],
                        key=str(i),
                        avatar_style="thumbs"
                    )
    
    def load(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                self.history = f.read().splitlines()

    def save(self):
        with open(self.history_file, "w") as f:
            f.write("\n".join(self.history))
