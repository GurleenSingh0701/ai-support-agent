# import os
# from typing import List, Dict, Any

# class KBRetriever:
#     def __init__(self, docs_dir: str = None):
#         if not docs_dir:
#             docs_dir = os.path.join(os.path.dirname(__file__), "docs")
#         self.docs_dir = docs_dir
#         self.documents = self._load_documents()

#     def _load_documents(self) -> List[Dict[str, str]]:
#         docs = []
#         if os.path.exists(self.docs_dir):
#             for filename in os.listdir(self.docs_dir):
#                 if filename.endswith(".md") or filename.endswith(".txt"):
#                     filepath = os.path.join(self.docs_dir, filename)
#                     with open(filepath, "r", encoding="utf-8") as f:
#                         docs.append({"filename": filename, "content": f.read()})
#         return docs

#     def search(self, query_text: str, top_k: int = 2) -> List[str]:
#         query_words = set(query_text.lower().split())
#         scored_snippets = []
        
#         for doc in self.documents:
#             lines = doc["content"].split("\n")
#             for i, line in enumerate(lines):
#                 if not line.strip():
#                     continue
#                 line_words = set(line.lower().split())
#                 overlap = len(query_words.intersection(line_words))
#                 if overlap > 0:
#                     scored_snippets.append((overlap, line.strip()))
                    
#         scored_snippets.sort(key=lambda x: x[0], reverse=True)
#         results = [s[1] for s in scored_snippets[:top_k]]
        
#         if not results:
#             results = [
#                 "AutoDesk Store Policy: Returns accepted within 30 days of purchase. Support agents are available 24/7."
#             ]
#         return results

# kb_retriever = KBRetriever()


import os
import math
from typing import List, Dict, Any, Optional
from google import genai

class KBRetriever:
    def __init__(self, docs_dir: Optional[str] = None):
        if not docs_dir:
            docs_dir = os.path.join(os.path.dirname(__file__), "docs")
        self.docs_dir = docs_dir
        self.documents = self._load_documents()
        self.chunks = self._chunk_documents(self.documents)
        self.embeddings_cache = {}
        self._initialize_embeddings()

    def _load_documents(self) -> List[Dict[str, str]]:
        docs = []
        if os.path.exists(self.docs_dir):
            for filename in os.listdir(self.docs_dir):
                if filename.endswith(".md") or filename.endswith(".txt"):
                    filepath = os.path.join(self.docs_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        docs.append({"filename": filename, "content": f.read()})
        return docs

    def _chunk_documents(self, docs: List[Dict[str, str]]) -> List[str]:
        chunks = []
        for doc in docs:
            # Semantic chunking by paragraphs to maintain context
            paragraphs = [p.strip() for p in doc["content"].split("\n\n") if p.strip()]
            chunks.extend(paragraphs)
        
        # Fallback if docs directory is empty
        if not chunks:
            chunks = ["Autodesk Store Policy: Returns accepted within 30 days of purchase. Support agents are available 24/7."]
        return chunks

    def _get_embedding(self, text: str) -> List[float]:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return [0.0] * 768 # Dummy embedding if API key is missing
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.embed_content(
                model='gemini-embedding-2',
                contents=text
            )
            if response.embeddings and response.embeddings[0].values is not None:
                return list(response.embeddings[0].values)
            return [0.0] * 768
        except Exception as e:
            print(f"Embedding error: {e}")
            return [0.0] * 768

    def _initialize_embeddings(self):
        """Pre-computes embeddings for all chunks in the KB at startup."""
        for chunk in self.chunks:
            self.embeddings_cache[chunk] = self._get_embedding(chunk)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def search(self, query_text: str, top_k: int = 2) -> List[str]:
        query_embedding = self._get_embedding(query_text)
        
        scored_chunks = []
        for chunk, embedding in self.embeddings_cache.items():
            score = self._cosine_similarity(query_embedding, embedding)
            scored_chunks.append((score, chunk))
            
        # Sort by highest semantic similarity
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Filter low-relevance matches (Threshold: 0.5)
        results = [s[1] for s in scored_chunks[:top_k] if s[0] > 0.50 or len(self.embeddings_cache) == 1]
        
        if not results:
            results = ["No specific policy found for your query. Connecting you to a support agent for clarification."]
            
        return results

kb_retriever = KBRetriever()