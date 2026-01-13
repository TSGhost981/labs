import sqlite3
import threading
import time
import json
import requests

# Ваш токен
TOKEN = '7612529764:AAHz1cFYDdrw5-VQ0xcpgX-R4Dg0IbvG4P8'
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'

# Блокировка для потокобезопасности
db_lock = threading.Lock()


# База данных для избранного
class SimpleDatabase:
    def __init__(self):
        with db_lock:
            self.conn = sqlite3.connect('dicaprio_favorites.db', check_same_thread=False)
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites 
                (user_id INTEGER, film_id TEXT, PRIMARY KEY (user_id, film_id))
            ''')
            self.conn.commit()

    def toggle_favorite(self, user_id, film_id):
        with db_lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM favorites WHERE user_id=? AND film_id=?",
                           (user_id, film_id))
            if cursor.fetchone():
                cursor.execute("DELETE FROM favorites WHERE user_id=? AND film_id=?",
                               (user_id, film_id))
                action = "removed"
            else:
                cursor.execute("INSERT INTO favorites VALUES (?, ?)",
                               (user_id, film_id))
                action = "added"
            self.conn.commit()
            return action

    def get_favorites(self, user_id):
        with db_lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT film_id FROM favorites WHERE user_id=?", (user_id,))
            return [row[0] for row in cursor.fetchall()]


db = SimpleDatabase()

FILMS = {
    'titanic': {
        'name': 'Титаник (Titanic)',
        'year': 1997,
        'genre': 'Драма, романтика',
        'duration': '195 мин',
        'rating': '7.9/10 IMDb',
        'desc': 'Эпическая история любви на фоне гибели самого известного корабля в истории. Леонардо ДиКаприо в роли Джека Доусона.',
        'cast': 'Леонардо ДиКаприо, Кейт Уинслет, Билли Зейн',
        'awards': '11 премий Оскар',
        'director': 'Джеймс Кэмерон'
    },
    'inception': {
        'name': 'Начало (Inception)',
        'year': 2010,
        'genre': 'Научная фантастика, триллер',
        'duration': '148 мин',
        'rating': '8.8/10 IMDb',
        'desc': 'Криминальный триллер о проникновении в подсознание. ДиКаприо играет Дома Кобба, вора, крадущего идеи из снов.',
        'cast': 'Леонардо ДиКаприо, Джозеф Гордон-Левитт, Эллен Пейдж',
        'awards': '4 премии Оскар',
        'director': 'Кристофер Нолан'
    },
    'wolf_wallstreet': {
        'name': 'Волк с Уолл-стрит (The Wolf of Wall Street)',
        'year': 2013,
        'genre': 'Биография, комедия, криминал',
        'duration': '180 мин',
        'rating': '8.2/10 IMDb',
        'desc': 'Экранизация биографии брокера Джордана Белфорта. ДиКаприо в одной из своих самых ярких ролей.',
        'cast': 'Леонардо ДиКаприо, Джона Хилл, Марго Робби',
        'awards': '5 номинаций на Оскар',
        'director': 'Мартин Скорсезе'
    },
    'revenant': {
        'name': 'Выживший (The Revenant)',
        'year': 2015,
        'genre': 'Приключения, драма, вестерн',
        'duration': '156 мин',
        'rating': '8.0/10 IMDb',
        'desc': 'История выживания охотника Хью Гласса в суровых условиях дикой природы Америки 1820-х годов.',
        'cast': 'Леонардо ДиКаприо, Том Харди, Донал Глисон',
        'awards': 'Оскар за лучшую мужскую роль',
        'director': 'Алехандро Г. Иньярриту'
    },
    'departed': {
        'name': 'Отступники (The Departed)',
        'year': 2006,
        'genre': 'Криминал, триллер, драма',
        'duration': '151 мин',
        'rating': '8.5/10 IMDb',
        'desc': 'Триллер о полицейском под прикрытием и кроте в полиции. ДиКаприо играет детектива Билли Костигана.',
        'cast': 'Леонардо ДиКаприо, Мэтт Дэймон, Джек Николсон',
        'awards': '4 премии Оскар',
        'director': 'Мартин Скорсезе'
    },
    'great_gatsby': {
        'name': 'Великий Гэтсби (The Great Gatsby)',
        'year': 2013,
        'genre': 'Драма, романтика',
        'duration': '143 мин',
        'rating': '7.2/10 IMDb',
        'desc': 'Экранизация классического романа Ф.С. Фицджеральда. ДиКаприо в роли загадочного миллионера Джея Гэтсби.',
        'cast': 'Леонардо ДиКаприо, Кэри Маллиган, Тобей Магуайр',
        'awards': '2 премии Оскар',
        'director': 'Баз Лурман'
    },
    'catch_me_if_you_can': {
        'name': 'Поймай меня, если сможешь (Catch Me If You Can)',
        'year': 2002,
        'genre': 'Биография, криминал, драма',
        'duration': '141 мин',
        'rating': '8.1/10 IMDb',
        'desc': 'История Фрэнка Абигнейла-младшего, гениального мошенника, выдававшего себя за пилота, врача и адвоката.',
        'cast': 'Леонардо ДиКаприо, Том Хэнкс, Кристофер Уокен',
        'awards': '2 номинации на Оскар',
        'director': 'Стивен Спилберг'
    },
    'avita': {
        'name': 'Авиатор (The Aviator)',
        'year': 2004,
        'genre': 'Биография, драма',
        'duration': '170 мин',
        'rating': '7.5/10 IMDb',
        'desc': 'Биографический фильм о Говарде Хьюзе, эксцентричном миллионере, авиаторе и кинорежиссере.',
        'cast': 'Леонардо ДиКаприо, Кейт Бланшетт, Кейт Бекинсейл',
        'awards': '5 премий Оскар',
        'director': 'Мартин Скорсезе'
    }
}


class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f'https://api.telegram.org/bot{token}'
        self.offset = 0

    def send_message(self, chat_id, text, reply_markup=None):
        url = f'{self.base_url}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }

        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)

        response = requests.post(url, json=data)
        return response.json()

    def edit_message_text(self, chat_id, message_id, text, reply_markup=None):
        url = f'{self.base_url}/editMessageText'
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML'
        }

        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)

        response = requests.post(url, json=data)
        return response.json()

    def answer_callback_query(self, callback_query_id, text=None):
        url = f'{self.base_url}/answerCallbackQuery'
        data = {
            'callback_query_id': callback_query_id
        }
        if text:
            data['text'] = text

        response = requests.post(url, json=data)
        return response.json()

    def get_updates(self):
        url = f'{self.base_url}/getUpdates'
        params = {'offset': self.offset, 'timeout': 30}

        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json().get('result', [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения обновлений: {e}")
        return []

    def process_updates(self, updates):
        for update in updates:
            self.offset = update['update_id'] + 1

            if 'message' in update:
                self.handle_message(update['message'])
            elif 'callback_query' in update:
                self.handle_callback_query(update['callback_query'])

    def handle_message(self, message):
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        user_name = message['from'].get('first_name', 'Пользователь')

        if 'text' in message:
            text = message['text']

            if text == '/start' or text == '/start@your_bot_name':
                self.send_start(chat_id, user_name)
            elif text == '/help':
                self.send_help(chat_id)
            elif text == '/films':
                self.show_films(chat_id)
            elif text == '/fav':
                self.show_favorites(chat_id, user_id)
            elif text == '/dicaprio':
                self.send_dicaprio_info(chat_id)
            elif text == '🎥 Фильмы':
                self.show_films(chat_id)
            elif text == '⭐ Избранное':
                self.show_favorites(chat_id, user_id)
            elif text == '🏆 Об актере':
                self.send_dicaprio_info(chat_id)
            elif text == '❓ Помощь':
                self.send_help(chat_id)
            else:
                self.send_message(chat_id, "Используйте команды или кнопки внизу.")

    def handle_callback_query(self, callback_query):
        callback_id = callback_query['id']
        user_id = callback_query['from']['id']
        data = callback_query['data']
        message = callback_query['message']
        chat_id = message['chat']['id']
        message_id = message['message_id']

        try:
            if data.startswith("info_"):
                film_id = data.split("_")[1]
                self.show_film_info(chat_id, message_id, film_id, user_id)
            elif data.startswith("fav_"):
                film_id = data.split("_")[1]
                self.toggle_favorite(callback_id, chat_id, message_id, film_id, user_id)
            elif data == "back_to_list":
                self.back_to_list(chat_id, message_id)
        except Exception as e:
            print(f"Ошибка обработки callback: {e}")
            self.answer_callback_query(callback_id, "Ошибка при обработке")

    def send_start(self, chat_id, user_name):
        text = f"🎬 Привет, {user_name}!\n\n"
        text += "Это бот с фильмами Леонардо ДиКаприо!\n\n"
        text += "📌 <b>Основные команды:</b>\n"
        text += "/films - все фильмы ДиКаприо\n"
        text += "/fav - ваше избранное\n"
        text += "/dicaprio - информация об актере\n"
        text += "/help - помощь\n\n"
        text += "Или используйте кнопки ниже ⬇️"

        reply_markup = {
            'keyboard': [
                [{'text': '🎥 Фильмы'}, {'text': '⭐ Избранное'}],
                [{'text': '🏆 Об актере'}, {'text': '❓ Помощь'}]
            ],
            'resize_keyboard': True,
            'one_time_keyboard': False
        }

        self.send_message(chat_id, text, reply_markup)

    def send_help(self, chat_id):
        text = "🎭 <b>Фильмы Леонардо ДиКаприо</b>\n\n"
        text += "📌 <b>Доступные команды:</b>\n\n"
        text += "/start - начать работу\n"
        text += "/films - показать все фильмы\n"
        text += "/fav - показать избранные фильмы\n"
        text += "/dicaprio - информация об актере\n"
        text += "/help - эта справка\n\n"
        text += "🎬 <b>Леонардо ДиКаприо</b> - американский актер, продюсер и активист.\n"
        text += "Лауреат премии Оскар (2016), трехкратный номинант на Золотой глобус.\n\n"
        text += "Используйте кнопки внизу для удобной навигации."

        self.send_message(chat_id, text)

    def send_dicaprio_info(self, chat_id):
        text = "🏆 <b>Леонардо ДиКаприо</b>\n\n"
        text += "🔸 <b>Полное имя:</b> Леонардо Вильгельм ДиКаприо\n"
        text += "🔸 <b>Дата рождения:</b> 11 ноября 1974 года\n"
        text += "🔸 <b>Место рождения:</b> Лос-Анджелес, США\n"
        text += "🔸 <b>Карьера:</b> Актер, продюсер\n"
        text += "🔸 <b>Награды:</b> Оскар, BAFTA, Золотой глобус\n\n"
        text += "📌 <b>Ключевые фильмы:</b>\n"
        text += "• Титаник (1997) - мировая слава\n"
        text += "• Выживший (2015) - Оскар\n"
        text += "• Волк с Уолл-стрит (2013)\n"
        text += "• Начало (2010)\n"
        text += "• Отступники (2006)\n\n"
        text += "🌱 <b>Активизм:</b> Основатель фонда по защите окружающей среды."

        self.send_message(chat_id, text)

    def show_films(self, chat_id):
        keyboard = []
        for film_id, film in FILMS.items():
            keyboard.append([{
                'text': f"🎬 {film['name']} ({film['year']})",
                'callback_data': f"info_{film_id}"
            }])

        reply_markup = {
            'inline_keyboard': keyboard
        }

        self.send_message(chat_id, "🎥 Выберите фильм с Леонардо ДиКаприо:", reply_markup)

    def show_favorites(self, chat_id, user_id):
        favorites = db.get_favorites(user_id)

        if not favorites:
            self.send_message(chat_id, "⭐ У вас пока нет избранных фильмов.")
            return

        text = "⭐ <b>Ваши избранные фильмы:</b>\n\n"
        for film_id in favorites:
            film = FILMS.get(film_id)
            if film:
                text += f"🎬 {film['name']} ({film['year']})\n"

        self.send_message(chat_id, text)

    def show_film_info(self, chat_id, message_id, film_id, user_id):
        film = FILMS.get(film_id)
        if not film:
            self.edit_message_text(chat_id, message_id, "Фильм не найден")
            return

        favorites = db.get_favorites(user_id)

        text = f"🎬 <b>{film['name']}</b>\n\n"
        text += f"📅 <b>Год:</b> {film['year']}\n"
        text += f"🎭 <b>Жанр:</b> {film['genre']}\n"
        text += f"⏱ <b>Длительность:</b> {film['duration']}\n"
        text += f"⭐ <b>Рейтинг:</b> {film['rating']}\n"
        text += f"🎬 <b>Режиссер:</b> {film['director']}\n"
        text += f"🏆 <b>Награды:</b> {film['awards']}\n\n"
        text += f"👥 <b>Актерский состав:</b>\n{film['cast']}\n\n"
        text += f"📝 <b>Описание:</b>\n{film['desc']}"

        keyboard = []

        if film_id in favorites:
            keyboard.append([{
                'text': "❌ Убрать из избранного",
                'callback_data': f"fav_{film_id}"
            }])
        else:
            keyboard.append([{
                'text': "⭐ Добавить в избранное",
                'callback_data': f"fav_{film_id}"
            }])

        keyboard.append([{
            'text': "🔙 Назад к списку",
            'callback_data': "back_to_list"
        }])

        reply_markup = {
            'inline_keyboard': keyboard
        }

        self.edit_message_text(chat_id, message_id, text, reply_markup)

    def toggle_favorite(self, callback_id, chat_id, message_id, film_id, user_id):
        try:
            action = db.toggle_favorite(user_id, film_id)
            film = FILMS.get(film_id)
            film_name = film['name'] if film else "Фильм"

            if action == "added":
                self.answer_callback_query(callback_id, f"⭐ '{film_name}' добавлен в избранное")
            else:
                self.answer_callback_query(callback_id, f"❌ '{film_name}' удален из избранного")

            self.show_film_info(chat_id, message_id, film_id, user_id)
        except Exception as e:
            print(f"Ошибка в toggle_favorite: {e}")
            self.answer_callback_query(callback_id, "Ошибка при обновлении избранного")

    def back_to_list(self, chat_id, message_id):
        keyboard = []
        for film_id, film in FILMS.items():
            keyboard.append([{
                'text': f"🎬 {film['name']} ({film['year']})",
                'callback_data': f"info_{film_id}"
            }])

        reply_markup = {
            'inline_keyboard': keyboard
        }

        self.edit_message_text(
            chat_id,
            message_id,
            "🎥 Выберите фильм с Леонардо ДиКаприо:",
            reply_markup
        )

    def run(self):
        print("🎭 Бот с фильмами Леонардо ДиКаприо запущен. Нажмите Ctrl+C для остановки.")

        while True:
            try:
                updates = self.get_updates()
                if updates:
                    self.process_updates(updates)
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("\n📴 Бот остановлен")
                break
            except Exception as e:
                print(f"Ошибка в основном цикле: {e}")
                time.sleep(5)


# Запуск бота
if __name__ == "__main__":
    bot = TelegramBot(TOKEN)
    bot.run()