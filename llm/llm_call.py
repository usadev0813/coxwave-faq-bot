# 스트리밍용 GPT API 호출 함수
import openai

async def stream_gpt_response(messages):
    try:
        # ChatCompletion API 사용
        stream = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400,
            temperature=0.3,
            stream=True,
        )

        async for chunk in stream:
            if "choices" in chunk and chunk["choices"][0].get("delta", {}).get("content"):
                yield chunk["choices"][0]["delta"]["content"]
    except Exception as e:
        yield f"GPT API 호출 중 오류가 발생했습니다: {str(e)}"