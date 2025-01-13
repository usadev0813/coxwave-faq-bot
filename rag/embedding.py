from sentence_transformers import SentenceTransformer

# SentenceTransformer 모델 로드
model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')

# 임베딩 생성 함수
def generate_embedding(text: str, normalize=True):
    return model.encode(text, normalize_embeddings=normalize)
