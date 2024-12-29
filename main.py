import streamlit as st
from chat_engine import ChatBot
import json

st.set_page_config(
    page_icon="🤖",
    page_title="Ask-Bot",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None
)

def initialize_session_state():
    if "chat_started" not in st.session_state:
        st.session_state.chat_started = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ChatBot(st.secrets["GROQ_API"])

initialize_session_state()

with st.sidebar:
    st.subheader("🅞🆇 Z 🅴🅴", divider="gray")
    st.write('chatbot : `langgraph & groq_inference`.')
    selected_model = st.selectbox(
        ":grey-background[LLM Model]", 
        options=list(ChatBot.AVAILABLE_MODELS.keys()),
        format_func=lambda x: ChatBot.AVAILABLE_MODELS[x],
        key="model_select"
    )
    
    if selected_model != st.session_state.chatbot.model_name:
        st.session_state.chatbot.update_model(selected_model)
    
    thread_id = st.text_input(":grey-background[Nom_Session_Chat]", value="001", key="thread_id")
    
    if not st.session_state.chat_started:
        if st.button("Démarrer la Session de Chat", use_container_width=True):
            st.session_state.chat_started = True
            st.session_state.messages = []
            st.rerun()
    else:
        if st.button("Terminer la Session de Chat", use_container_width=True, type="primary"):
            st.session_state.chat_started = False
            st.rerun()
        
        st.divider()
        
        with st.expander("Historique de la Session (JSON)", expanded=False):
            st.json(st.session_state.messages)
            
        #st.subheader("Suggestions de questions")
        suggestions = [
            "Tell me about Ethereum",
            "How to work with JSON in Python?",
            "Write a short poem"
        ]
        
        def set_input(suggestion):
            st.session_state.user_input = suggestion
            
        #for suggestion in suggestions:
        #    st.button(suggestion, on_click=set_input, args=(suggestion,), use_container_width=True)

st.subheader("၊၊||၊ :violet[Chat]🅱🅞🆃 ☰", divider="gray")

if st.session_state.chat_started:
    if not st.session_state.messages:
        hello_message = ":sparkles: Hello, How can I help you ?"
        st.session_state.messages = [{"role": "assistant", "content": hello_message}]
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is your message?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.session_state.chatbot.chat(prompt, thread_id)
            #st.markdown(response["messages"][-1].content)
            # stream
            response_content = response["messages"][-1].content
            response_str = ""
            response_container = st.empty()
            for token in response_content:
                response_str += token
                response_container.markdown(response_str)
            st.session_state.messages.append(
                {"role": "assistant", "content": response["messages"][-1].content}
            )
