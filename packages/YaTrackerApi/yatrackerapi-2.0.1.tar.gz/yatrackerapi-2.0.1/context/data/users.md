## 👥 API для работы с пользователями (Users)

### 📖 Управление пользователями

#### Универсальный метод get()
Метод `get()` поддерживает два режима работы:

**Без параметров** - получение списка всех пользователей:
```python
# Все пользователи организации
users = await client.users.get()

# Структура ответа - список
[
    {
        "id": "user123",
        "login": "username",
        "displayName": "Полное Имя",
        "email": "user@company.com",
        "department": "Отдел разработки",
        "position": "Разработчик",
        "trackerRole": "employee"
    },
    ...
]
```

**С параметром user_id** - получение конкретного пользователя:

**Обязательные параметры:**
- `user_id` - логин (str) или ID (int) пользователя

```python
# По логину
user = await client.users.get("username")

# По ID
user = await client.users.get(123456)

# Структура ответа - словарь
{
    "id": "user123",
    "login": "username",
    "displayName": "Полное Имя",
    "email": "user@company.com",
    "department": "Отдел разработки",
    "position": "Разработчик",
    "trackerRole": "employee"
}
```

### 📊 Структура данных пользователя

#### Основные поля пользователя:
```python
{
    "id": "user_123456",                    # Уникальный ID пользователя
    "login": "username",                    # Логин пользователя
    "displayName": "Иван Иванов",           # Отображаемое имя
    "email": "ivan.ivanov@company.com",     # Email адрес
    "department": "Отдел разработки",       # Подразделение
    "position": "Senior Developer",         # Должность
    "trackerRole": "employee",              # Роль в Tracker
    "firstName": "Иван",                    # Имя
    "lastName": "Иванов",                   # Фамилия
    "timezone": "Europe/Moscow",            # Часовой пояс
    "locale": "ru",                         # Локаль
    "isActive": True,                       # Активность аккаунта
    "createdAt": "2024-01-15T10:30:00.000+0300"  # Дата создания
}
```

#### Доступные роли в Tracker:
- `"admin"` - Администратор
- `"employee"` - Сотрудник
- `"guest"` - Гость
- `"readonly"` - Только чтение

### 🔍 Примеры использования

#### Поиск пользователей по отделу:
```python
# Получение всех пользователей
users = await client.users.get()

# Фильтрация разработчиков
developers = [
    user for user in users
    if "разработ" in user.get("department", {}).get("display", "").lower()
]

print(f"Найдено разработчиков: {len(developers)}")
for dev in developers:
    print(f"- {dev['display']} ({dev['login']})")
```

#### Получение информации о текущем пользователе:
```python
# По логину
current_user = await client.users.get("my_username")

# По ID
current_user = await client.users.get(123456)

print(f"Пользователь: {current_user['display']}")
print(f"Отдел: {current_user.get('department', {}).get('display', 'N/A')}")
print(f"Email: {current_user['email']}")
```

#### Создание списка исполнителей:
```python
# Получение всех пользователей
users = await client.users.get()

# Формирование списка потенциальных исполнителей
assignees = []
for user in users:
    dept_name = user.get("department", {}).get("display", "")
    if (not user.get("dismissed", False) and
        dept_name in ["Отдел разработки", "QA отдел"]):
        assignees.append({
            "login": user["login"],
            "name": user["display"],
            "department": dept_name
        })

# Использование в создании задачи
task = await client.issues.create(
    summary="Новая задача для команды",
    queue="DEVELOPMENT",
    assignee=assignees[0]["login"],  # Назначить первого из списка
    followers=[a["login"] for a in assignees[:3]]  # Первые 3 как наблюдатели
)
```

### 🔧 Интеграция с другими API

#### Использование в задачах:
```python
# Получение пользователя для назначения
user = await client.users.get("developer")

# Создание задачи с назначением
await client.issues.create(
    summary="Задача для разработчика",
    queue="DEVELOPMENT",
    assignee=user["login"],  # Можно использовать login или id
    description=f"Задача назначена пользователю {user['display']}"
)
```

#### Использование в комментариях:
```python
# Получение команды для упоминания
team_users = await client.users.get()
qa_team = [u for u in team_users
           if "QA" in u.get("department", {}).get("display", "")]

# Создание комментария с упоминаниями
await client.issues.comments.create(
    issue_id="TASK-123",
    text=f"@{qa_team[0]['login']} @{qa_team[1]['login']}, требуется тестирование",
    summonees=[u["login"] for u in qa_team[:2]]
)
```