import os
import requests
import json

import openai


from random import shuffle

from telebot import TeleBot, types

from speech import convert_to_wav, recognize_speech, file_duration
from config import TOKEN, openai_api_key, openai_api_url

bot = TeleBot(TOKEN)


# TODO
# 1.	Начинаем чат со слова start/
# 2.	Затем появляется выбор:
# Текст
# до 50 слов
# 51-100 слов
# 101-150 слов
# 151-200 слов
# 201-205 слов
# Свой текст (если свой, то должны будут вставить свой)
# 3.	Когда выбор сделан, то дается список текстов по каждой категории.
# 4.	Когда текст выбран, то появляется кнопка с изображением микрофона. И как-то надо дать понять, что надо читать вслух.
# 5.	После прочтения выдается анализ: скорость чтения (слов /мин), анализ правильности – вот здесь хотелось бы узнать, какие у вас предложения.
# Может появляется опять текст, и подчеркиваются и произносятся те слова, которые неправильно прочитаны.
# 6.	После анализа появляется Прочитать текст снова? Да Нет
# 7.	Для текстов, которые есть в базе, предлагаются вопросы на понимание после анализа и предложения прочитать снова. Multiple choice questions
# 8.	Анализ понимания выдается в процентном соотношении. Все правильно: 100% и т.д.
# 9.	После выдается выбор: Прочитать текст/завершить.

message_id_text = ''
list_btn = ['1-50 слов', '51-100 слов',
            '101-150 слов', '151-200 слов', '201-205 слов']

FILENAME = 'new.json'
client = openai.OpenAI(api_key=openai_api_key)


def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        assistant_reply = response['choices'][0]['message']['content']

        return assistant_reply

    except Exception as e:
        print(f"Error processing API response: {e}")

        return "An error occurred while processing the request."


class Text:
    def __init__(self, FILENAME):
        with open(FILENAME, 'r', encoding='utf-8') as f:
            self.document = json.load(f)
        self.word_count = ''
        self.name_text = ''
        self.cur_question = 0
        self.correct_ans = 0
        self.list_btns = []

    def select_text(self):
        self.text = self.document[self.word_count][self.name_text]['text']
        return self.text

    def select_list_questions(self):
        self.list_questions = self.document[self.word_count][self.name_text]['questions']
        return self.list_questions

    def next_question(self):
        self.cur_question += 1
        self.list_btns = []

    def restart(self):
        self.list_btns = []
        self.correct_ans = 0
        self.cur_question = 0
        self.word_count = ''
        self.name_text = ''

    def show_question_markup(self):
        self.question = self.select_list_questions()[self.cur_question]
        self.list_btns.append(self.question['answer'])
        for wrong in self.question['wrong']:
            self.list_btns.append(wrong)
        shuffle(self.list_btns)
        markup = types.InlineKeyboardMarkup()
        for btn in self.list_btns:
            if len(btn) > 27:
                btn = btn[:27] + '...'
            markup.add(types.InlineKeyboardButton(
                text=btn, callback_data='btn/'+btn))
        return (self.question['question'], markup)

    def check_answer(self, btn):
        if btn == self.question['answer']:
            self.correct_ans += 1

    def result(self):
        return f'Верно отвеченных {self.correct_ans} из {len(self.list_questions)-1}'

    def save_text(self, filename, text_title, text, text_questions=None):
        with open(filename, 'a', encoding='utf-8') as f:
            word_count = len(text.split())
            if not text_questions:
                new_text = {'text': text}
            else:
                lines = text.split('\n')
                result = []

                i = 0
                while i < len(lines):
                    question_line = lines[i].strip()
                    answer_lines = []
                    i += 1
                    while i < len(lines) and lines[i].startswith('Ответ: '):
                        answer_line = lines[i].replace('Ответ: ', '').strip()
                        if answer_line.endswith('+'):
                            answer_lines.append(answer_line[:-1].strip())
                        i += 1

                    question_dict = {
                        "question": question_line.replace('Вопрос: ', '').strip(),
                        "answer": answer_lines[0],
                        "wrong": answer_lines[1:]
                    }
                    result.append(question_dict)

                new_text = {'text': text, 'questions': result}

    def next_text_or_end(self):
        self.restart()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Прочитать ещё текст', callback_data='ru'),
                   types.InlineKeyboardButton('Завершить', callback_data='end'))
        return markup

    def repeat_text_markup(self):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Да', callback_data='yes'),
                   types.InlineKeyboardButton(text='Нет', callback_data='no'))
        return ('Прочитать текст снова', markup)

    def words_per_min(self, file_path, regonised_text):
        duration_min = file_duration(file_path) / 60
        len_words = len(regonised_text.split())
        return f'Количество слов в минуту: {round(len_words / duration_min)}'


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data='ru')
    btn2 = types.InlineKeyboardButton(
        text='🇬🇧 English                                       ',callback_data='en')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     "🇷🇺 Выберите язык текстов / 🇬🇧 Choose text language", reply_markup=markup)


txt = Text(FILENAME)


@bot.callback_query_handler(func=lambda call: call.data)
def text_list(call):
    global txt, message_id_text
    if call.data == 'ru':
        btns_text_list = list(txt.document.keys())
        markup = types.InlineKeyboardMarkup()
        for res in btns_text_list:
            markup.add(types.InlineKeyboardButton(
                res, callback_data='words/'+res))
        markup.add(types.InlineKeyboardButton(
            'Добавить свой текст', callback_data='add_text'))
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text='Выбор текста по кол-ву слов', reply_markup=markup)
        return
    elif call.data.split('/')[0] == 'words':
        txt.word_count = call.data.split('/')[1]
        markup = types.InlineKeyboardMarkup()
        for text in txt.document[txt.word_count]:
            if len(text) > 30:
                text = text[:30] + '...'
            markup.add(types.InlineKeyboardButton(
                text, callback_data='text/'+text))
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text='Тексты на выбор', reply_markup=markup)
        return
    elif call.data == 'add_text':
        pass

    elif call.data == 'end':
        bot.send_message(call.message.chat.id,
                         'Пока! \nЧтобы воспользоваться снова ботом /start')
        return
    elif call.data.split('/')[0] == 'text':
        sent_message_1 = call.message
        txt.name_text = call.data.split('/')[1]
        sent_message_2 = bot.send_message(call.message.chat.id,
                                          txt.select_text())
        with open('images/microphone.png', 'rb') as img:
            sent_message_3 = bot.send_photo(call.message.chat.id, img)
        message_id_text = (sent_message_1.message_id, sent_message_2.message_id,
                           sent_message_3.message_id)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text='Тексты на выбор')
        return
    elif call.data == 'yes':
        bot.send_message(call.message.chat.id, txt.text)
        return
    elif call.data == 'no':
        q, markup = txt.show_question_markup()
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text=q, reply_markup=markup)
        return
    elif call.data.split('/')[0] == 'btn':
        btn = call.data.split('/')[1]
        txt.check_answer(btn)
        if txt.cur_question < len(txt.list_questions)-1:
            txt.next_question()
            q, markup = txt.show_question_markup()
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text=q, reply_markup=markup)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text=txt.result(), reply_markup=txt.next_text_or_end())
        return


@bot.message_handler(content_types=['voice'])
def read_voice_message(message):
    global message_id_text, txt
    for mes in message_id_text:
        bot.delete_message(chat_id=message.chat.id, message_id=mes)

    file_info = bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    chat_id = message.chat.id
    message_id = message.message_id
    file_name = f"{chat_id}_{message_id}"
    voice_file = bot.download_file(file_path)
    with open(f"{file_name}.ogg", "wb") as file:
        file.write(voice_file)

    convert_to_wav(f"{file_name}.ogg", f"{file_name}.wav")

    text = recognize_speech(f"{file_name}.wav")
    bot.send_message(message.chat.id, txt.words_per_min(
        f'{file_name}.wav', text))
    # Вызов метода анализа ChatGPT generate_response
    t, markup = txt.repeat_text_markup()
    text_generate = generate_response(
        f"Напиши текстовые рекомендации, проблемные места у ученика с речью, интонацией, проанализирвов текст, который прочитал ученик. Текст был получен из перевода голосового сообщения: {text} и сравни с оригинальным {txt.text}.")

    bot.send_message(message.chat.id, text_generate)
    bot.send_message(message.chat.id, t, reply_markup=markup)

    os.remove(f"{file_name}.ogg")
    os.remove(f"{file_name}.wav")


if __name__ == '__main__':
    bot.polling(non_stop=True)
