import streamlit as st
from openai import OpenAI

# OpenAI API Key를 입력 받는 함수
def get_openai_api_key():
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    return api_key

# OpenAI API 인증 함수
@st.cache(allow_output_mutation=True)
def authenticate_openai(api_key):
    openai.api_key = api_key

# GPT-3.5 Turbo 모델을 사용하여 응답 생성하는 함수
@st.cache(allow_output_mutation=True)
def generate_response(question):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=question,
        max_tokens=50
    )
    return response.choices[0].text.strip()

def main():
    st.title("GPT-3.5 Turbo Q&A App")

    # 세션 상태에서 OpenAI API Key 가져오기
    session_state = st.session_state
    if 'api_key' not in session_state:
        session_state.api_key = get_openai_api_key()

    # OpenAI API Key가 없을 경우, 애플리케이션 종료
    if not session_state.api_key:
        st.warning("Please enter your OpenAI API Key.")
        st.stop()

    # OpenAI API 인증
    authenticate_openai(session_state.api_key)

    # 질문 입력 받기
    question = st.text_input("Enter your question:")

    if question:
        # GPT-3.5 Turbo 모델을 사용하여 응답 생성
        response = generate_response(question)
        st.write("AI's response:")
        st.write(response)

if __name__ == "__main__":
    main()
