# Проект Foodgram: «Продуктовый помощник». 
[![workflow status](https://github.com/mowb5st/foodgram-project-react/actions/workflows/main.yml/badge.svg?event=push)](https://github.com/mowb5st/foodgram-project-react/actions/workflows/main.yml)
# Описание проекта
 В этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

#### В проекте два приложения:
1. core (модели рецептов, ингредиентов, тэгов, подписок, избранного, список покупок, связанные модели)
2. backend (бэкенд проекта)

### В проекте доступны Эндпойнты
| адрес                                         | метод             | описание                                                                                                                 |
|-----------------------------------------------|-------------------|--------------------------------------------------------------------------------------------------------------------------|
| api/auth/signup/                            | POST              | регистрация нового пользователя                                                                                 |
| api/auth/token/login/                          | POST              | получение токена авторизации                                                                                                      |
| api/recipes/                          | GET, POST, PATCH, DELETE | получение списка всех рецептов                                                                                                        |
| api/recipes/{id}/favorite                                | POST, DELETE    | добавить или удалить из избранного                                                                      |
| api/subscriptions/                                | GET         | получить список подписок                                                                                           |
| api/users/{2}/subscribe/                    | POST, DELETE   | подписаться или отписать от пользователя                                                                            |
| api/tags/              | GET         | получение списка всех тегов                                                                                              |
| api/ingredients/   | GET   | получение списка всех ингредиентов                                                                                      |
| api/recipes/download_shopping_cart/ | GET         | скачать список покупок |
| api/recipes/{id}/shopping_cart/ | POST, DELETE   | добавить или удалить рецепт из списка покупок                                                |


### Доступные команды
Импорт данных из csv, расположенных в папке api_yamdb/static/data. Маппинг файлов и моделей расположен внутри консольной команды.
```
python manage.py importjson
```

Генерация рецептов для заполнения БД. Необходимо указать (в целых числах) нужное количество постов и пользователей, от лица которых будут созданы посты

```
python manage.py recipegenerator 25 5
```

# Установка и запуск проекта

### Способ 1: Контейнеры Docker
В проекте в папке infra содержится конфигурация Docker-compose и nginx
Для начала необходимо скопировать проект:
```
git@github.com:mowb5st/foodgram-project-react.git
```
Перейти в папку infra:
```
cd infra
```
Запустить docker-compose:
```
docker-compose up -d
```
Выполнить миграции:
```
docker-compose backend exec python manage.py migrate
```
Отдельные ссылки для контейнеров backend и frontend соответственно:
```
docker pull mowb/backend:latest
```
```
docker pull mowb/frontend:latest
```


### Способ 2: Развернуть проект локально
Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:mowb5st/foodgram-project-react.git
```

```
cd backend
```

Cоздать и активировать виртуальное окружение:

>для Linux
> 
>```
>python3 -m venv env
>```
>```
>source env/bin/activate
>```
>```
>python3 -m pip install --upgrade pip

>для Windows
> 
>```
>python -m venv venv
>```
>```
>source venv/Scripts/activate 
>```
>```
>python -m pip install --upgrade pip

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

>для Linux
>```
>python3 manage.py migrate

>для Windows
>```
>python manage.py migrate

Запустить проект:

>для Linux
>```
>python3 manage.py runserver

>для Windows
>```
>python manage.py runserver
