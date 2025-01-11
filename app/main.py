from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from util.chroma import get_chroma_client, get_or_create_collection, query_chroma

# FastAPI 애플리케이션 초기화
app = FastAPI()

# ChromaDB 클라이언트 및 컬렉션 설정
client = get_chroma_client()
collection_name = "naver_help"
collection = get_or_create_collection(client, collection_name)


# API 엔드포인트
@app.post("/query")
async def query(request: Request):
    """
    사용자의 쿼리를 받아 가장 유사한 결과를 반환합니다.
    """
    body = await request.json()
    user_query = body.get("query", "")

    if not user_query:
        return JSONResponse(content={"message": "쿼리 내용을 입력해주세요."}, status_code=400)

    # 벡터DB에서 쿼리 실행 (상위 1개 결과)
    result = query_chroma(collection, user_query, n_results=1)

    if result:
        return JSONResponse(content=result[0], status_code=200)
    else:
        return JSONResponse(content={"message": "검색 결과가 없습니다."}, status_code=404)
