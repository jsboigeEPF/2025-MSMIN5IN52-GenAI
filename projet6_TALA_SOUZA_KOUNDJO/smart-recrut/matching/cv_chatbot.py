"""
CV Chatbot with RAG (Retrieval-Augmented Generation)
Allows querying uploaded CVs using semantic search and LLM
"""
import os
import pandas as pd
from typing import List, Dict, Optional
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import DistanceStrategy
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

load_dotenv()

# Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RAG_K_THRESHOLD = 5
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 500


class CVVectorStore:
    """Manages FAISS vectorstore for CV embeddings"""
    
    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"}
        )
        self.vectorstore = None
        self.df = None
        
    def ingest_csv(self, csv_path: str) -> int:
        """Load CVs from CSV and create vectorstore"""
        # Read CSV
        self.df = pd.read_csv(csv_path)
        
        # Validate columns
        if "Resume" not in self.df.columns or "ID" not in self.df.columns:
            raise ValueError("CSV must contain 'ID' and 'Resume' columns")
        
        # Load documents
        loader = DataFrameLoader(self.df, page_content_column="Resume")
        documents = loader.load()
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        document_chunks = text_splitter.split_documents(documents)
        
        # Create vectorstore
        self.vectorstore = FAISS.from_documents(
            document_chunks,
            self.embedding_model,
            distance_strategy=DistanceStrategy.COSINE
        )
        
        return len(self.df)
    
    def ingest_dataframe(self, df: pd.DataFrame) -> int:
        """Load CVs from DataFrame and create vectorstore"""
        self.df = df
        
        # Validate columns
        if "Resume" not in self.df.columns or "ID" not in self.df.columns:
            raise ValueError("DataFrame must contain 'ID' and 'Resume' columns")
        
        # Load documents
        loader = DataFrameLoader(self.df, page_content_column="Resume")
        documents = loader.load()
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        document_chunks = text_splitter.split_documents(documents)
        
        # Create vectorstore
        self.vectorstore = FAISS.from_documents(
            document_chunks,
            self.embedding_model,
            distance_strategy=DistanceStrategy.COSINE
        )
        
        return len(self.df)
    
    def similarity_search(self, query: str, k: int = RAG_K_THRESHOLD) -> List[Dict]:
        """Search for similar CVs"""
        if self.vectorstore is None:
            return []
        
        # Get similar documents with scores
        docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
        
        # Extract unique IDs and get full CV text
        id_resume_dict = dict(zip(self.df["ID"].astype(str), self.df["Resume"]))
        seen_ids = set()
        results = []
        
        for doc, score in docs_with_scores:
            doc_id = str(doc.metadata.get("ID", ""))
            if doc_id and doc_id not in seen_ids:
                seen_ids.add(doc_id)
                results.append({
                    "id": doc_id,
                    "resume": id_resume_dict.get(doc_id, ""),
                    "score": float(score)
                })
                
                if len(results) >= k:
                    break
        
        return results
    
    def get_cv_by_id(self, cv_id: str) -> Optional[str]:
        """Retrieve CV by ID"""
        if self.df is None:
            return None
        
        try:
            resume = self.df[self.df["ID"].astype(str) == str(cv_id)].iloc[0]["Resume"]
            return resume
        except (IndexError, KeyError):
            return None


class CVChatbot:
    """LLM-powered chatbot for CV analysis"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0.1
        )
        self.vector_store = CVVectorStore()
        
    def load_cvs(self, csv_path: str = None, df: pd.DataFrame = None) -> int:
        """Load CVs from CSV or DataFrame"""
        if csv_path:
            return self.vector_store.ingest_csv(csv_path)
        elif df is not None:
            return self.vector_store.ingest_dataframe(df)
        else:
            raise ValueError("Must provide either csv_path or df")
    
    def _retrieve_relevant_cvs(self, query: str, fiches_context: str = "") -> str:
        """Retrieve relevant CVs based on query"""
        # Search vectorstore
        results = self.vector_store.similarity_search(query, k=RAG_K_THRESHOLD)
        
        if not results:
            return "Aucun CV trouvé."
        
        # Format results
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"=== Candidat ID: {result['id']} (Score: {result['score']:.3f}) ===\n"
                f"{result['resume']}\n"
            )
        
        context = "\n\n".join(context_parts)
        
        # Add fiches context if available
        if fiches_context:
            context = f"FICHES DE POSTE DISPONIBLES:\n{fiches_context}\n\n" + context
        
        return context
    
    def generate_response_stream(self, user_query: str, fiches_context: str = ""):
        """Generate streaming response"""
        # Retrieve relevant CVs
        context = self._retrieve_relevant_cvs(user_query, fiches_context)
        
        # Create prompt
        system_message = SystemMessage(content="""
Tu es un expert en recrutement qui analyse des CVs pour aider à la sélection de candidats.

Tes responsabilités:
- Analyser les CVs fournis dans le contexte
- Identifier les meilleurs candidats pour un poste
- Comparer les candidats entre eux
- Répondre aux questions sur les compétences, expériences, etc.
- Utiliser les fiches de poste disponibles pour mieux comprendre les besoins

IMPORTANT:
- Utilise TOUJOURS les IDs des candidats dans tes réponses (ex: "Candidat ID 123")
- Base-toi UNIQUEMENT sur les informations du contexte
- Si tu ne sais pas, dis-le clairement
- N'invente jamais d'informations
- Sois concis mais précis
        """.strip())
        
        user_message = HumanMessage(content=f"""
Question: {user_query}

Contexte (CVs et fiches de poste):
{context}
        """.strip())
        
        # Stream response
        stream = self.llm.stream([system_message, user_message])
        return stream
    
    def get_cv_by_ids(self, ids: List[str]) -> List[Dict]:
        """Get CVs by specific IDs"""
        results = []
        for cv_id in ids:
            resume = self.vector_store.get_cv_by_id(cv_id)
            if resume:
                results.append({"id": cv_id, "resume": resume})
        return results
