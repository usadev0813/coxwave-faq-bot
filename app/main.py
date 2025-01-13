import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv
import openai

from llm.llm_call import stream_gpt_response
from llm.prompt import generate_prompt, generate_fallback_prompt, base_prompt, fallback_base_prompt
from rag.chroma import get_chroma_client, get_or_create_collection, query_chroma

# 환경 변수 로드
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

# FastAPI 애플리케이션 초기화
app = FastAPI()

# ChromaDB 클라이언트 및 컬렉션 설정
client = get_chroma_client()
collection_name = os.getenv("COLLECTION_NAME")
if not collection_name:
    raise ValueError("COLLECTION_NAME 환경 변수가 설정되지 않았습니다.")
collection = get_or_create_collection(client, collection_name)


# 스트리밍 기반 RAG API 엔드포인트
@app.post("/query/stream")
async def query_stream(request: Request):
    body = await request.json()
    user_query = body.get("query", "")

    if not user_query:
        return JSONResponse(content={"message": "쿼리 내용을 입력해주세요."}, status_code=400)

    # 벡터DB에서 상위 3개 검색결과 가져오기
    result = query_chroma(collection, user_query, n_results=3)

    if result:
        valid_results = [res for res in result if res["similarity_score"] >= 0.3]

        if valid_results:
            faq_answers = [res["content"] for res in valid_results]
            prompt = generate_prompt(user_query, faq_answers)

            # ChatCompletion 메시지 생성
            messages = [
                {"role": "system", "content": base_prompt},
                {"role": "user", "content": prompt},
            ]

            # 스트리밍 방식으로 GPT 응답 반환
            return StreamingResponse(stream_gpt_response(messages), media_type="text/plain")
        else:
            # 유사도가 낮을 경우, 유도형 질문 생성 및 LLM 호출
            fallback_prompt = generate_fallback_prompt(user_query, result)

            messages = [
                {"role": "system", "content": fallback_base_prompt},
                {"role": "user", "content": fallback_prompt},
            ]

            # 스트리밍 방식으로 GPT 응답 반환
            return StreamingResponse(stream_gpt_response(messages), media_type="text/plain")
    else:
        return JSONResponse(content={"message": "검색 결과가 없습니다."}, status_code=404)


@app.post("/query/vector")
async def query_stream(request: Request):
    body = await request.json()
    user_query = body.get("query", "")

    if not user_query:
        return JSONResponse(content={"message": "쿼리 내용을 입력해주세요."}, status_code=400)

    # 벡터DB에서 쿼리 실행 (상위 3개 결과)
    result = query_chroma(collection, user_query, n_results=3)

    if result:
        return JSONResponse(content=result, status_code=200)
    else:
        return JSONResponse(content={"message": "검색 결과가 없습니다."}, status_code=404)
