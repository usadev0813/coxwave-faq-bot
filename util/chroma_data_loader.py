import os
import pickle
import re
from dotenv import load_dotenv
from util.chroma import get_chroma_client, get_or_create_collection, store_data_in_chroma

load_dotenv()

# 데이터 로드
pkl_path = "../final_result.pkl"
with open(pkl_path, "rb") as f:
    data = pickle.load(f)

# 불필요한 데이터 제거 함수 (정규표현식 사용)
def clean_data_with_regex(text):
    # 정규표현식 패턴 정의
    patterns = [
        r"위 도움말이 도움이 되었나요\?",    # 고정 문구
        r"별점[1-5]점",                      # "별점X점" 패턴
        r"소중한 의견을 남겨주시면.*?보완하도록 노력하겠습니다\.",  # 의견 남기기 문구
        r"보내기",                           # "보내기" 단일 문구
        r"관련 도움말/키워드",                # 관련 도움말 문구
        r"도움말 닫기",                      # "도움말 닫기" 문구
    ]
    # 정규표현식을 순회하며 제거
    for pattern in patterns:
        text = re.sub(pattern, "", text)

    # 다중 개행 제거 및 불필요한 공백 제거
    text = re.sub(r"\n{2,}", "\n", text)  # 연속된 개행(\n)을 하나로 축소
    text = text.strip()  # 텍스트 양쪽 공백 제거

    return text

# 데이터 변환 및 전처리
items = [
    {"question": str(key), "answer": clean_data_with_regex(value)}
    for key, value in data.items()
]
print(f"총 데이터 개수: {len(items)}")

# 백터 DB에 저장
client = get_chroma_client()
collection_name = os.getenv("COLLECTION_NAME")
collection = get_or_create_collection(client, collection_name)
store_data_in_chroma(collection, items)
