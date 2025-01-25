class Student:
    def __init__(self, student_data: dict = None):
        student_data = student_data or {}
        self.semester = student_data.get('semester', 4)
        self.branch = student_data.get('branch', 'CSE')
        self.group = student_data.get('group', 'B')
        self.institute_id = student_data.get('institute_id', 53)

    def to_dict(self):
        return {
            'semester': self.semester,
            'branch': self.branch,
            'group': self.group,
            'institute_id': self.institute_id
        }