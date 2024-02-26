from openai import OpenAI
import sqlite3
import re
import requests

TOKEN = os.environment['TOKEN']                            # Вставляем свои токены от бота и от чат гпт
client = OpenAI(api_key=os.environment['api_key'])

def gpt(text: str, id: int, m_id: int):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={id}&text=Генерируется ответ♻️&reply_to_message_id={m_id}"    # Даём юзеру понять, что приняли его сообщение
        data = requests.get(url).json()
        rl = f"https://api.telegram.org/bot{TOKEN}/sendChatAction?chat_id={id}&action=typing"     # Для визуала делаем действие боту, типо он печатает, как реальный человек
        ata = requests.get(rl).json()
        
        connect = sqlite3.connect('gpt_us.db')        # Подключаемся к бд, чтобы достать последние два ответа бота. Они будут нужны для чат гпт
        cursor = connect.cursor()
        sql_query = f"""
                                SELECT con, con2 FROM ChatGPT WHERE id = '{id}'
                                """
        con = list(cursor.execute(sql_query).fetchone())[0]        # Берём два последних сообщения
        con2 = list(cursor.execute(sql_query).fetchone())[1]

        # Передаём инфу к чат гпт
        completion = client.chat.completions.create(
        model = 'gpt-3.5-turbo',        # Версию можно менять по своему усмотрению
        messages = [
            {"role": "system", "content" : "You are AI assistant of CEO of AI Automation Agency called EVOLUTE AI who gives recommendations and assist “Mukhammadali” the owner and Head of Evolute AI. Your task is to analyze information/data which will be sent to you and according to that you give actually working strategies and steps to user in order to Enhance company, You should be able to analyze even tine details before answering.The recommendations should include Steps, Time, Deadline, Digits, Caraters, Units, etc. Use clear and concise language yet friendly tone."},        # В поле content указываем "личность" бота на английском языке
            {'role': 'user', 'content': f'{text}'},        # Здесь передаётся сам запрос
            {'role': 'assistant', 'content': f'{con} {con2}'}    # Передаём контекст - последние два ответа бота
        ],
        temperature = 0.9        # Значение от 0 до 1. Отвечает за количество выразительности
        )
        ppp = re.compile('[a-zA-Z]')        # Нужно для проверки дальше
        
        english_text = completion.choices[0].message.content        # Получаем ответ нейросети на сообщение пользователя
        if ppp.match(english_text):         # Проверка на английский язык. Если нейронка вывела ответ на англе, то, возможно, это баг(так как запрос был, вероятнее всего на русском).    
            completion = client.chat.completions.create(        # Если ответ всё таки на английском, то прогоняем вновь, только без контекста. Поразительно, но работает.
            model = 'gpt-3.5-turbo',
            messages = [
                {"role": "system", "content" : "You are AI assistant of CEO of AI Automation Agency called EVOLUTE AI who gives recommendations and assist “Mukhammadali” the owner and Head of Evolute AI. Your task is to analyze information/data which will be sent to you and according to that you give actually working strategies and steps to user in order to Enhance company, You should be able to analyze even tine details before answering.The recommendations should include Steps, Time, Deadline, Digits, Caraters, Units, etc. Use clear and concise language yet friendly tone."},
                {'role': 'user', 'content': f'{text}'}
            ],
            temperature = 0.9
            )
            english_text = completion.choices[0].message.content

        try:
            sql_query = f"UPDATE ChaTGPT SET con = '{english_text}', con2 = '{con}' WHERE id = {id}"        # После обработки запроса обновляем ответы для контекста в бд 
            cursor.execute(sql_query)   
        except sqlite3.OperationalError:        # На случай ошибок
            sql_query = f"UPDATE ChaTGPT SET con = '', con2 = '{con}' WHERE id = {id}"
            cursor.execute(sql_query) 
        connect.commit()        # Сохраняем и закрываем бд
        connect.close()
        
        urll = f"https://api.telegram.org/bot{TOKEN}/deleteMessage?chat_id={id}&message_id={data['result']['message_id']}"        # Удаляем сообщение о принятии запроса пользователя
        print(requests.get(urll).json()) 
        
        mes = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={id}&text={english_text}&parse_mode=Markdown&reply_to_message_id={m_id}"        # Отсылаем юзеру ответ на его запрос
        print(requests.get(mes).json()) 
    except:        # На случай превышения лимитов запросов к api
        mess = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={id}&text=❌ Что-то пошло не так. Попробуй снова через 30 секунд&parse_mode=Markdown&reply_to_message_id={m_id}"
        print(requests.get(mess).json()) 


