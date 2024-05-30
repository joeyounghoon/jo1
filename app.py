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

# 저장한 메시지 사용자/응답 구분해서 보여주기
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력과 LLM 응답
if prompt := st.chat_input("What is up?"):
    # 사용자 메시지 보여주기
    st.chat_message("user").markdown(prompt)
    # 메모리에 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": prompt})

    # OpenAI API를 통한 응답 생성
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password", key="api_key")
    if openai_api_key:
        response = chatbot(prompt, openai_api_key)
    else:
        response = "API Key가 필요합니다."

    # LLM 응답 보여주기
    with st.chat_message("assistant"):
        st.markdown(response)
    # 메모리에 LLM 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": response})
