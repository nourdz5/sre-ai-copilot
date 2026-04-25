import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import os

embedding_fn = DefaultEmbeddingFunction()

chroma_client = chromadb.PersistentClient(path="./chroma_db")

def index_runbooks(runbooks_dir="./runbooks"):
    collection = chroma_client.get_or_create_collection(
        name="runbooks",
        embedding_function=embedding_fn
    )

    documents = []
    ids = []

    for filename in os.listdir(runbooks_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(runbooks_dir, filename)
            with open(filepath, "r") as f:
                content = f.read()
            documents.append(content)
            ids.append(filename.replace(".md", ""))

    if documents:
        collection.upsert(documents=documents, ids=ids)
        print(f"Indexed {len(documents)} runbooks")

    return collection


def search_runbooks(query, n_results=1):
    collection = chroma_client.get_or_create_collection(
        name="runbooks",
        embedding_function=embedding_fn
    )

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    if results["documents"] and results["documents"][0]:
        return results["documents"][0][0]

    return "No relevant runbook found"


if __name__ == "__main__":
    index_runbooks()
    result = search_runbooks("memory usage high, OOMKilled")
    print(result)
