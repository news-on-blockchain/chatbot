from app.models.students import Student
from app.utils.query_utils import contextualize_query

class ScheduleService:
    def __init__(self, vector_service):
        self.vector_service = vector_service
        self.query_engine = vector_service.get_query_engine()
    
    def process_query(self, query: str, student_data: dict = None):
        """
        Process a schedule query for a given student
        
        Args:
            query (str): User's query about schedule
            student_data (dict, optional): Student context information
        
        Returns:
            str: Query response
        """
        student = Student(student_data)
        contextualized_query = contextualize_query(query, student.to_dict())
        response = self.query_engine.query(contextualized_query)
        return str(response)