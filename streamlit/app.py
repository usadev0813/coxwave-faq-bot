import streamlit as st
import httpx

# Streamlit 앱 제목
st.title("네이버 스마트스토어 FAQ 기반 Chatbot")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# FastAPI 백엔드 URL 설정
BACKEND_API_URL = st.secrets["BACKEND_API_URL"]

# 기존 대화 표시
if st.session_state.messages:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자가 입력한 질문 처리
if user_query := st.chat_input("무엇을 도와드릴까요?"):
    # 사용자 입력 저장 및 화면 업데이트
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Assistant의 응답 처리
    with st.chat_message("assistant"):
        # 실시간 업데이트를 위한 Streamlit 컨테이너 생성
        message_container = st.empty()
        full_response = ""

        try:
            # FastAPI 스트리밍 API 호출
            with httpx.stream("POST", f"{BACKEND_API_URL}/query/stream", json={"query": user_query}) as response:
                for chunk in response.iter_text():
                    if chunk:
                        # 실시간으로 응답 데이터를 화면에 업데이트
                        full_response += chunk
                        message_container.markdown(full_response)

            # 최종 응답을 세션 상태에 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            error_message = f":warning: 오류가 발생했습니다: {e}"
            st.markdown(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
