ID_RAFAIL = 429272623

START_TEXT = """Добро пожаловать, {}! 👋

Меня зовут <b>Рафаил</b> @rafailvv, я студент <b>Университета Иннополис</b>, одного из самых современных и лучших IT ВУЗов в России!  🔝

✅ Я… 😌
📍владею языками программирования Python, С++, Java 🤓
📍педагог доп. образования Университета Иннополис 👨‍🏫
📍финалист всероссийской олимпиады НТИ🎖
📍более 3-х лет из обычных людей делаю программистов 👨‍💻
📍собрал команду молодых амбициозных преподавателей 👨‍🎓

Мы с командой разработали программу курсов, направленная не просто на изучение сухой теории с решением однотипных задач 😒, а на <u>создание интересных и познавательных проектов</u> 😊

Выберите ниже курс чтобы узнать о нём подробнее 👇🏼
"""

COURSE_TEXT = "❗Ближайший старт курса <u>{}</u> через<b> {} {} </b>❗"

COURSES_LIST = "Выберите ниже курс чтобы узнать о нём подробнее 👇"

MY_CONTACTS = """
Telegram: @rafailvv
Тел: +7 (939) 395-41-95

С уважением,
Венедиктов Рафаил"""

BUY_COURSE_TEXT = """❗Ваша заявка на приобритение курса {} <b>зарегистрирована</b>❗

Для получения более подробной информации:""" + MY_CONTACTS

INFO_FOR_BUY_COURSE = "Пользователь <b>{}</b> @{} хочет приобрести курс <u>{}</u>"

REJECTED_TEXT = "🥲 К сожалению, ваша заявка на курс {} отклонена "
ACCEPTED_TEXT = "🥳 Поздравляем, вы зарегистрированы на курс {}"

SUCCESSFUL_PAYMENT_TEXT = "🥳 Поздравляем, курс <b>\"{}\"</b> успешно оплачен!"
SUCCESSFUL_PAYMENT_INFO_FOR_ADMIN = "Пользователь <b>{}</b> @{} оплатил курс <u>\"{}\"</u>"

FLOW_LIST_TEXT = "Выберите нужный поток 👇"

TEACHER_START_TEXT = """👋 Добро пожаловать, {}, в <b>личный кабинет преподавателя</b>!

""" + FLOW_LIST_TEXT

STUDENT_START_TEXT = """👋 Добро пожаловать, {}, в <b>личный кабинет студента</b>!

""" + FLOW_LIST_TEXT

SELECTED_FLOW_TEXT = "✔️ Поток <b>{}</b> выбран"

TIMETABLE_TEXT = """📌 <b>Расписание занятий</b>

{}"""

CONNECT_TO_LINK_TEACHER = """❗Давай скорее, ученики уже ждут тебя❗"""

CONNECT_TO_LINK_STUDENT = """❗Преподаватель будет уже совсем скоро, поэтому скроее подключайся❗"""

NOTIFICATION_STUDENT_START_LESSON_TEXT = """😱 Занятие уже начинается, скорее присоединяйся 😱"""

PERSON_INFO_TEXT = """{} <b>{}</b> 

🔑 Ник: {}
📲 Тел: {}"""

CORRECTNESS_PERSONAL_INFO = """🔎 Проверьте корректность введённых данных учащегося 👇👇👇

🔡 ФИО: {}
📲 Тел: {}
🔑 Ник: @{}

📌 Если данные введены корректно, нажмите кнопку <b>Подтвердить</b>, иначне измените некорректные данные"""

LESSON_RECORDING_FOR_STUDENT_TEXT = """🎥 Запись занятия от {} <b>{} | Урок {}</b>

{}
"""

NEW_MSG_TEXT = "Преподаватель прислал тебе сообщение 👇"

NEW_HW_TEXT = "👏 <b>{}</b> отправил тебе домашнее задание к <b>уроку {}</b>"

SOLUTION_HW_TEXT = "👏 <b>{}</b> прислал решение к домашнему заданию для <b>урока {}</b>"

ACCEPTED_HW_TEXT = "✅ <b>{}</b> <u>принял</u> твоё домашнее задание к <b>уроку {}</b>"

REJECTED_HW_TEXT = """❌ <b>{}</b> <u>не принял</u> твоё домашнее задание к <b>уроку {}</b>

📌 Комментарий от преподавателя: {}"""

NEW_UPDATE_TEXT = """❗Уважаемый пользователь, в бот <b>были внесены изменения</b>.❗

Для корректной работы бота, отправьте боту команду <b>👉/start👈</b>, кликнув не неё"""

FEEDBACK_TEXT = """Со всеми проблемами или пожеланиями обращайтесь по указанным контактам 👇
""" + MY_CONTACTS

HELP = """"Как оплатить курс?
Для оплаты курса вам необходиомо:
1. Запустить бота при помощи команды "/start"
2. Выбрать необходимый курс.
3. Далее нажать на кнопку "Оплатить курс".
4. Ввести все необходимые данные.
5. Если всё было сделано верно, вам придет сообщение с моими контактами (Звонить с до).
В течении дня я свяжусь с вами.

Как узнать Раписание?
Для того, чтобы узнать расписание вам необходимо:
1. После оплаты курса перейдите в личный кабинет студента - кнопка "Перейти в кабинет студента".
2. Далее вам придет сообщение с расписанием занятий.

Если я пропустил урок, что делать? Хочу вспомнить пройденный материал, что делать?
В этом случае предусмотренна кнопка "Записи уроков".
Для этого, вам необходимо:
1. Перейти в личный кабинет студента -  кнопка "Перейти в кабинет студента",
либо нажать на кнопку имеющегося у вас потока н-р: "Знакомство с Python".
2. Затем нажать на кнопку "Записи уроков".
3. Выбрать необходимый урок.
4. Если всё сделано верно, то вам придет видеозапись.

Как получить или отправить домашнюю работу?
Для этого, вам не обязательно связываться по телефону или ещё где-то c самим преподавателем.
Достаточно будет нажать кнопку "Домашнее задание" в личном кабинете студента.

1. Перейти в личный кабинет студента -  кнопка "Перейти в кабинет студента",
либо нажать на кнопку имеющегося у вас потока н-р: "Знакомство с Python".
2. Выбрать тот урок, по которому вы бы хотели посмотреть  домашнюю работу.
3. Приступайте к выполнению задания.
После того, как вы сделали доманюю работу, можете её отправить.
Как сделать?
1. Нажмите кнопку "Отправить на проверку",которая находится после отправленного вам задания.
2. Сами выбирайте формат домашнего задания при отправке (фото, текст в сообщении и т.д).
3. В течении 24 часов преподаватель проверит ваше домашнее задание и отправит его вам с комментариями,
указав ваши ошибки или то, какой вы всё-таки молодец".

Как подключится к занятию?
Всё очень просто:

1. Перейти в личный кабинет студента -  кнопка "Перейти в кабинет студента",
либо нажать на кнопку имеющегося у вас потока(курса) н-р: "Знакомство с Python".
2. Нажать кнопку "Подключиться к занятию".
3. Далее нажать кнопку в сообщении "Подключиться к конференции".
4. Перейдите по ссылке в Zoom.



"""