class Schedule:
    def __init__(self, schedule_id, course_id, day_of_week, start_time, end_time, classroom=None):
        self.schedule_id = schedule_id
        self.course_id = course_id
        self.day_of_week = day_of_week   # 'Monday', 'Tuesday', ...
        self.start_time = start_time     # '09:00'
        self.end_time = end_time         # '11:00'
        self.classroom = classroom

    def __repr__(self):
        return f"Schedule(course={self.course_id}, {self.day_of_week} {self.start_time}-{self.end_time})"