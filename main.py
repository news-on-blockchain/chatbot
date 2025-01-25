import datetime
import json
import os
import argparse
from pinecone import Pinecone
from llama_index.llms.gemini import Gemini
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import StorageContext, VectorStoreIndex, Document
from llama_index.core import Settings

# Configuration constants
GOOGLE_API_KEY = "AIzaSyB3C2hhghT1ui_O_LtOJIU1l5opS7auWv8"
PINECONE_API_KEY = "pcsk_2KsrkV_F47uZsXMfR6MYnNTbutqzPjVZ3JtwFHGFPLAebXzaCJqceYXuthq38NDteu9gX6"
JSON_FILE_PATH = "./test.json"
PINECONE_INDEX_NAME = "schedule"
EMBEDDING_MODEL = "models/embedding-001"

class Student:
    def __init__(self, student_data: dict):
        self.semester = student_data.get('semester', 4)
        self.branch = student_data.get('branch', 'CSE')
        self.group = student_data.get('group', 'B')
        self.institute_id = student_data.get('institute_id', 53)

def configure_environment():
    """Set up environment variables"""
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Academic Schedule Management System",
        epilog="Example: python main.py --train"
    )
    parser.add_argument("--train", action="store_true",
                      help="Initialize/update Pinecone DB with local data")
    return parser.parse_args()

def load_schedule_data(file_path):
    """Load and process JSON schedule data"""
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

def initialize_components():
    """Initialize AI and database components"""
    llm = Gemini()
    embed_model = GeminiEmbedding(model_name=EMBEDDING_MODEL)
    pinecone = Pinecone()
    index = pinecone.Index(PINECONE_INDEX_NAME)
    
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.chunk_size = 512
    
    return PineconeVectorStore(pinecone_index=index)

def contextualize_query(base_query: str, student: Student) -> str:
    today = datetime.datetime.now().strftime("%A").lower()
    current_time = datetime.datetime.now().strftime("%H:%M")
    return (
        f"{base_query} For student in semester {student.semester}, "
        f"{student.branch} department, group {student.group}. "
        f"Today is {today}, current time is {current_time}. "
        "Consider only relevant courses matching the student's branch, group and semester."
    )

def main():
    # Initial setup
    configure_environment()
    args = parse_arguments()
    
    # Initialize vector store
    vector_store = initialize_components()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Handle training mode
    if args.train:
        print("🔧 Training mode: Processing local data...")
        documents = load_schedule_data(JSON_FILE_PATH)
        VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True
        )
        print("✅ Successfully updated Pinecone DB")
    
    # Initialize query engine
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    query_engine = index.as_query_engine()
    
    # Interactive query interface
    print("\n📚 Academic Schedule Query System")
    print("Type 'exit' to end session\n")
    
    while True:
        try:
            query = input("❓ Your question: ")
            if query.lower() == 'exit':
                break
            
            student = Student(student_data={
                  "semester": 4,
                  "branch": "CSE",
                  "group": "B",
                  "institute_id": 53
            })
            built_query: str = contextualize_query(query, student)
            response = query_engine.query(built_query)
            print(f"\n🤖 Response: {response}\n")
            
        except KeyboardInterrupt:
            print("\nSession ended")
            break
        except Exception as e:
            print(f"\n⚠️ Error processing query: {str(e)}")

if __name__ == "__main__":
    main()