# Django Messaging Service 🚀

Современный корпоративный SaaS-сервис (MVP) для управления клиентами и автоматизации email-рассылок. Проект разработан с использованием ролевой модели доступа, отказоустойчивого SMTP-логирования и производительного серверного кэширования.

## 🛠 Стек технологий
* **Backend:** Python 3.12+, Django 6.0 (CBV, Django ORM)
* **Database:** PostgreSQL (реляционная СУБД)
* **Caching & NoSQL:** Redis (высокопроизводительный сервер кэширования)
* **Dependency Management:** Poetry 2.4+ (пакетный менеджер)
* **Code Quality & Linter:** Ruff (форматтер и линтер), Mypy (статистический анализатор типов)
* **Frontend:** HTML5, CSS3, Bootstrap 5.3 (локальное подключение статики)

---

## 🔑 Ключевой функционал
1. **Управление клиентами (CRUD):** Возможность добавления, редактирования и удаления получателей рассылок. Пользователи изолированы (каждый видит только свою базу).
2. **Ядро рассылок:** Создание шаблонов сообщений, настройка интервалов отправки (`start_time`/`end_time`) со строгой валидацией дат и автоматическим расчетом статусов.
3. **Отказоустойчивый SMTP-движок:** Отправка писем через встроенный SMTP-клиент. Все сетевые ошибки или успешные факты доставки логируются в модель `MailingAttempt` через блоки `try-except` (база данных не падает при сбое сети).
4. **Регистрация и кастомная аутентификация:** Вход по `Email` вместо `username`. Реализована верификация аккаунтов через одноразовые токены, отправляемые по ссылке на почту, а также полноценный цикл сброса и восстановления пароля.
5. **Ролевая модель (Группы Django):** 
   * **Пользователи:** Полный контроль только над своими клиентами и рассылками.
   * **Менеджеры (Группа `Менеджеры`):** Могут просматривать всю аналитику и списки в системе, но лишены прав на изменение или удаление чужих данных (Пункт 9 ТЗ).
6. **Кэширование данных (Redis):** Аналитические счетчики главной страницы защищены паттерном Cache-Aside и кэшируются в Redis на 10 минут, разгружая основную базу данных.

---

## 🚀 Быстрый запуск проекта локально

### 1. Клонирование репозитория и установка зависимостей
```bash
git clone <ссылка_на_ваш_репозиторий>
cd django-messaging-service
poetry install
```

### 2. Настройка переменных окружения
Создайте в корне проекта файл `.env` на основе примера из `core/.env.example`:
```text
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=[]

DATABASE_NAME=django_messaging_service
DATABASE_USER=messenger_user
DATABASE_PASSWORD=your_postgres_password
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432

EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_HOST_USER=your_email@yandex.ru
EMAIL_HOST_PASSWORD=your_yandex_app_password
EMAIL_USE_SSL=True
DEFAULT_FROM_EMAIL=your_email@yandex.ru
```

### 3. Запуск инфраструктуры (Linux Ubuntu)
Убедитесь, что PostgreSQL и Redis запущены в вашей системе:
```bash
sudo systemctl start postgresql
sudo systemctl start redis-server
```

### 4. Накатка миграций и создание администратора
```bash
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

### 5. Запуск сервера разработки
```bash
poetry run python manage.py runserver
```
После этого проект будет доступен в браузере по адресу: [http://127.0.0](http://127.0.0)

