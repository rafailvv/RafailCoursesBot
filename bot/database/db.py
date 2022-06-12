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

    def get_course_name_by_course_id(self, course_id):
        return self.cur.execute(f"SELECT name FROM course WHERE id = '{course_id}'").fetchone()[0]

    def get_course_name_by_flow_id(self, flow_id):
        return self.cur.execute("""
            SELECT c.name
            FROM course c
            INNER JOIN course_flow cf on c.id = cf.course
        """).fetchone()[0]

    def get_course_full_description(self, course_id):
        des_query = self.cur.execute(
            f"SELECT short_description,description FROM course WHERE id = '{course_id}'").fetchone()
        return des_query[0] + "\n\n" + des_query[1]

    def get_course_short_description(self, course_id):
        return self.cur.execute(f"SELECT short_description FROM course WHERE id = '{course_id}'").fetchone()[0]

    def get_near_course_by_name(self, course_name):
        min_delta = 365
        flows = self.cur.execute(f"""
        SELECT course.id, course_flow.start_date
        FROM course 
        INNER JOIN course_flow on course.id = course_flow.course AND
        course.name = '{course_name}'""").fetchall()

        for course, flow_date in flows:
            year, month, day = flow_date.split("-")
            delta = (datetime(int(year), int(month), int(day)) - datetime.now()).days
            if min_delta > delta >= 0:
                min_delta = delta
                course_id = course

        return course_id, min_delta + 1

    def is_teacher(self, chat_id, useraname):
        id = self.cur.execute(f"SELECT id FROM teacher WHERE username = '@{useraname}'").fetchone()
        if id is not None:
            self.cur.execute(f"UPDATE teacher SET chat_id = {chat_id} WHERE id ={id[0]}")
            self.db.commit()
            return True
        else:
            return False

    def is_student(self, chat_id, useraname):
        id = self.cur.execute(f"SELECT id FROM student WHERE username = '@{useraname}' AND is_approved = 1").fetchone()
        if id is not None:
            self.cur.execute(f"UPDATE student SET chat_id = {chat_id} WHERE id ={id[0]}")
            self.db.commit()
            return True
        else:
            return False

    def get_teacher_id_by_chat_id(self, chat_id):
        return self.cur.execute(f"SELECT id FROM teacher WHERE chat_id = {chat_id}").fetchone()[0]

    def get_student_id_by_chat_id(self, chat_id):
        return self.cur.execute(f"SELECT id FROM student WHERE chat_id = {chat_id}").fetchone()[0]

    def get_further_flows_for_teacher(self, teacher_id):
        res = []
        flows = self.cur.execute(f"""
            SELECT name, start_date, finish_date 
            FROM course_flow 
            INNER JOIN course c on course_flow.course = c.id AND course_flow.teacher = {teacher_id} """).fetchall()
        for flow in flows:
            res.append((flow[0],
                        flow[1].split("-")[2] + "." + flow[1].split("-")[1] + "." + flow[1].split("-")[0],
                        flow[2].split("-")[2] + "." + flow[2].split("-")[1] + "." + flow[2].split("-")[0]))
        return res

    def get_current_flows_for_student(self, student_id):
        res = []
        flows = self.cur.execute(f"""
            SELECT name, start_date, finish_date 
            FROM course_flow 
            INNER JOIN course c on course_flow.course = c.id 
            INNER JOIN student s on course_flow.id = s.course_flow AND s.id = {student_id}""").fetchall()
        for flow in flows:
            res.append((flow[0],
                        flow[1].split("-")[2] + "." + flow[1].split("-")[1] + "." + flow[1].split("-")[0],
                        flow[2].split("-")[2] + "." + flow[2].split("-")[1] + "." + flow[2].split("-")[0]))
        return res

    def get_near_course_flow_by_course_id(self, id):
        min_delta = -1

        for course_flow, flow_date in self.cur.execute(
                f"SELECT id, start_date FROM course_flow WHERE course = {id} AND student_count < 7").fetchall():
            year, month, day = flow_date.split("-")
            delta = (datetime(int(year), int(month), int(day)) - datetime.now()).days
            if min_delta == -1 or (min_delta > delta >= 0):
                min_delta = delta
                course_flow_id = course_flow
        return course_flow_id

    def get_flow_id_by_course_and_date(self, course_name, start_date, finish_date, teacher_chat_id):
        # TODO check if such flow for student

        return self.cur.execute(f"""
            SELECT id FROM course_flow 
            WHERE course = (SELECT id FROM course WHERE name = '{course_name}') AND
                start_date = '{datetime(int(start_date.split(".")[2]),
                                        int(start_date.split(".")[1]),
                                        int(start_date.split(".")[0])).date()}' AND 
                finish_date = '{datetime(int(finish_date.split(".")[2]),
                                         int(finish_date.split(".")[1]),
                                         int(finish_date.split(".")[0])).date()}'""").fetchone()[0]

    def get_link_by_flow_id(self, id):
        return self.cur.execute(f"SELECT lesson_link FROM course_flow WHERE id = {id}").fetchone()[0]

    def get_list_students_by_flow_id(self, id):
        return self.cur.execute(
            f"SELECT full_name, id FROM student WHERE course_flow = {id} AND is_approved = 1").fetchall()

    def get_chat_id_students_in_flow(self, id):
        a = self.cur.execute(f"SELECT chat_id FROM student WHERE course_flow = {id} AND is_approved = 1").fetchall()
        return a

    def get_student_info(self, student_id):
        return self.cur.execute(
            f"SELECT full_name, username, phone FROM student WHERE id = {student_id} AND is_approved = 1").fetchone()

    def add_student(self, full_name, phone, username, course_flow, chat_id):
        if chat_id is None:
            self.cur.execute(f"""INSERT INTO student(username, full_name, phone, course_flow) 
                                    VALUES ('@{username}', '{full_name}', '{phone}', {course_flow})""")
        else:
            self.cur.execute(f"""INSERT INTO student(username, full_name, phone, course_flow, chat_id) 
                                                VALUES ('@{username}', '{full_name}', '{phone}', {course_flow}, {chat_id})""")
        self.db.commit()

    def get_teacher_name_by_chat_id(self, chat_id):
        teacher_name = self.cur.execute(f"SELECT full_name FROM teacher WHERE chat_id = {chat_id}").fetchone()[
            0].split()
        if teacher_name is not None:
            return teacher_name[1]

    def get_student_name_by_chat_id(self, chat_id):
        student_name = self.cur.execute(f"SELECT full_name FROM student WHERE chat_id = {chat_id}").fetchone()[
            0].split()
        if student_name is not None:
            return student_name[1]

    def update_confirmation(self, student_id, is_approved=False):
        if not is_approved:
            self.cur.execute(f"DELETE FROM student WHERE id = {student_id}")
        else:
            self.cur.execute(f"UPDATE student SET is_approved = 1 WHERE id = {student_id}")
            self.cur.execute(f"""UPDATE course_flow SET student_count = student_count + 1 WHERE id = 
                    (SELECT course_flow FROM student WHERE id = {student_id})""")
        self.db.commit()

    def get_student_id_by_username(self, username):
        return self.cur.execute(f"SELECT id FROM student WHERE username = '@{username}'").fetchone()[0]

    def get_student_chat_id_by_id(self, id):
        chat_id = self.cur.execute(f"SELECT chat_id FROM student WHERE id = {id}").fetchone()
        if chat_id is not None:
            return chat_id[0]
        return None

    def get_timetable_by_flow_id(self, id):
        return self.cur.execute(f"SELECT timetable FROM course_flow WHERE id = {id}").fetchone()[0]

    def check_if_is_student(self, chat_id):
        if self.cur.execute(f"""SELECT id FROM student WHERE chat_id = {chat_id}""").fetchone() is None:
            return False
        return True

    def get_teacher_info(self, flow_id):
        return self.cur.execute(f"""SELECT full_name, username, phone FROM course_flow, teacher 
                        WHERE course_flow.id = {flow_id} AND teacher.id = course_flow.teacher""").fetchone()

    def save_new_recording(self, video, description, flow_id):
        lesson_number = \
        self.cur.execute(f"SELECT MIN(lesson_number) FROM video_recording WHERE flow_id = {flow_id}").fetchone()[0]
        if lesson_number is None:
            lesson_number = 1
        else:
            lesson_number += 1

        self.cur.execute(f"""INSERT INTO video_recording(flow_id, lesson_number, lesson_date, description, recording)
                    VALUES({flow_id}, {lesson_number}, '{datetime.now().date()}', '{description}', '{video}')""")
        self.db.commit()
        return lesson_number

    def get_students_chat_id_in_flow(self, flow_id):
        return self.cur.execute(f"SELECT chat_id FROM student WHERE course_flow = {flow_id}").fetchall()

    def get_id_recordings_by_flow_id(self, flow_id):
        return self.cur.execute(
            f"SELECT lesson_number, id  FROM video_recording WHERE flow_id = {flow_id} ORDER BY lesson_number").fetchall()

    def get_recorded_lesson(self, id):
        return self.cur.execute(f"""
            SELECT vr.lesson_date, c.name, vr.lesson_number, vr.description, vr.recording 
            FROM video_recording vr
            INNER JOIN course_flow cf on vr.flow_id = cf.id
            INNER JOIN course c on cf.course = c.id WHERE vr.id = {id}
        """).fetchone()

    def get_past_lessons_numbers(self, flow_id):
        return self.cur.execute(f"""SELECT lesson_number FROM video_recording WHERE flow_id = {flow_id}""").fetchall()

    def get_fio_teacher_by_chat_id(self, chat_id):
        return " ".join(
            self.cur.execute(f"""SELECT full_name FROM teacher WHERE chat_id = {chat_id}""").fetchone()[0].split()[1:])

    def add_hw(self, flow_id, lesson_number, student_id, content, content_type):
        self.cur.execute(f"""INSERT INTO homework (flow_id, lesson_number, student_id, datatime_added, content_type, content) 
            VALUES ({flow_id}, {int(lesson_number)}, {student_id}, '{datetime.now()}', '{content_type}','{content}')""")
        self.db.commit()

        return self.cur.execute(f"""
            SELECT id FROM homework WHERE flow_id = {flow_id} AND lesson_number = {lesson_number} AND student_id = {student_id}
            AND content_type = '{content_type}' AND content = '{content}'
        """).fetchone()[0]

    # def get_hw_id(self, flow_id, lesson_number, student_id):
    #     return self.cur.execute(f"SELECT id FROM homework WHERE flow_id = {flow_id} AND lesson_number = '{lesson_number}' AND "
    #                             f"student_id = {student_id} AND confirmation = 0").fetchone()[0]

    def get_hw(self, id):
        return self.cur.execute(f"SELECT content, content_type FROM homework WHERE id = {id}").fetchone()

    def get_hw_solution(self, id):
        return self.cur.execute(f"SELECT content_solution, content_type_solution FROM homework WHERE id = {id}").fetchone()

    def update_hw_solution(self, id, content, content_type):
        self.cur.execute(f"UPDATE homework SET content_solution = '{content}', content_type_solution = '{content_type}', "
                         f"confirmation = 0 WHERE id = {id}")
        self.db.commit()

    def get_teacher_chat_id_by_hw_id(self, hw_id):
        return self.cur.execute(f"""
            SELECT t.chat_id
            FROM teacher t
            INNER JOIN course_flow cf on t.id = cf.teacher
            INNER JOIN homework h on cf.id = h.flow_id AND h.id = {hw_id}
        """).fetchone()[0]

    def get_student_chat_id_by_hw_id(self, hw_id):
        return self.cur.execute(f"""
            SELECT s.chat_id
            FROM student s
            INNER JOIN homework h on s.id = h.student_id AND h.id = {hw_id}
        """).fetchone()[0]

    def get_student_fio_by_hw_id(self, hw_id):
        return self.cur.execute(f"""
            SELECT s.full_name
            FROM student s
            INNER JOIN homework h on s.id = h.student_id AND h.id = {hw_id}
        """).fetchone()[0]

    def get_teacher_fio_by_hw_id(self, hw_id):
        return  " ".join(self.cur.execute(f"""
            SELECT t.full_name
            FROM teacher t 
            INNER JOIN course_flow cf on t.id = cf.teacher
            INNER JOIN homework h on cf.id = h.flow_id AND h.id = {hw_id}
        """).fetchone()[0].split()[1:])

    def get_lesson_number_by_hw_id(self, hw_id):
        return self.cur.execute(f"SELECT lesson_number FROM homework WHERE id = {hw_id}").fetchone()[0]

    def get_not_done_hw_id(slef, flow_id, student_chat_id):
        return list(set (slef.cur.execute(f"""
            SELECT h.id, h.lesson_number 
            FROM homework h
            INNER JOIN student s on h.student_id = s.id 
            AND h.flow_id = {flow_id} AND s.chat_id = {student_chat_id} 
            AND content_solution is null""").fetchall()))

    def get_unchecked_lessons(self, flow_id):
        list_lessons = self.cur.execute(f"""
            SELECT lesson_number FROM homework WHERE content_solution is not null 
            AND confirmation = 0 AND flow_id = {flow_id}
        """).fetchall()

        for i in range(len(list_lessons)):
            list_lessons[i] = int(list_lessons[i][0])
        list_lessons.sort()

        return list(set(list_lessons))

    def get_names_for_unchecked_hw(self, flow_id, lesson_number):
        return self.cur.execute(f"""
            SELECT s.full_name, h.id
            FROM homework h 
            INNER JOIN student s on h.student_id = s.id
            AND  h.content_solution is not null
            AND  (h.confirmation = 0 OR h.content_solution = -1) 
            AND  h.flow_id = {flow_id} AND  h.lesson_number = {lesson_number}
        """).fetchall()

    def accept_homework(self, hw_id):
        self.cur.execute(f"UPDATE homework SET confirmation = 1 WHERE id = {hw_id}")
        self.db.commit()

    def reject_homework(self, hw_id):
        self.cur.execute(f"UPDATE homework SET confirmation = -1, content_solution = null, content_type_solution = null"
                         f" WHERE id = {hw_id}")
        self.db.commit()

    def add_user_if_not_exits(self, chat_id, username):
        if self.cur.execute(f"SELECT id FROM all_users WHERE chat_id = {chat_id}").fetchone() is None:
            self.cur.execute(f"INSERT INTO all_users(chat_id, username) VALUES ({chat_id}, '@{username}')")
            self.db.commit()

    def delete_user(self, chat_id):
        self.cur.execute(f"DELETE FROM all_users WHERE chat_id = {chat_id}")
        self.db.commit()

    def get_chat_id_all_users(self):
        return self.cur.execute("SELECT chat_id FROM all_users").fetchall()