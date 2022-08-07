# Задание для стажеров на Backend
# WB—Tech


## Для запуска:

##### 1) Создайте виртуальное окружение

    python -m venv venv
    
##### 2) Активируйте виртуальное окружение

##### 3) Устанавите зависимости: 

    pip install -r requirements.txt

##### 4) Файл `example.env` переименуйте в `.env` и пропишите коннект к базе

##### 5) Выполните команду для выполнения миграций

    python manage.py deploy
    
##### 6) Создайте суперпользователя

    python manage.py createsuperuser
    
##### 7) Запустите сервер

    python manage.py runserver

