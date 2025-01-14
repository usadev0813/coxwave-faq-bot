# 스트리밍용 GPT API 호출 함수
import openai


async def stream_gpt_response(messages, memory, user_message):
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
                yield chunk["choices"][0]["delta"]["content"]

        memory.add_message(user_message, gpt_response)
    except Exception as e:
        error_message = f"GPT API 호출 중 오류가 발생했습니다: {str(e)}"
        yield error_message
        memory.add_message(user_message, error_message)
