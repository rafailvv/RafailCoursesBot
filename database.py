import sqlite3


class Database:
    def __init__(self):
        self.db = sqlite3.connect('education.db')
        self.cur = self.db.cursor()

    def get_courses_name(self):
        courses_names = []
        for name in self.cur.execute("SELECT name FROM course").fetchall():
            courses_names.append(name[0])
        return courses_names

    def get_course_program(self, course_id):
        return self.cur.execute(f"SELECT program FROM course WHERE id = '{course_id}'").fetchone()[0]

    def get_course_name(self, course_id):
        return self.cur.execute(f"SELECT name FROM course WHERE id = '{course_id}'").fetchone()[0]

    def get_course_full_description(self, course_id):
        des_query = self.cur.execute(
            f"SELECT short_description,description FROM course WHERE id = '{course_id}'").fetchone()
        return des_query[0] + "\n\n" + des_query[1]

    def get_course_short_description(self, course_id):
        return self.cur.execute(f"SELECT short_description FROM course WHERE id = '{course_id}'").fetchone()[0]

    def get_course_id_by_name(self, course_name):
        return self.cur.execute(f"SELECT id FROM course WHERE name = '{course_name}'").fetchone()[0]
