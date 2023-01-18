# Homework_bot
Бот проверяет статус сданного на ревью проекта и присылает оповещения в личные сообщения в telegram

## Технологии
+ Python
+ Python-telegram-bot

## Как запустить проект

+ Клонировать репозиторий и перейти в него в командной строке

``` 
git clone <ссылка>
```

```
cd homework_bot
```

+ Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

+ Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

+ Получить токен API Практикум.Домашка по [ссылке](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a)

+ В файл .env добавить токены:
```
PRACTICUM_TOKEN=токен API Практикум.Домашка
TELEGRAM_TOKEN=ваш телеграм токен
TELEGRAM_CHAT_ID=телеграм токен бота
```

+ Запустить проект:

```
python homework.py 
```

## Об авторе

Игорь Дягилев

## Контакты
+ I.diagilev@gmail.com
