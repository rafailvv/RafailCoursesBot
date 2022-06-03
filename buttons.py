from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

class Buttons:
    description_btn = KeyboardButton(text="📃 Описание курса")
    program_btn = KeyboardButton(text="🕖 Программа курса")
    buy_btn = KeyboardButton(text="💰 Оплатить курс")
    back_to_courses_btn = KeyboardButton(text="⬅ Список курсов")

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

    def get_confirm_and_reject(self, user_id, course_id):
        buttons = InlineKeyboardMarkup(row_width=2)
        buttons.insert(InlineKeyboardButton(text="Подтвердить", callback_data=f"Buy|Accept|{user_id}|{course_id}"))
        buttons.insert(InlineKeyboardButton(text="Отклонить", callback_data=f"Buy|Reject|{user_id}|{course_id}"))
        return buttons



