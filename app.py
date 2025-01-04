import kivy
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import ScrollView
from kivy.clock import Clock
from dotenv import load_dotenv
import requests
import os
import math

os.environ.clear()
load_dotenv(".venv/.env")

# получим переменные окружения из .env
vsegpt = os.environ.get("OPENAI_URL")
# API-key
api_key = os.environ.get("OPENAI_API_KEY")

KV = '''
BoxLayout:
    orientation: 'vertical'

    ScrollView:
        MDBoxLayout:
            id: chat_layout
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height  # Устанавливаем высоту равной минимальной высоте содержимого
            padding: 10
            spacing: 10

    MDBoxLayout:
        size_hint_y: None
        height: '60dp'  # Установите фиксированную высоту для нового Horizontal BoxLayout
        padding: 10
        spacing: 10

        MDTextField:
            id: user_input
            hint_text: "Введите сообщение"
            mode: "rectangle"
            multiline: False
            on_text_validate: app.send_message()

        MDRaisedButton:
            text: "Отправить"
            on_release: app.send_message()
'''

system_prompt = '''
    Ты - большая языковая модель. Отвечай на вопросы пользователя честно и прямо. Ответ пиши в информационном стиле:
    Исключить клише, газетные, корпоративные, канцелярские, бытовые штампы, указания на настоящее время,
    формализмы, неопределенности, эвфемизмы, вводные слова и выражения и сослагательные наклонения.
    Оценочные выражения дополнить фактами или цифрами, иначе исключить.
'''


class ChatApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def send_message(self):
        user_input = self.root.ids.user_input
        message = user_input.text
        if message:
            self.add_message("Вы: " + message, "user")
            user_input.text = ""
            self.get_response(system_prompt, message)

    def add_message(self, text, sender="user"):
        bubble = MDBoxLayout(
            orientation="vertical",
            padding="10dp",
            spacing="5dp",
            size_hint_x=0.8,
            adaptive_height=True,
            md_bg_color=(0.9, 0.9, 1, 1) if sender == "user" else (0.9, 1, 0.9, 1),
            radius=[15, 15, 15, 15],
            pos_hint={"right": 1} if sender == "user" else {"left": 1}
        )
        label = MDLabel(
            text=text,
            halign="left",
            theme_text_color="Primary",
            size_hint_y=None,
            padding=(10, 10),
            text_size=(self.root.width * 0.75, None),
            adaptive_height=True
        )
        label.bind(texture_size=label.setter("size"))
        bubble.add_widget(label)
        self.root.ids.chat_layout.add_widget(bubble)

        # Автоматическая прокрутка вниз после добавления нового сообщения
        Clock.schedule_once(self.scroll_to_bottom, 0.1)

    def scroll_to_bottom(self, *args):
        scroll_view = self.root.children[1]  # Получаем ScrollView
        scroll_view.scroll_y = 0  # Прокрутка к нижней части ScrollView

    def get_response(self, system, message):
        # Формируем данные для POST-запроса

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai/gpt4-o-mini",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": message}
            ]
        }

        try:
            # Отправляем POST-запрос к модели
            response = requests.post("https://api.vsegpt.ru/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()  # Проверка на наличие ошибок в запросе

            # Получаем ответ от модели
            response_data = response.json()
            bot_message = response_data['choices'][0]['message']['content']

            # Добавляем ответ бота в чат
            self.add_message("ChatGPT: " + bot_message, "ChatGPT")

        except Exception as e:
            print(f"Error occurred: {e}")
            self.add_message(f"Ошибка {e}: Не удалось получить ответ", "ChatGPT")


if __name__ == "__main__":
    ChatApp().run()