import os
import numpy as np
import faiss
import google.generativeai as genai
from typing import List, Tuple, Dict
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ ERROR: No API key found!")
    exit(1)
genai.configure(api_key=api_key)
os.environ["GOOGLE_API_KEY"] = api_key
embedding_model = "models/gemini-embedding-001"

class RAGEngine:
    def __init__(self):
        self.documents = []
        self.chunks = []
        self.embeddings = None
        self.index = None
        self.chunk_to_doc = []
        
    def load_runbooks(self, runbook_dir: str = "data/runbooks"):
        import os
        self.documents = []
        for filename in os.listdir(runbook_dir):
            if filename.endswith(".txt"):
                with open(os.path.join(runbook_dir, filename), 'r') as f:
                    content = f.read()
                    self.documents.append({
                        "name": filename.replace(".txt", ""),
                        "content": content
                    })
        print(f"✅ Loaded {len(self.documents)} runbooks")
        return self.documents
    
    def chunk_documents(self, chunk_size: int = 500, overlap: int = 50):
        self.chunks = []
        self.chunk_to_doc = []
        for doc_idx, doc in enumerate(self.documents):
            content = doc["content"]
            words = content.split()
            for i in range(0, len(words), chunk_size - overlap):
                chunk = " ".join(words[i:i + chunk_size])
                if chunk.strip():
                    self.chunks.append(chunk)
                    self.chunk_to_doc.append(doc_idx)
        print(f"✅ Created {len(self.chunks)} chunks")
        return self.chunks
    
    def embed_and_index(self):
        if not self.chunks:
            return None
        embeddings = []
        batch_size = 50
        print(f"🔄 Embedding {len(self.chunks)} chunks...")
        for i in range(0, len(self.chunks), batch_size):
            batch = self.chunks[i:i+batch_size]
            try:
                result = genai.embed_content(
                    model=embedding_model,
                    content=batch,
                    task_type="retrieval_document"
                )
                embeddings.extend(result['embedding'])
            except Exception as e:
                print(f"  ❌ Error: {e}")
                raise
        self.embeddings = np.array(embeddings).astype('float32')
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)
        print(f"✅ Created FAISS index with {len(self.embeddings)} vectors")
        return self.index
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float, str]]:
        result = genai.embed_content(
            model=embedding_model,
            content=[query],
            task_type="retrieval_query"
        )
        query_embedding = np.array(result['embedding']).astype('float32')
        distances, indices = self.index.search(query_embedding.reshape(1, -1), top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks) and idx >= 0:
                doc_idx = self.chunk_to_doc[idx]
                doc_name = self.documents[doc_idx]["name"]
                # Convert distance to similarity (0-1)
                similarity = 1.0 / (1.0 + distances[0][i])
                results.append((self.chunks[idx], similarity, doc_name))
        return results
    
    def get_relevant_runbook(self, incident_type: str, description: str) -> Dict:
        query = f"{incident_type}: {description}"
        results = self.search(query, top_k=2)
        if not results:
            return {"found": False, "content": None, "citation": None, "confidence": 0.0}
        best_confidence = results[0][1]
        # Only consider it found if confidence > 0.15
        if best_confidence < 0.15:
            return {"found": False, "content": None, "citation": None, "confidence": best_confidence}
        chunks = [r[0] for r in results]
        citations = [r[2] for r in results]
        return {
            "found": True,
            "content": "\n\n".join(chunks),
            "citation": ", ".join(citations),
            "confidence": best_confidence
        }
