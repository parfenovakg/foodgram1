# praktikum_new_diplom
## Foodgram — Продуктовый помощник
Foodgram — это веб‑приложение, где пользователи могут публиковать рецепты, подписываться на других авторов, добавлять понравившиеся блюда в избранное и формировать список покупок.

## 🌍 Домен проекта

Проект развернут по адресу: [http://thisisfoodgram.myftp.org](http://thisisfoodgram.myftp.org)

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
```bash
git clone git@github.com:<USERNAME>/foodgram-project.git
cd foodgram-project
```

2. Создайте .env файл (backend/.env)
```env
SECRET_KEY=<секретный_ключ_Django>
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost,thisisfoodgram.myftp.org
CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost,http://thisisfoodgram.myftp.org
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

3. Проверьте docker-compose (пути к static/media/docs должны быть смонтированы)  
Создайте локальные директории для bind‑монтов при необходимости:
```bash
mkdir -p infra/static infra/media docs
```

4. Запуск в Docker
```bash
docker-compose up -d --build
```

5. Миграции, сбор статики и создание суперпользователя
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
docker-compose exec backend python manage.py createsuperuser
```

6. Доступ к админке (сервер)
```
http://thisisfoodgram.myftp.org/admin/
```
Создать при необходимости:
```bash
docker-compose exec backend python manage.py createsuperuser --username review --email review@admin.ru
```

7. Загрузка тестовых данных (опционально)
```bash
docker-compose exec backend python manage.py loaddata data.json
```

8. Документация API
```
http://thisisfoodgram.myftp.org/api/docs/
```
Локально (если nginx отдает docs):
```
http://localhost/api/docs/
```
Файлы документации лежат в папке docs/.

9. Обновление версии (деплой изменений)
```bash
git pull
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
```

10. Полезные команды
```bash
# логи
docker-compose logs -f backend

# перезапуск сервиса
docker-compose restart nginx

# остановка всех сервисов
docker-compose down

# очистка неиспользуемых данных
docker system prune -af
```

## Пример запросов/ответов
### Авторизация  
**Запрос**  
```http
POST /api/auth/token/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}
```
**Ответ**  
```json
{
  "auth_token": "xxxxx..."
}
```

### Получение списка рецептов  
**Запрос**  
```http
GET /api/recipes/
```
**Ответ (фрагмент)**  
```json
[
  {
    "id": 1,
    "name": "Оливье",
    "author": {"id": 2, "username": "review"},
    "tags": [{"id": 1, "name": "Салаты"}],
    "ingredients": [{"id": 5, "name": "Картофель", "amount": 3}],
    "image": "http://.../media/recipes/1.jpg",
    "text": "Классический рецепт...",
    "cooking_time": 45,
    "is_favorited": false,
    "is_in_shopping_cart": false
  }
]
```

### Добавление в избранное  
**Запрос**  
```http
POST /api/recipes/1/favorite/
```
**Ответ**  
```json
{
  "status": "added"
}
```

## Авторство
Проект разработан в рамках обучения на Яндекс.Практикум  
Автор: Парфенова Ксения  
Email: parfenovakg@yandex.ru