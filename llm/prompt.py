base_prompt = """
### 컨텍스트
당신은 스마트 스토어 FAQ를 위한 챗봇입니다. 아래 FAQ 답변을 참고하여 사용자에게 친절하고 정확한 답변을 제공합니다. 
FAQ 답변과 관련된 후속 질문을 두 가지 이상 포함시켜 사용자가 추가로 궁금해할만한 내용을 제안합니다.
"""

fallback_base_prompt = """
### 컨텍스트
해당 질문은 스마트스토어 FAQ와 직접적인 연관성이 낮습니다. 
스마트 스토어 FAQ를 위한 챗봇임을 안내 후 FAQ 답변과 관련된 후속 질문을 두 가지 이상 포함시켜 사용자가 추가로 궁금해할만한 내용을 제안합니다.
"""


def generate_prompt(user_query, faq_answers):
    faq_text = "\n".join([f"{i + 1}. {answer}" for i, answer in enumerate(faq_answers)])
    return (
        f"""
        ### 사용자 입력
        사용자 질문: {user_query}
        
        FAQ 답변:
        {faq_text}
        
        {{챗봇답변}}
        
        - {{후속질문1}}
        - {{후속질문2}}
        """
    )


def generate_fallback_prompt(user_query, faq_answers):
    faq_text = "\n".join([f"{i + 1}. {answer}" for i, answer in enumerate(faq_answers)])
    return (
        f"""    
        ### 사용자 입력
        사용자 질문: {user_query}
        
        FAQ 답변:
        {faq_text}
        
        {{챗봇답변}}
        
        - {{후속질문1}}
        - {{후속질문2}}
        """
    )
