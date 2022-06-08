from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date

class Buttons:
    description_btn = KeyboardButton(text="📃 Описание курса")
    program_btn = KeyboardButton(text="📆 Программа курса")
    buy_btn = KeyboardButton(text="💰 Оплатить курс")
    back_to_courses_btn = KeyboardButton(text="⬅ Список курсов")
    connect_to_chat = KeyboardButton(text="💬 Подключиться к чату")

    lesson_link_btn = KeyboardButton(text="🔉 Подключиться к занятию")
    student_list_btn = KeyboardButton(text = "👨‍🎓 Список учащихся")
    lesson_video_btn = KeyboardButton(text= "🎥 Запись урока")
    back_to_flow_btn = KeyboardButton(text="⬅ Список потоков")

    def __init__(self, db):
        self.db = db

    def get_courses_buttons(self):
        buttons = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        for course_name in self.db.get_courses_name():
            buttons.insert(KeyboardButton(text=course_name))
        return buttons

    def in_course(self):
        buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons.insert(self.description_btn)
        buttons.insert(self.program_btn)
        buttons.insert(self.buy_btn)
        buttons.add(self.back_to_courses_btn)
        return buttons

    def get_confirm_and_reject(self, chat_id, course_id, student_id):
        buttons = InlineKeyboardMarkup(row_width=2)
        buttons.insert(InlineKeyboardButton(text="Подтвердить", callback_data=f"Buy|Accept|{chat_id}|{course_id}|{student_id}"))
        buttons.insert(InlineKeyboardButton(text="Отклонить", callback_data=f"Buy|Reject|{chat_id}|{course_id}|{student_id}"))
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
        return buttons

    def in_flow(self):
        buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons.insert(self.lesson_link_btn)
        buttons.insert(self.lesson_video_btn)
        buttons.insert(self.student_list_btn)
        buttons.add(self.back_to_flow_btn)
        return buttons

    def get_students_names_in_flow(self, flow_id):
        buttons = InlineKeyboardMarkup(row_width=1)
        for name, chat_id in self.db.get_list_students_by_flow_id(flow_id):
            buttons.insert(InlineKeyboardButton(text=name, callback_data=chat_id))
        return buttons

    def get_link_to_lesson(self, flow_id):
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.insert(InlineKeyboardButton("Подключиться к конференции", url=self.db.get_link_by_flow_id(flow_id)))
        return buttons

    def how_find_username(self):
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.insert(InlineKeyboardButton("Как узнать какой ник?", url="https://ustanovkaos.ru/obshchenie/kak-uznat-svoj-nik-v-telegramme.html"))
        return buttons

    def edit_personal_info(self):
        buttons = InlineKeyboardMarkup(row_width=1)
        buttons.insert(InlineKeyboardButton("✏ Изменить ФИО", callback_data="PersInfo|fio"))
        buttons.insert(InlineKeyboardButton("✏ Изменить номер телефона", callback_data="PersInfo|phone"))
        buttons.insert(InlineKeyboardButton("✏ Изменить ник", callback_data="PersInfo|username"))
        buttons.insert(InlineKeyboardButton("✅ Подтвердить", callback_data="PersInfo|accept"))
        return buttons

