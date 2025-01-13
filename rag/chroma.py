import os
import chromadb
from chromadb.config import Settings
from rag.embedding import generate_embedding

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ChromaDB 클라이언트 생성
def get_chroma_client():
    return chromadb.PersistentClient(
        path=os.path.join(ROOT_DIR, "chroma_data"),
        settings=Settings(anonymized_telemetry=False)
    )


# 컬렉션 생성 또는 가져오기
def get_or_create_collection(client, collection_name):
    return client.get_or_create_collection(name=collection_name)


# 데이터 저장
def store_data_in_chroma(collection, items, batch_size=100):
    ids = []
    metadatas = []
    embeddings = []
    documents = []

    for idx, item in enumerate(items):
        embedding = generate_embedding(item["question"])
        ids.append(str(idx))
        metadatas.append({"question": item["question"], "source": "final_result.pkl"})
        embeddings.append(embedding.tolist())
        documents.append(item["answer"])

    for i in range(0, len(ids), batch_size):
        chunk_ids = ids[i:i + batch_size]
        chunk_metadatas = metadatas[i:i + batch_size]
        chunk_embeddings = embeddings[i:i + batch_size]
        chunk_documents = documents[i:i + batch_size]

        collection.add(
            ids=chunk_ids,
            embeddings=chunk_embeddings,
            metadatas=chunk_metadatas,
            documents=chunk_documents
        )
    print(f"컬렉션 '{collection.name}'에 {len(items)}개의 데이터가 저장되었습니다.")


# 데이터 검색
def query_chroma(collection, query_text: str, n_results=1):
    query_embedding = generate_embedding(query_text)
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    if result["ids"]:
        formatted_results = []
        for idx, (doc_id, metadata, document, distance) in enumerate(zip(
                result["ids"][0],
                result["metadatas"][0],
                result["documents"][0],
                result["distances"][0])):
            formatted_results.append({
                "id": doc_id,
                "question": metadata["question"],
                "content": document,
                "similarity_score": round(1 - distance, 2),  # 유사도 점수 계산
                "source": metadata["source"]
            })
        return formatted_results
    else:
        return None
