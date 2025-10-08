## 👥 API для работы с пользователями (Users)

### 📖 Управление пользователями

#### Получение списка пользователей (get())
**Опциональные параметры:**
- `fields` - дополнительные поля (строка через запятую)

```python
# Все пользователи организации
users = await client.users.get()

# С дополнительными полями
users = await client.users.get(fields="login,email,displayName,department")

# Структура ответа
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

#### Получение конкретного пользователя (get_user())
**Обязательные параметры:**
- `user_login_or_id` - логин или ID пользователя

**Опциональные параметры:**
- `fields` - дополнительные поля

```python
# По логину
user = await client.users.get_user("username")

# По ID
user = await client.users.get_user("123456")

# С дополнительными полями
user = await client.users.get_user(
    user_login_or_id="username",
    fields="login,email,displayName,department,position"
)
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
# Получение всех пользователей с информацией об отделах
users = await client.users.get(fields="login,displayName,department")

# Фильтрация разработчиков
developers = [
    user for user in users
    if "разработ" in user.get("department", "").lower()
]

print(f"Найдено разработчиков: {len(developers)}")
for dev in developers:
    print(f"- {dev['displayName']} ({dev['login']})")
```

#### Получение информации о текущем пользователе:
```python
# Если известен логин
current_user = await client.users.get_user("my_username")

# С полной информацией
detailed_user = await client.users.get_user(
    user_login_or_id="my_username",
    fields="login,displayName,email,department,position,timezone"
)

print(f"Пользователь: {detailed_user['displayName']}")
print(f"Отдел: {detailed_user['department']}")
print(f"Email: {detailed_user['email']}")
```

#### Создание списка исполнителей:
```python
# Получение активных пользователей отдела
users = await client.users.get(fields="login,displayName,department,isActive")

# Формирование списка потенциальных исполнителей
assignees = []
for user in users:
    if (user.get("isActive", True) and
        user.get("department") in ["Отдел разработки", "QA отдел"]):
        assignees.append({
            "login": user["login"],
            "name": user["displayName"],
            "department": user["department"]
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
user = await client.users.get_user("developer")

# Создание задачи с назначением
await client.issues.create(
    summary="Задача для разработчика",
    queue="DEVELOPMENT",
    assignee=user["login"],  # Можно использовать login или id
    description=f"Задача назначена пользователю {user['displayName']}"
)
```

#### Использование в комментариях:
```python
# Получение команды для упоминания
team_users = await client.users.get(fields="login,displayName,department")
qa_team = [u for u in team_users if "QA" in u.get("department", "")]

# Создание комментария с упоминаниями
await client.issues.comments.create(
    issue_id="TASK-123",
    text=f"@{qa_team[0]['login']} @{qa_team[1]['login']}, требуется тестирование",
    summonees=[u["login"] for u in qa_team[:2]]
)
```