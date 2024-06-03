import streamlit as st
import openai

# OpenAI API 호출을 위한 함수
@st.cache_data
def get_openai_response(api_key, prompt):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

# 세션 상태에 API Key 저장
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

# API Key 입력
st.title("GPT-3.5 Turbo Chatbot")
st.session_state.api_key = st.text_input("Enter your OpenAI API Key", type="password", value=st.session_state.api_key)

# 질문 입력
prompt = st.text_area("Enter your question:")

# 응답 표시
if st.button("Get Response"):
    if st.session_state.api_key and prompt:
        response = get_openai_response(st.session_state.api_key, prompt)
        st.text_area("Response:", value=response, height=200)
    else:
        st.error("Please enter both the API Key and a question.")
