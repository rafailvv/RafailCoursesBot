import sqlite3
from datetime import date, datetime


class Database:
    def __init__(self):
        self.db = sqlite3.connect('bot/database/education.db')
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

    def is_teacher(self, chat_id, useraname):
        id = self.cur.execute(f"SELECT id FROM teacher WHERE username = '@{useraname}'").fetchone()
        if id is not None:
            self.cur.execute(f"UPDATE teacher SET chat_id = {chat_id} WHERE id ={id[0]}")
            self.db.commit()
            return True
        else:
            return False

    def get_teacher_id_by_chat_id(self, chat_id):
        return self.cur.execute(f"SELECT id FROM teacher WHERE chat_id = '{chat_id}'").fetchone()[0]

    def get_further_flows_for_teacher(self, teacher_id):
        res = []
        flows = self.cur.execute(f"""
            SELECT name, start_date, finish_date 
            FROM course_flow 
            INNER JOIN course c on course_flow.course = c.id AND teacher = {teacher_id}""").fetchall()
        for flow in flows:
            res.append((flow[0],
                        flow[1].split("-")[2] + "." + flow[1].split("-")[1] +  "." + flow[1].split("-")[0],
                        flow[2].split("-")[2] + "." + flow[2].split("-")[1] +  "." + flow[2].split("-")[0] ))
        return res



    def get_near_flow_delta_by_course_id(self, id):
        min_delta = -1
        for flow_date in self.cur.execute(f"SELECT start_date FROM course_flow WHERE course = {id} AND student_count < 7").fetchall():
            year, month, day = flow_date[0].split("-")
            delta = (datetime(int(year), int(month), int(day)) - datetime.now()).days
            if min_delta == -1 or (min_delta > delta >= 0):
                min_delta = delta
        return min_delta

    def get_flow_id_by_course_and_date(self, course_name, start_date, finish_date, teacher_chat_id):
        return self.cur.execute(f"""
            SELECT id FROM course_flow 
            WHERE course = (SELECT id FROM course WHERE name = '{course_name}') AND
                teacher = (SELECT id FROM teacher WHERE chat_id = {teacher_chat_id}) AND 
                start_date = '{datetime(int(start_date.split(".")[2]),
                                        int(start_date.split(".")[1]), 
                                        int(start_date.split(".")[0])).date() }' AND 
                finish_date = '{datetime(int(finish_date.split(".")[2]),
                                         int(finish_date.split(".")[1]),
                                         int(finish_date.split(".")[0])).date() }'""").fetchone()[0]

    def get_link_by_flow_id(self, id):
        return self.cur.execute(f"SELECT lesson_link FROM course_flow WHERE id = {id}").fetchone()[0]

    def get_list_students_by_flow_id (self, id):
        return self.cur.execute(f"SELECT full_name, chat_id FROM student WHERE course_flow = {id}").fetchall()

    def get_chat_id_students_in_flow(self, id):
        return self.cur.execute(f"SELECT chat_id FROM student WHERE course_flow = {id}").fetchall()



