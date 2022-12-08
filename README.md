# Homework_bot
### Описание
Telegram-бот, обращающийся к API сервиса Практикум.Домашка и сообщающий статус проверки домашней работы.
### Запуск проекта в dev-режиме
Клонируем репозиторий на свой компьютер
```
git clone https://github.com/Pash1et/homework_bot.git
```
Переходим в папку с файлом и устанавливаем виртуальное окружение
```
python -m venv venv
```
Активируем виртуальное окружение
```
source venv/script/Activate
```
В файле homework.py необходимо заполнить переменные окружения своими данными  
```
PRACTICUM_TOKEN = ...  
TELEGRAM_TOKEN = ...  
TELEGRAM_CHAT_ID = ...
```
В параметре `RETRY_TIME` можно установить частоту запросов к API в секундах

Запуск проекта 
```
python homework.py
```
