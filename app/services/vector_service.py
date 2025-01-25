import json
import os
from pinecone import Pinecone
from llama_index.llms.gemini import Gemini
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import StorageContext, VectorStoreIndex, Document, Settings

class VectorService:
    def __init__(self, config):
        os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
        os.environ["PINECONE_API_KEY"] = config.PINECONE_API_KEY
        
        self.config = config
        self.pinecone = Pinecone()
        self.index = self.pinecone.Index(config.PINECONE_INDEX_NAME)
        
        self._initialize_settings()
    
    def _initialize_settings(self):
        """Initialize AI and database settings"""
        Settings.llm = Gemini()
        Settings.embed_model = GeminiEmbedding(model_name=self.config.EMBEDDING_MODEL)
        Settings.chunk_size = 512
    
    def load_schedule_data(self, file_path=None):
        """Load and process JSON schedule data"""
        file_path = file_path or self.config.JSON_FILE_PATH
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        documents = []
        # Process course schedules
        for schedule in data.get("schedules", []):
            doc_text = f"""
            Course: {schedule.get('course_title', '')} ({schedule.get('course_code', '')})
            Type: {schedule.get('type', '').title()}
            Professor: {schedule.get('prof', 'N/A')}
            Time: {schedule.get('from', '')} to {schedule.get('to', '')}
            Day: {schedule.get('day', '')}
            Group: {schedule.get('group', '')}
            Room: {schedule.get('room', '')}
            Semester: {schedule.get('semester', '')}
            """
            metadata = {
                "semester": schedule.get("semester", ""),
                "branch": schedule.get("branch", ""),
                "group": schedule.get("group", ""),
                "type": schedule.get("type", ""),
                "course_code": schedule.get("course_code", ""),
                "day": schedule.get("day", "")
            }
            documents.append(Document(text=doc_text.strip(), metadata=metadata))
        
        # Add institute information
        if "institute" in data:
            institute = data["institute"]
            institute_text = f"""
            Institute: {institute.get('name', '')} ({institute.get('short_name', '')})
            Affiliation: {institute.get('affiliation', '')}
            Website: {institute.get('website_url', '')}
            Email Domain: {institute.get('mail_slug', '')}
            """
            documents.append(Document(
                text=institute_text.strip(),
                metadata={"type": "institute_info"}
            ))
        
        return documents
    
    def train_vector_store(self):
        """Train/Update Pinecone vector store"""
        vector_store = PineconeVectorStore(pinecone_index=self.index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        documents = self.load_schedule_data()
        VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True
        )
        return "Successfully updated Pinecone DB"
    
    def get_query_engine(self):
        """Get query engine for vector store"""
        vector_store = PineconeVectorStore(pinecone_index=self.index)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        return index.as_query_engine()