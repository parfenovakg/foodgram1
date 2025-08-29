# praktikum_new_diplom
## Foodgram — Продуктовый помощник
Foodgram — это веб‑приложение, где пользователи могут публиковать рецепты, подписываться на других авторов, добавлять понравившиеся блюда в избранное и формировать список покупок.

### Возможности
- Регистрация и аутентификация пользователей
- Публикация, редактирование и удаление рецептов с фото
- Добавление рецептов в избранное
- Подписка на авторов
- Автоматическая генерация списка покупок по выбранным рецептам
- Пагинация и удобная API‑структура

### Стек технологий
Backend: Python, Django, Django REST Framework
База данных: PostgreSQL
Контейнеризация: Docker

### Установка и запуск
1. Клонируйте репозиторий
git clone git@github.com:<USERNAME>/foodgram-project.git cd foodgram-project

2. Создайте .env файл
SECRET_KEY=<секретный_ключ_Django>
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db DB_PORT=5432

4. Запуск в Docker
docker-compose up -d --build

5. Миграции, сбор статики и создание суперпользователя
docker-compose exec backend python manage.py migrate docker-compose exec backend python manage.py collectstatic --noinput docker-compose exec backend python manage.py createsuperuser

# Сайт доступен по адресу https://thisisfoodgram.myftp.org/
