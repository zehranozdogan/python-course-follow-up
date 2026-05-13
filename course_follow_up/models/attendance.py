class Attendance:
    def __init__(self, attendance_id, student_id, course_id, total_hours=0, absent_hours=0, attendance_date=None):
        self.attendance_id = attendance_id
        self.student_id = student_id
        self.course_id = course_id
        self.total_hours = total_hours
        self.absent_hours = absent_hours
        self.attendance_date = attendance_date

    def calculate_percentage(self):
        if self.total_hours == 0:
            return 100
        attended_hours = self.total_hours - self.absent_hours
        return round((attended_hours / self.total_hours) * 100, 2)