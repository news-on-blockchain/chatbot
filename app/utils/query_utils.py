import datetime
from typing import Dict, Any

def contextualize_query(base_query: str, student_data: Dict[str, Any]) -> str:
    """
    Enhance the base query with contextual information from student data
    
    Args:
        base_query (str): Original user query
        student_data (Dict[str, Any]): Student context information
    
    Returns:
        str: Contextualized query with additional details
    """
    today = datetime.datetime.now().strftime("%A").lower()
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    return (
        f"{base_query} For student in semester {student_data.get('semester', 4)}, "
        f"{student_data.get('branch', 'CSE')} department, "
        f"group {student_data.get('group', 'B')}. "
        f"Today is {today}, current time is {current_time}. "
        "Consider only relevant courses matching the student's branch, group and semester."
    )