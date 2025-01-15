# 스트리밍용 GPT API 호출 함수
import openai
from typing import AsyncGenerator, List

from llm.prompt import summarize_prompt
from rag.conversation_memory import ConversationMemory


async def stream_gpt_call(messages: List[dict], memory: ConversationMemory, user_message: str):
    """
    GPT 스트리밍 응답을 처리하고 메모리에 저장하는 함수.
    """
    try:
        # ChatCompletion API 사용
        stream = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.3,
            stream=True,
        )
        gpt_response = ""

        async for chunk in stream:
            if "choices" in chunk and chunk["choices"][0].get("delta", {}).get("content"):
                content = chunk["choices"][0]["delta"]["content"]
                gpt_response += content
                yield content

        # 대화 요약 생성 및 메모리에 저장
        summary_conversation = _generate_conversation_summary(user_message, gpt_response)
        memory.add_message(user_message, gpt_response, summary_conversation)
    except Exception as e:
        error_message = f"GPT API 호출 중 오류가 발생했습니다: {str(e)}"
        yield error_message


def _generate_conversation_summary(user_message: str, ai_message: str) -> str:
    """
    사용자와 AI 간 대화를 요약하는 함수.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": summarize_prompt()},
                {"role": "user", "content": f"User: {user_message}, AI: {ai_message}"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"요약 생성 중 오류가 발생했습니다: {str(e)}"
