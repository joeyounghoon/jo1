import streamlit as st
from openai import OpenAI
import time

# OpenAI API 함수
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
        if run_check.status in ['queued', 'in_progress']:
            time.sleep(2)
        else:
            break
    return run

def chatbot(user_input, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    assistant = client.beta.assistants.create(
        name="데이터 분석 전문가",
        description="당신은 데이터 분석 전문가입니다.",
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

# 메모리 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit UI
st.title("LLM 기반 챗봇")

openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

if openai_api_key:
    user_prompt = st.chat_input("질문을 입력하세요")

    if user_prompt:
        # 사용자 메시지 저장 및 표시
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        
        # OpenAI API를 통한 응답 생성
        chatbot_response = chatbot(user_prompt, openai_api_key)
        
        # 챗봇 응답 저장 및 표시
        st.session_state.messages.append({"role": "assistant", "content": chatbot_response})
        with st.chat_message("assistant"):
            st.markdown(chatbot_response)

# 저장된 메시지를 순회하면서 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
