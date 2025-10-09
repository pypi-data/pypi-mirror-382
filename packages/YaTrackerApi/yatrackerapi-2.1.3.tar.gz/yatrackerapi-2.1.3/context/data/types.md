## Типы данных и основные структуры

### 🔧 Общие принципы типизации
- **Множественные форматы**: большинство полей принимает строки, числа или объекты
- **Автоматическое преобразование**: клиент сам определяет формат и преобразует данные
- **Валидация на клиенте**: проверка типов перед отправкой на сервер
- **Различие CREATE/UPDATE**: разные наборы допустимых операций

### 🏷️ Определенные типы

```python
# Основные типы полей
QueueType = Union[str, int, Dict[str, Union[str, int]]]  # Очередь
ParentType = Union[str, Dict[str, str]]                  # Родительская задача
SprintType = Union[int, str, Dict[str, Union[int, str]]] # Спринт
TypeType = Union[str, int, Dict[str, Union[str, int]]]   # Тип задачи
PriorityType = Union[str, int, Dict[str, Union[str, int]]] # Приоритет
FollowerType = Union[str, int, Dict[str, Union[str, int]]] # Наблюдатель
AssigneeType = Union[str, int, Dict[str, Union[str, int]]] # Исполнитель
AuthorType = Union[str, int, Dict[str, Union[str, int]]]   # Автор
LocalFieldsType = Dict[str, Any]                           # Кастомные поля
SummoneesType = Union[str, int, Dict[str, Union[str, int]]] # Призванные пользователи

# Специальные типы для операций (только PATCH)
AddRemoveType = Dict[str, List[str]]  # {"add": [...], "remove": [...]}
ProjectType = Dict[str, Union[int, List[int], AddRemoveType]]
```

### 🔧 Примеры использования типов

```python
# Очередь (обязательно для создания)
queue = "TREK"                    # Строка-ключ
queue = 123                       # Число-ID
queue = {"key": "TREK"}           # Объект с ключом
queue = {"id": "123"}             # Объект с ID

# Исполнитель/Автор
assignee = "userlogin"            # Логин пользователя
assignee = 123456                 # ID пользователя
assignee = {"login": "userlogin"} # Объект с логином
assignee = {"id": "123456"}       # Объект с ID

# Проекты (для создания)
project = {
    "primary": 1234,              # Основной проект
    "secondary": [5678, 9012]     # Дополнительные проекты
}

# Проекты (для обновления с операциями)
project = {
    "primary": 1234,
    "secondary": {"add": [5678]}  # Добавить дополнительный
}

# Кастомные поля (любые типы данных JSON)
localfields = {
    "customPriority": "Очень высокий",    # Строка
    "businessValue": 85,                  # Число
    "estimatedHours": 16.5,               # Десятичное
    "isDraft": False,                     # Boolean
    "deadline": "2025-12-31",             # Дата
    "tags_custom": ["urgent", "client"],  # Массив
    "metadata": {                         # Объект
        "source": "api",
        "version": "1.0"
    }
}

# Призванные пользователи в комментариях
summonees = [
    "username",                   # По логину
    {"login": "reviewer"},        # Объект с логином
    {"id": "123"},               # Объект с ID
    789012                       # ID как число
]
```

### 📋 Структуры ответов API

#### Задача (Issue)
```python
{
    "id": "task_id",
    "key": "TASK-123",
    "summary": "Название задачи",
    "description": "Описание",
    "status": {"key": "open", "display": "Открыта"},
    "assignee": {"login": "username", "display": "Имя"},
    "priority": {"key": "normal", "display": "Обычный"},
    "queue": {"key": "QUEUE", "display": "Очередь"},
    "createdAt": "2025-01-01T12:00:00.000+0300",
    "updatedAt": "2025-01-01T15:30:00.000+0300",
    "transitions": [...],  # при expand="transitions"
    "attachments": [...]   # при expand="attachments"
}
```

#### Пользователь (User)
```python
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

#### Комментарий (Comment)
```python
{
    "id": "comment_123",
    "text": "Текст комментария",
    "createdBy": {"display": "Имя Автора", "login": "author"},
    "createdAt": "2025-01-01T12:00:00.000+0300",
    "updatedAt": "2025-01-01T12:30:00.000+0300",  # при обновлении
    "updatedBy": {"display": "Имя Редактора"},     # при обновлении
    "attachments": [...],  # при expand="attachments" или "all"
    "html": "<p>HTML версия</p>",  # при expand="html" или "all"
    "summonees": [...]  # призванные пользователи
}
```

#### Сущность (Entity: Project/Portfolio/Goal)
```python
{
    "id": "PROJECT-123",
    "shortId": "PROJECT-123",
    "summary": "Название проекта",
    "description": "Описание проекта",
    "entityStatus": "in_progress",
    "lead": {"login": "manager", "display": "Менеджер"},
    "author": {"login": "creator", "display": "Создатель"},
    "createdAt": "2025-01-01T00:00:00.000+0300",
    "start": "2025-01-01T00:00:00.000+0300",
    "end": "2025-12-31T23:59:59.000+0300",
    "tags": ["strategic", "2025"],
    "teamUsers": [...],
    "clients": [...],
    "followers": [...]
}
```

#### Поле (Field)
```python
{
    "id": "field_12345",
    "key": "summary",
    "name": {"ru": "Название"},
    "description": {"ru": "Описание"},
    "type": "string",
    "schema": {
        "type": "string",
        "required": True,
        "readonly": False,
        "maxLength": 255
    },
    "options": [...]  # для списков
}
```

### 🔗 Типы связей

#### Связи между задачами (Issues)
- `relates` - простая связь
- `is dependent by` - текущая задача блокирует связанную
- `depends on` - текущая задача зависит от связанной
- `is subtask for` - текущая является подзадачей
- `is parent task for` - текущая является родительской
- `duplicates` - текущая дублирует связанную
- `is duplicated by` - связанная дублирует текущую
- `is epic of` - текущая является эпиком (только для эпиков)
- `has epic` - связанная является эпиком (только для эпиков)

#### Связи между сущностями (Entities)

**Для проектов и портфелей:**
- `depends on` - текущая сущность зависит от связанной
- `is dependent by` - текущая сущность блокирует связанную
- `works towards` - связь проекта с целью

**Для целей:**
- `parent entity` - родительская цель
- `child entity` - подцель
- `depends on` - зависимость между целями
- `is dependent by` - блокировка другой цели
- `is supported by` - связь с поддерживающим проектом