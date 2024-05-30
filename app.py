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
        if run_check.status in ['queued', 'in_progress']:
            time.sleep(2)
        else:
            break
    return run

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

# OpenAI API 클라이언트 생성
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)

    # 메모리 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = None
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

    # Assistant 및 Thread 생성
    if st.session_state.assistant_id is None or st.session_state.thread_id is None:
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

    # 저장된 메시지 표시
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 사용자 입력 처리
    user_prompt = st.chat_input("질문을 입력하세요")
    if user_prompt:
        # 사용자 메시지 저장 및 표시
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # 챗봇 응답 생성 및 표시
        chatbot_response = chatbot(user_prompt, client, st.session_state.assistant_id, st.session_state.thread_id)
        st.session_state.messages.append({"role": "assistant", "content": chatbot_response})
        with st.chat_message("assistant"):
            st.markdown(chatbot_response)

    # Clear 버튼
    if st.button("Clear"):
        # 기존 Thread 삭제
        if st.session_state.thread_id:
            client.beta.threads.delete(thread_id=st.session_state.thread_id)
        # 새로운 Assistant 및 Thread 생성
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

    # 대화창 나가기 버튼
    if st.button("Exit Chat"):
        # Thread 및 Assistant 삭제
        if st.session_state.thread_id:
            client.beta.threads.delete(thread_id=st.session_state.thread_id)
        if st.session_state.assistant_id:
            client.beta.assistants.delete(assistant_id=st.session_state.assistant_id)
        st.session_state.assistant_id = None
        st.session_state.thread_id = None
        st.session_state.messages = []
