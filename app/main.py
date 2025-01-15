import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv
import openai

from llm.llm_call import stream_gpt_call
from llm.prompt import generate_prompt, generate_fallback_prompt
from rag.chroma import get_chroma_client, get_or_create_collection, query_chroma
from rag.conversation_memory import ConversationMemory

# 환경 변수 로드 및 검증
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

collection_name = os.getenv("COLLECTION_NAME")
if not collection_name:
    raise ValueError("COLLECTION_NAME 환경 변수가 설정되지 않았습니다.")

# FastAPI 애플리케이션 초기화
app = FastAPI()

# ChromaDB 클라이언트 및 컬렉션 설정
client = get_chroma_client()
collection = get_or_create_collection(client, collection_name)

# 대화기록 인메모리 생성
memory = ConversationMemory()

def process_query_results(user_query: str, result: list, memory: ConversationMemory):
    """
    벡터DB 쿼리 결과를 처리하고 적절한 프롬프트를 생성.
    """
    valid_results = [res for res in result if res["similarity_score"] >= 0.2]

    if valid_results:
        faq_answers = [res["content"] for res in valid_results]
        prompt = generate_prompt(faq_answers, memory.get_history())

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query},
        ]
        return {
            "stream": True,
            "messages": messages,
        }
    else:
        fallback_prompt = generate_fallback_prompt(result, memory.get_history())

        messages = [
            {"role": "system", "content": fallback_prompt} ,
            {"role": "user", "content": user_query},
        ]
        return {
            "stream": True,
            "messages": messages,
        }

# 스트리밍 기반 RAG API 엔드포인트
@app.post("/query/stream")
async def query_stream(request: Request):
    body = await request.json()
    user_query = body.get("query", "")

    if not user_query:
        return JSONResponse(content={"message": "쿼리 내용을 입력해주세요."}, status_code=400)

    # 벡터DB에서 쿼리 실행
    result = query_chroma(collection, user_query, n_results=3)

    if result:
        response_data = process_query_results(user_query, result, memory)
        if response_data["stream"]:
            return StreamingResponse(
                stream_gpt_call(response_data["messages"], memory, user_query),
                media_type="text/plain",
            )
    else:
        return JSONResponse(content={"message": "검색 결과가 없습니다."}, status_code=404)

# 일반 벡터 쿼리 API 엔드포인트
@app.post("/query/vector")
async def query_vector(request: Request):
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
