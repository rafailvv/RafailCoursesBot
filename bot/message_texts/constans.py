def get_text_by_key(input):
    text = {}
    with open('bot/message_texts/text.txt', 'r', encoding='utf-8') as fi:
        all_text = fi.read().split("---")
    for el in all_text:
        el= el.strip().split('=')
        text[el[0]] = el[1]

    return text[input]

ID_RAFAIL = 429272623