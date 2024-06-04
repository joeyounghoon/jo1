# jo1
import streamlit as st
import openai
from PIL import Image
from io import BytesIO
import requests

# 함수: OpenAI API 호출을 통한 텍스트 응답 생성
@st.cache_data
def get_openai_text_response(api_key, prompt):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

# 함수: OpenAI API 호출을 통한 이미지 생성
@st.cache_data
def get_openai_image_response(api_key, prompt):
    openai.api_key = api_key
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    image_response = requests.get(image_url)
    return Image.open(BytesIO(image_response.content))

# 세션 상태 초기화
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'text_prompt' not in st.session_state:
    st.session_state.text_prompt = ''
if 'image_prompt' not in st.session_state:
    st.session_state.image_prompt = ''

# API Key 입력
st.sidebar.title("Settings")
st.session_state.api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password", value=st.session_state.api_key)

# 페이지 선택
page = st.sidebar.selectbox("Select a Page", ["Chat with GPT-3.5", "Generate Image with Dall-E"])

if page == "Chat with GPT-3.5":
    st.title("GPT-3.5 Turbo Chatbot")
    
    # 질문 입력
    st.session_state.text_prompt = st.text_area("Enter your question:", value=st.session_state.text_prompt)
    
    # 응답 표시
    if st.button("Get Response"):
        if st.session_state.api_key and st.session_state.text_prompt:
            response = get_openai_text_response(st.session_state.api_key, st.session_state.text_prompt)
            st.text_area("Response:", value=response, height=200)
        else:
            st.error("Please enter both the API Key and a question.")

elif page == "Generate Image with Dall-E":
    st.title("Dall-E Image Generator")
    
    # 프롬프트 입력
    st.session_state.image_prompt = st.text_area("Enter your prompt for image generation:", value=st.session_state.image_prompt)
    
    # 이미지 생성 및 표시
    if st.button("Generate Image"):
        if st.session_state.api_key and st.session_state.image_prompt:
            image = get_openai_image_response(st.session_state.api_key, st.session_state.image_prompt)
            st.image(image, caption="Generated by Dall-E", use_column_width=True)
        else:
            st.error("Please enter both the API Key and a prompt for image generation.")
