import os
import pickle
from dotenv import load_dotenv

from util.chroma import get_chroma_client, get_or_create_collection, store_data_in_chroma

load_dotenv()

# 데이터 로드
pkl_path = "../final_result.pkl"
with open(pkl_path, "rb") as f:
    data = pickle.load(f)

# 데이터 변환: dict 구조에서 id와 content를 추출
items = [{"question": str(key), "answer": value} for key, value in data.items()]
print(f"총 데이터 개수: {len(items)}")

client = get_chroma_client()
collection_name = os.getenv("COLLECTION_NAME")
collection = get_or_create_collection(client, collection_name)

# 데이터 저장
store_data_in_chroma(collection, items)
