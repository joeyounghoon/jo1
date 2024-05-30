import streamlit as st
from openai import OpenAI
import time

def run_and_wait(client, assistant, thread):
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    while True:
        run_check = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(run_check.status)
        if run_check.status in ['queued', 'in_progress']:
            time.sleep(2)
        else:
            break
    return run

def chatbot(user_input, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    assistant = client.beta.assistants.create(
        name="챗봇",
        description="당신은 챗봇입니다.",
        model="gpt-4-turbo-preview",
    )
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ]
    )
    run = run_and_wait(client, assistant, thread)
    thread_messages = client.beta.threads.messages.list(thread.id, run_id=run.id)
    response_text = thread_messages.data[-1].content[0].text.value
    return response_text

# Streamlit UI
st.title("LLM 기반 챗봇")

openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

if openai_api_key:
    user_prompt = st.text_input("질문을 입력하세요")

    if user_prompt:
        chatbot_response = chatbot(user_prompt, openai_api_key)
        st.write("Chatbot Response:")
        st.write(chatbot_response)
