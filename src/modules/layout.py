import streamlit as st

class Layout:
    
    def show_header(self, types_files):
        st.markdown(
            f"""
            <h1 style='text-align: center;'> Ask anything about your {types_files} files!</h1>
            """,
            unsafe_allow_html=True,
        )
        

    def show_api_key_missing(self):
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>Enter your <a href="https://platform.openai.com/account/api-keys" target="_blank">OpenAI API key</a> on the sidebar to start chatting.</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def prompt_form(self):
        with st.form(key="my_form", clear_on_submit=True):
            user_input = st.text_area(
                "Query:",
                placeholder="Ask me anything about the document...",
                key="input",
                label_visibility="collapsed",
            )
            submit_button = st.form_submit_button(label="Send")
            
            is_ready = submit_button and user_input
        return is_ready, user_input
    
    def prompt_form_email(self):
        with st.form(key="my_form_email", clear_on_submit=True):
            user_input = st.text_area(
                "Query:",
                placeholder="Ask me anything about your email...",
                key="input",
                label_visibility="collapsed",
            )
            submit_button = st.form_submit_button(label="Send")
            
            is_ready = submit_button and user_input
        return is_ready, user_input
    
