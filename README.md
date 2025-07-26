# Реферальная система

Простая реферальная система с авторизацией по номеру телефона, построенная на Django и Django REST Framework.

## Функциональность

- Авторизация по номеру телефона с 4-значным кодом
- Автоматическое создание нового пользователя при первой авторизации
- Генерация уникального 6-значного инвайт-кода для каждого пользователя
- Активация чужого инвайт-кода (только один раз)
- Просмотр списка рефералов в профиле
- REST API для всего функционала
- Веб-интерфейс для тестирования
- Документация API (ReDoc/Swagger)
- Панель администратора Django

## Установка и запуск

### Локальная установка

1. Клонируйте репозиторий и перейдите в папку проекта
2. Создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # На Windows: .venv\Scripts\activate
   ```

3. Установите зависимости:
   ```bash
   pip install django djangorestframework psycopg2-binary python-decouple drf-spectacular django-cors-headers
   ```

4. Создайте файл `.env`:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   USE_SQLITE=True
   ```

5. Примените миграции:
   ```bash
   python manage.py migrate
   ```

6. Создайте суперпользователя:
   ```bash
   python manage.py createsuperuser
   ```

7. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Авторизация

#### 1. Отправка кода авторизации
- **URL**: `POST /api/auth/send-code/`
- **Body**:
  ```json
  {
    "phone_number": "+71234567890"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Код отправлен на номер +71234567890",
    "code": "1234"
  }
  ```

#### 2. Проверка кода авторизации
- **URL**: `POST /api/auth/verify-code/`
- **Body**:
  ```json
  {
    "phone_number": "+71234567890",
    "code": "1234"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Пользователь найден",
    "user_id": 1,
    "is_new_user": false
  }
  ```

### Профиль пользователя

#### 3. Получение профиля
- **URL**: `GET /api/auth/profile/`
- **Headers**: `X-User-ID: 1`
- **Response**:
  ```json
  {
    "phone_number": "+71234567890",
    "invite_code": "ABC123",
    "activated_invite_code": "XYZ789",
    "referrals": ["+79876543210", "+78887776655"]
  }
  ```

#### 4. Активация инвайт-кода
- **URL**: `POST /api/auth/activate-invite/`
- **Headers**: `X-User-ID: 1`
- **Body**:
  ```json
  {
    "invite_code": "XYZ789"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Инвайт-код XYZ789 успешно активирован"
  }
  ```

## Веб-интерфейс

Откройте браузер и перейдите по адресу `http://localhost:8000/` для тестирования через веб-интерфейс.

## Документация API

- **ReDoc**: `http://localhost:8000/api/docs/`
- **Swagger UI**: `http://localhost:8000/api/swagger/`
- **Схема API**: `http://localhost:8000/api/schema/`

## Панель администратора

Доступ к панели администратора: `http://localhost:8000/admin/`

## Модели данных

### User
- `phone_number` - номер телефона (уникальный)
- `invite_code` - 6-значный инвайт-код пользователя
- `activated_invite_code` - активированный инвайт-код
- `is_active`, `is_staff` - флаги активности и доступа к админке
- `date_joined` - дата регистрации

### AuthCode
- `phone_number` - номер телефона
- `code` - 4-значный код авторизации
- `created_at` - время создания
- `is_used` - флаг использования

### Referral
- `referrer` - пользователь, который пригласил
- `referred` - приглашенный пользователь
- `created_at` - дата создания связи

## Особенности реализации

1. **Аутентификация**: Для упрощения тестирования используется заголовок `X-User-ID` вместо токенов
2. **Коды авторизации**: Возвращаются в ответе для удобства тестирования
3. **База данных**: По умолчанию используется SQLite для простоты развертывания
4. **Инвайт-коды**: Генерируются автоматически при создании пользователя

## Развертывание

Проект готов для развертывания на платформах типа PythonAnywhere, Heroku или Railway. Для PostgreSQL создайте соответствующие переменные окружения и установите `USE_SQLITE=False`.

## Технологии

- Python 3.8+
- Django 5.2
- Django REST Framework
- PostgreSQL/SQLite
- Bootstrap 5 (для веб-интерфейса)
- drf-spectacular (для документации API)
