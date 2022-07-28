from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date


class Buttons:
    description_btn = KeyboardButton(text="📃 Описание курса")
    program_btn = KeyboardButton(text="📆 Программа курса")
    buy_btn = KeyboardButton(text="💰 Оплатить курс")
    back_to_courses_btn = KeyboardButton(text="⬅ Список курсов")
    connect_to_chat = KeyboardButton(text="💬 Подключиться к чату")

    lesson_link_btn = KeyboardButton(text="🔉 Подключиться к занятию")
    lesson_video_btn = KeyboardButton(text="🎥 Записи уроков")
    student_list_btn = KeyboardButton(text="👨‍🎓 Список учащихся")
    check_homework_btn = KeyboardButton(text="💌 Домашнее задание")
    back_to_flow_btn = KeyboardButton(text="⬅ Список потоков")

    teacher_info_btn = KeyboardButton(text="👨‍🏫 Связаться с преподавателем")

    student_account_btn = KeyboardButton(text="👨‍🎓 Перейти в кабинет студента")
    send_homework_btn = KeyboardButton(text="📩 Домашние задания")
    feedback_btn = KeyboardButton(text = "📢 Обратная связь")

    def __init__(self, db):
        self.db = db

    def get_courses_buttons(self, is_student=False):
        buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for course_name in self.db.get_courses_name():
            buttons.insert(KeyboardButton(text=course_name))
        if is_student:
            buttons.add(self.student_account_btn)
        return buttons

    def in_course(self, is_student):
        buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons.insert(self.description_btn)
        buttons.insert(self.program_btn)
        buttons.insert(self.buy_btn)
        buttons.add(self.back_to_courses_btn)
        if is_student:
            buttons.add(self.student_account_btn)
        return buttons

    def get_confirm_and_reject(self, chat_id, course_id, student_id):
        buttons = InlineKeyboardMarkup(row_width=2)
        buttons.insert(
            InlineKeyboardButton(text="Подтвердить", callback_data=f"Buy|Accept|{chat_id}|{course_id}|{student_id}"))
        buttons.insert(
            InlineKeyboardButton(text="Отклонить", callback_data=f"Buy|Reject|{chat_id}|{course_id}|{student_id}"))
        return buttons

    def get_buttons_after_payment(self):
        buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons.insert(self.connect_to_chat)
        buttons.insert(self.back_to_courses_btn)
        return buttons

    def get_flow_for_teacher(self, id):
        buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        for name, start_date, finish_date in self.db.get_further_flows_for_teacher(id):
            buttons.insert(KeyboardButton(text=f"{name} | {start_date} - {finish_date}"))
        return buttons

    def get_flow_for_student(self, id):
        buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        for name, start_date, finish_date in self.db.get_current_flows_for_student(id):
            buttons.insert(KeyboardButton(text=f"{name} | {start_date} - {finish_date}"))
        buttons.insert(self.back_to_courses_btn)
        return buttons

    def in_flow_teacher(self):
        buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons.insert(self.lesson_link_btn)
        buttons.insert(self.lesson_video_btn)
        buttons.insert(self.student_list_btn)
        buttons.insert(self.check_homework_btn)
        buttons.add(self.back_to_flow_btn)
        return buttons

    def in_flow_student(self):
        buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons.insert(self.lesson_link_btn)
        buttons.insert(self.lesson_video_btn)
        buttons.insert(self.teacher_info_btn)
        buttons.insert(self.send_homework_btn)
        buttons.insert(self.back_to_flow_btn)
        buttons.insert(self.feedback_btn)
        return buttons

    def get_students_names_in_flow(self, flow_id, topic):
        buttons = InlineKeyboardMarkup(row_width=1)
        for name, id in self.db.get_list_students_by_flow_id(flow_id):
            buttons.insert(InlineKeyboardButton(text=name, callback_data=f"{topic}|{id}"))
        return buttons

    def get_students_list_in_flow(self, flow_id):
        buttons = self.get_students_names_in_flow(flow_id, "Student")
        buttons.insert(InlineKeyboardButton(text="Сообщение всем студентам", callback_data=f"SendAll|send"))
        return buttons

    def get_link_to_lesson(self, flow_id):
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.insert(InlineKeyboardButton("Подключиться к конференции", url=self.db.get_link_by_flow_id(flow_id)))
        return buttons

    def how_find_username(self):
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.insert(InlineKeyboardButton("Как узнать какой ник?",
                                            url="https://ustanovkaos.ru/obshchenie/kak-uznat-svoj-nik-v-telegramme.html"))
        return buttons

    def edit_personal_info(self):
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.insert(InlineKeyboardButton("✏ Изменить ФИО", callback_data="PersInfo|fio"))
        buttons.insert(InlineKeyboardButton("✏ Изменить номер телефона", callback_data="PersInfo|phone"))
        buttons.insert(InlineKeyboardButton("✏ Изменить ник", callback_data="PersInfo|username"))
        buttons.insert(InlineKeyboardButton("✅ Подтвердить", callback_data="PersInfo|accept"))
        return buttons

    def edit_recording_info(self):
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.insert(InlineKeyboardButton("✏ Изменить видеозапись", callback_data="Record|video"))
        buttons.insert(InlineKeyboardButton("✏ Изменить описание", callback_data="Record|description"))
        buttons.insert(InlineKeyboardButton("✅ Подтвердить", callback_data="Record|accept"))
        return buttons

    def edit_message(self, topic):
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.insert(InlineKeyboardButton("✏ Изменить содержимое", callback_data=f"{topic}|edit"))
        buttons.insert(InlineKeyboardButton("✅ Подтвердить", callback_data=f"{topic}|accept"))
        return buttons

    def get_button_to_student_page(self):
        buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons.insert(self.student_account_btn)
        return buttons

    def get_recorded_lessons(self, flow_id):
        buttons = InlineKeyboardMarkup(row_width=2)
        for lesson_number, id in self.db.get_id_recordings_by_flow_id(flow_id):
            buttons.insert(InlineKeyboardButton(text=f"Урок {lesson_number}", callback_data=f"RecLesson|{id}"))
        return buttons

    def message_types(self):
        buttons = InlineKeyboardMarkup(row_width=2)
        buttons.insert(InlineKeyboardButton(text="📝 Текст 📝", callback_data="SendAll|text.txt"))
        buttons.insert(InlineKeyboardButton(text="✉ Документ ✉", callback_data="SendAll|document"))
        buttons.insert(InlineKeyboardButton(text="🖼 Картнику 🖼", callback_data="SendAll|image"))
        buttons.insert(InlineKeyboardButton(text="🎞 Видеозапись 🎞", callback_data="SendAll|video"))
        return buttons

    def home_action_selection(self):
        buttons = InlineKeyboardMarkup(row_width=2)
        buttons.insert(InlineKeyboardButton(text="Проверить", callback_data="HW_T|check"))
        buttons.insert(InlineKeyboardButton(text="Назначить", callback_data="HW_T|assign"))
        return buttons

    def get_past_lessons(self, flow_id):
        buttons = InlineKeyboardMarkup(row_width=2)
        for i in self.db.get_past_lessons_numbers(flow_id):
            buttons.insert(InlineKeyboardButton(text=f"Урок {i[0]}", callback_data=f"HW_T|num_les {i[0]}"))
        return buttons

    def get_show_hw(self, hw_id):
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.insert(InlineKeyboardButton(
            text="Показать",
            callback_data=f"HW_S|show|{hw_id}"))
        return buttons

    def get_show_hw_solution(self, hw_id):
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.insert(InlineKeyboardButton(
            text="Показать",
            callback_data=f"HW_T|solution|{hw_id}"))
        return buttons

    def get_student_send_hw(self, hw_id):
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.insert(InlineKeyboardButton(text="Отправить на проверку", callback_data=f"HW_S|for_confirm|{hw_id}"))
        return buttons

    def get_confirmation(self, hw_id):
        buttons = InlineKeyboardMarkup(row_width=2)
        buttons.insert(InlineKeyboardButton(text="Подтвердить", callback_data=f"HW_T|conf|acp|{hw_id}"))
        buttons.insert(InlineKeyboardButton(text="Отклонить", callback_data=f"HW_T|conf|rej|{hw_id}"))
        return buttons

    def get_not_done_hw(self, flow_id, student_chat_id):
        buttons = InlineKeyboardMarkup(row_width=2)
        for hw_id, lesson_number in self.db.get_not_done_hw_id(flow_id,student_chat_id):
            buttons.insert(InlineKeyboardButton(text=f"Урок {lesson_number}", callback_data=f"HW_S|show|{hw_id}"))
        return buttons

    def get_unchecked_lessons(self, flow_id):
        buttons = InlineKeyboardMarkup(row_width=2)
        for lesson_number in self.db.get_unchecked_lessons(flow_id):
            buttons.insert(InlineKeyboardButton(text=f"Урок {lesson_number}", callback_data=f"HW_T|checkles|{lesson_number}"))
        return buttons

    def get_names_unchecked_lessons(self, flow_id, lesson_number):
        buttons = InlineKeyboardMarkup(row_width=1)
        for name, hw_id in self.db.get_names_for_unchecked_hw(flow_id,lesson_number):
            buttons.insert(InlineKeyboardButton(text=f"{name}", callback_data=f"HW_T|solution|{hw_id}"))
        return buttons
