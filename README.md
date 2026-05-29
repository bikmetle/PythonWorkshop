# PythonWorkshop

Урок 1

До урока
установить python если не установлен
установить git если не установлен
почитать про git
почитать про virtual environment
почитать про .env переменные окружения


Урок
сделать ключи ssh для гит если нет 
добавить в гит ключи

перейти по ссылке гитхаб и скачать репо
git clone git@github.com:bikmetle/PythonWorkshop.git

создать свою ветку main-....
git checkout -b 'main-...'

создать ветку lesson-1-....
git checkout -b 'lession-1-...'

создать venv
python3 venv venv

активировать
venv\Scripts\activate

установить aiogram через pip
pip install aiogram

самый простой echo bot из инструкции к aiogram

получить токен от botfather
добавить токен в файл .env
добавить файл .env.example
добавить запись .env .gitignore

установить python-dotenv
pip install python-dotenv

добавить строки
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

запустить бот и проверить

коммит
git add -A && git commit -m 'название комита'

отправить на гит
git push



Урок 2
Вопросы
git
venv
.env
token



до Урока
получить апи ключи для openai

Урок
bot open ai
отвечать на текстовые вопросы
отвечать на аудио вопросы

дз
у нас есть message.text

попробовать сделать ответ на аудио сообщение
порядок такой:
из аудио транскрибировать в текст
ответить на вопрос из транскрибации




добавить sqlite подумать таблицы
изучить ответ от опен ии
добавить данные из ответа в таблицу
тестовый период пользователю


дз ключи от юкассы 
store payment info
проверять оплату и давать ответ


deploy to vps



vide code
