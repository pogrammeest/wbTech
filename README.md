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

    python manage.py makemigrations
    python manage.py migrate
    
##### 6) Создайте суперпользователя (Опционально)

    python manage.py createsuperuser

##### 7) Заполните бд (Опционально)

    python manage.py loaddata fixtures/profiles.json --app profiles.Profile
    python manage.py loaddata fixtures/posts.json --app posts.Post
    python manage.py loaddata fixtures/comment.json --app posts.Comment
    python manage.py loaddata fixtures/like.json --app posts.Like

    
##### 8) Запустите сервер

    python manage.py runserver


## Приложение работает на:
    http://localhost:8000

## Документация к api находится по пути 
    http://localhost:8000/swagger/

## Api находится по пути 
    http://localhost:8000/api/
