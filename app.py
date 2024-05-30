import streamlit as st
from openai import OpenAI
import time

# Function to run and wait for a run to complete
def run_and_wait(client, assistant_id, thread_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    while True:
        run_check = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run_check.status in ['queued', 'in_progress']:
            time.sleep(2)
        else:
            break
    return run

# Function to interact with the chatbot
def chatbot(user_input, client, assistant_id, thread_id):
    thread = client.beta.threads.retrieve(thread_id=thread_id)
    messages = thread.messages + [{"role": "user", "content": user_input}]
    client.beta.threads.update(
        thread_id=thread_id,
        messages=messages
    )
    run = run_and_wait(client, assistant_id, thread_id)
    thread_messages = client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id)
    response_text = thread_messages.data[-1].content[0].text.value
    return response_text

# Streamlit UI
st.title("LLM 기반 챗봇")

openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
    
    # Initializing session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = None
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

    # Create Assistant and Thread if not already created
    if st.session_state.assistant_id is None or st.session_state.thread_id is None:
        try:
            assistant = client.beta.assistants.create(
                name="데이터 분석 전문가",
                description="당신은 데이터 분석 전문가입니다.",
                model="gpt-4-turbo-preview",
            )
            st.session_state.assistant_id = assistant.id
        except Exception as e:
            st.error(f"Error creating assistant: {e}")
        
        try:
            thread = client.beta.threads.create(
                assistant_id=st.session_state.assistant_id,
                messages=[]
            )
            st.session_state.thread_id = thread.id
        except Exception as e:
            st.error(f"Error creating thread: {e}")

    # Display stored messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Process user input
    user_prompt = st.chat_input("질문을 입력하세요")
    if user_prompt:
        # Store and display user message
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Generate and display chatbot response
        try:
            chatbot_response = chatbot(user_prompt, client, st.session_state.assistant_id, st.session_state.thread_id)
            st.session_state.messages.append({"role": "assistant", "content": chatbot_response})
            with st.chat_message("assistant"):
                st.markdown(chatbot_response)
        except Exception as e:
            st.error(f"Error generating response: {e}")

    # Clear button
    if st.button("Clear"):
        if st.session_state.thread_id:
            try:
                client.beta.threads.delete(thread_id=st.session_state.thread_id)
            except Exception as e:
                st.error(f"Error deleting thread: {e}")
        try:
            assistant = client.beta.assistants.create(
                name="데이터 분석 전문가",
                description="당신은 데이터 분석 전문가입니다.",
                model="gpt-4-turbo-preview",
            )
            thread = client.beta.threads.create(
                assistant_id=assistant.id,
                messages=[]
            )
            st.session_state.assistant_id = assistant.id
            st.session_state.thread_id = thread.id
            st.session_state.messages = []
        except Exception as e:
            st.error(f"Error creating new assistant or thread: {e}")

    # Exit Chat button
    if st.button("Exit Chat"):
        if st.session_state.thread_id:
            try:
                client.beta.threads.delete(thread_id=st.session_state.thread_id)
            except Exception as e:
                st.error(f"Error deleting thread: {e}")
        if st.session_state.assistant_id:
            try:
                client.beta.assistants.delete(assistant_id=st.session_state.assistant_id)
            except Exception as e:
                st.error(f"Error deleting assistant: {e}")
        st.session_state.assistant_id = None
        st.session_state.thread_id = None
        st.session_state.messages = []
