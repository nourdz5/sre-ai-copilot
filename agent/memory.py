import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from datetime import datetime

embedding_fn = DefaultEmbeddingFunction()

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="incidents",
    embedding_function=embedding_fn
)

def store_incident(alert_text, severity, analysis, verdict):
    timestamp = datetime.utcnow().isoformat()
    collection.add(
        documents=[alert_text],
        metadatas=[{
            "severity": severity,
            "analysis": analysis,
            "verdict": verdict,
            "timestamp": timestamp
        }],
        ids=[f"{alert_text}_{timestamp}"]
    )

def get_similar_incidents(alert_text, n=3):
    count = collection.count()
    if count == 0:
        return []

    results = collection.query(
        query_texts=[alert_text],
        n_results=min(n, count)
    )

    if not results["documents"][0]:
        return []

    incidents = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        incidents.append({
            "alert": doc,
            "severity": meta["severity"],
            "analysis": meta["analysis"],
            "verdict": meta["verdict"],
            "timestamp": meta["timestamp"]
        })

    return incidents
