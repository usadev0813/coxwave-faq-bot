import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv
import openai
from util.chroma import get_chroma_client, get_or_create_collection, query_chroma

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


# GPT 프롬프트 템플릿
def generate_prompt(user_query, faq_answers):
    faq_text = "\n".join([f"{i + 1}. {answer}" for i, answer in enumerate(faq_answers)])
    return (
        f"""
        ### 컨텍스트
        너는 네이버 스마트스토어 고객센터 상담사입니다. 아래 FAQ 답변을 참고하여 사용자에게 친절하고 정확한 답변을 제공합니다. 
        사용자의 질문에 대해 답을 해준 뒤, 관련된 후속 질문을 두 가지 이상 포함시켜 사용자가 추가로 궁금해할만한 내용을 제안합니다.

        ### 참고사항
        - 후속 질문은 항상 친절한 어조로 작성하세요.

        ### 예제
        사용자 질문: 미성년자도 판매 회원 등록이 가능한가요?
        FAQ 답변:
        네이버 스마트스토어는 만 14세 미만의 개인(개인 사업자 포함) 또는 법인사업자는 입점이 불가함을 양해 부탁 드립니다.
        (스마트스토어 판매 이용약관 : 제5조 (이용계약의 성립) 3항)
        만 14세 이상 ~ 만 19세 미만인 판매회원은 아래의 서류를 가입 신청단계에서 제출해주셔야 심사가 가능합니다.
        - 법정대리인 인감증명서 사본 1부
        - 가족관계증명서 사본 1부
        - 스마트스토어 법정대리인 동의서 사본 1부

        상담사 답변:
        네이버 스마트스토어는 만 14세 미만의 개인(개인 사업자 포함) 또는 법인사업자는 입점이 불가함을 양해 부탁 드립니다.

        후속 질문:
        - 등록에 필요한 서류 안내해드릴까요?
        - 등록 절차는 얼마나 오래 걸리는지 안내가 필요하신가요?

        ### 사용자 입력
        사용자 질문: {user_query}
        FAQ 답변:
        {faq_text}

        상담사 답변:
        """
    )


# 스트리밍용 GPT API 호출 함수
async def stream_gpt_response(messages):
    try:
        # ChatCompletion API 사용
        stream = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400,
            temperature=0.5,
            stream=True,
        )

        async for chunk in stream:
            if "choices" in chunk and chunk["choices"][0].get("delta", {}).get("content"):
                yield chunk["choices"][0]["delta"]["content"]
    except Exception as e:
        yield f"GPT API 호출 중 오류가 발생했습니다: {str(e)}"


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
        faq_answers = [res["content"] for res in result]
        prompt = generate_prompt(user_query, faq_answers)

        # ChatCompletion 메시지 생성
        messages = [
            {"role": "system", "content": "친절하고 정확한 상담사 역할을 수행합니다."},
            {"role": "user", "content": prompt},
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

    # 벡터DB에서 쿼리 실행 (상위 1개 결과)
    result = query_chroma(collection, user_query, n_results=3)

    if result:
        return JSONResponse(content=result, status_code=200)
    else:
        return JSONResponse(content={"message": "검색 결과가 없습니다."}, status_code=404)
