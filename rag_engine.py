from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RagEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print(f"Initializing embedding model: {model_name}... (Could take a minute if downloading)")
        self.encoder = SentenceTransformer(model_name)
        self.dimension = self.encoder.get_sentence_embedding_dimension()
        
        # Using L2 distance for similarity search in FAISS
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []
        
    def index_documents(self, chunks):
        self.chunks = chunks
        if not chunks:
            print("No valid chunks available to index.")
            return
            
        print(f"Encoding {len(chunks)} chunks into vectors...")
        embeddings = self.encoder.encode(chunks)
        
        print("Adding vectors to FAISS index...")
        self.index.add(np.array(embeddings).astype('float32'))
        
    def add_document(self, text):
        if not text:
            return
            
        print(f"Encoding new learned fact...")
        embedding = self.encoder.encode([text])
        
        self.chunks.append(text)
        self.index.add(np.array(embedding).astype('float32'))
        print(f"Added to dynamic FAISS memory: {text}")
        
    def search(self, query, k=5):
        if not self.chunks or self.index.ntotal == 0:
            return []
            
        # Encode the query text
        query_vector = self.encoder.encode([query])
        
        # Evaluate how many to return
        num_results = min(k, len(self.chunks))
        
        # Search against FAISS index
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), num_results)
        
        # Retrieve the original text mapping
        results = []
        for i in indices[0]:
            if i != -1 and i < len(self.chunks):
                results.append(self.chunks[i])
                
        return results
