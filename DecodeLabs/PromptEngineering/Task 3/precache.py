import os
import sys
import io
import pandas as pd

from app import EmbeddingEngine, FAISSVectorStore, SAMPLE_DATASETS

def run():
    print("Pre-caching FAISS indices and vector embeddings to disk...")
    embedder = EmbeddingEngine()
    store = FAISSVectorStore(embedder)

    for name, csv_str in SAMPLE_DATASETS.items():
        store.clear()
        df = pd.read_csv(io.StringIO(csv_str))
        chunk_list = []
        for idx, row in df.iterrows():
            chunk_list.append({
                'id': row['id'],
                'paragraph': str(row['paragraph_text']),
                'citation_id': f"[Paragraph {row['id']}]",
                'source': str(row.get('source', 'Dataset.csv'))
            })
        store.add_chunks(chunk_list, cache_key=name)

    print("✅ All FAISS indices pre-cached to disk successfully!")

if __name__ == "__main__":
    run()
