# YaTrackerApi - Особенности и подводные камни

> Документ описывает нестандартные особенности работы с Yandex Tracker API, обнаруженные в процессе разработки

## 📋 Содержание

- [Пагинация при поиске сущностей](#пагинация-при-поиске-сущностей)
- [Параметр fields при поиске](#параметр-fields-при-поиске)
- [Формат поля project при создании задачи](#формат-поля-project-при-создании-задачи)
- [Формат полей type и priority](#формат-полей-type-и-priority)
- [Получение сущностей с полным набором полей](#получение-сущностей-с-полным-набором-полей)
- [Ограничения на изменение системных полей](#ограничения-на-изменение-системных-полей)
- [Дополнительные замечания](#дополнительные-замечания)

---

## Пагинация при поиске сущностей

### Проблема

При использовании `entities.search()` API возвращает пагинированный ответ в виде словаря, а не списка.

### Структура ответа

```python
{
    "hits": 125,      # Общее количество найденных сущностей
    "pages": 3,       # Количество страниц
    "values": [...]   # Массив сущностей на текущей странице (по умолчанию 50)
}
```

### Решение

```python
# Получаем первую страницу
projects_raw = await tracker.client.entities.search(
    entity_type="project",
    fields="summary,id"
)

# Проверяем тип ответа
if isinstance(projects_raw, dict):
    pages = projects_raw.get("pages", 1)

    # Если страниц больше 1 - загружаем все за один запрос
    if isinstance(pages, int) and pages > 1:
        per_page = pages * 50
        projects_raw = await tracker.client.entities.search(
            entity_type="project",
            fields="summary,id",
            per_page=per_page  # Параметр в snake_case
        )

    # Извлекаем данные из values
    if "values" in projects_raw:
        projects = projects_raw["values"]
    else:
        projects = []
else:
    # Если вернулся список (редкий случай)
    projects = projects_raw
```

### Важно

- **Имя параметра**: `per_page` (snake_case), хотя в логах API показывает `perPage` (camelCase) - библиотека автоматически конвертирует
- **Умножение на 50**: Значение `pages * 50` гарантирует получение всех результатов за один запрос
- **Максимум**: API имеет лимиты на `per_page`, обычно до 1000

---

## Параметр fields при поиске

### Проблема

Без явного указания полей в параметре `fields`, API может не возвращать некоторые поля в ответе (например, `summary` для проектов).

### Поведение

#### Без fields:
```python
projects = await tracker.client.entities.search(
    entity_type="project"
)
# summary может отсутствовать в ответе
```

#### С fields:
```python
projects = await tracker.client.entities.search(
    entity_type="project",
    fields="summary,id"
)
# Поля будут в proj["fields"]["summary"]
```

### Структура ответа

Когда используется параметр `fields`, данные находятся в подобъекте `fields`:

```python
{
    "id": "68d3c38893e7da46375740b3",
    "shortId": 341,
    "entityType": "project",
    "fields": {
        "summary": "ЖК Деснаречье д. 4_Навигация -1 и 1 этажи",
        "id": "68d3c38893e7da46375740b3"
    },
    # ... другие поля
}
```

### Решение

```python
# Получаем проекты с нужными полями
projects = await tracker.client.entities.search(
    entity_type="project",
    fields="summary,id,description"
)

# Извлекаем данные из fields
for proj in projects["values"]:
    # Проверяем где находится summary
    summary = proj.get("fields", {}).get("summary", "")

    # Fallback на корень объекта (если fields не использовались)
    if not summary:
        summary = proj.get("summary", "")

    # Если всё ещё пусто - используем shortId
    if not summary:
        summary = f"Проект #{proj.get('shortId', 'N/A')}"
```

---

## Формат поля project при создании задачи

### Проблема

При создании задачи с привязкой к проекту API выдает ошибку:
```
400: {"errors":{"id":"Incorrect data format."}}
```

### Причина

API ожидает **shortId** проекта (число), а не полный строковый **id**.

### Типы ID проекта

```python
project = {
    "id": "68e5764ffa5085239cef5e94",  # Полный ID (строка, 24 символа)
    "shortId": 342                       # Короткий ID (число)
}
```

### Форматы для разных версий API

#### v3 API (текущая)
```python
await client.issues.create(
    summary="Новая задача",
    queue="TESTBOT",
    project={
        "primary": 342,      # shortId как число
        "secondary": [340]   # Опционально: дополнительные проекты
    }
)
```

#### v2 API (устаревшая)
```python
await client.issues.create(
    summary="Новая задача",
    queue="TESTBOT",
    project=342  # Только shortId как число
)
```

### Правильная реализация

```python
# После создания проекта
new_project = await tracker.client.entities.create(
    entity_type="project",
    summary="Новый проект"
)

# Извлекаем shortId (не id!)
project_short_id = new_project.get("shortId")

# Создаем задачу с привязкой к проекту
issue = await tracker.client.issues.create(
    summary="Задача проекта",
    queue="TESTBOT",
    project={"primary": project_short_id}
)
```

### Важно

- ✅ Используйте `shortId` (число)
- ❌ Не используйте `id` (строка)
- ✅ Формат v3: `{"primary": shortId}`
- ❌ Не используйте просто `project_id` как строку

---

## Формат полей type и priority

### Проблема

При создании задачи с полями `type` и `priority` API выдает ошибку 400, если передать полные объекты.

### Неправильно

```python
# Получили задачу
issue = await client.issues.get("TESTBOT-1")

# Пытаемся создать копию с теми же полями
new_issue = await client.issues.create(
    summary="Копия задачи",
    queue="TESTBOT",
    type=issue["type"],        # ❌ Полный объект
    priority=issue["priority"]  # ❌ Полный объект
)

# Структура полного объекта:
{
    "type": {
        "self": "https://api.tracker.yandex.net/v3/issuetypes/21",
        "id": "21",
        "key": "milestone",
        "display": "Веха"
    }
}
```

### Правильно

API ожидает только ключ (`key`) или ID (`id`):

```python
# Извлекаем только ключ или ID
issue_type = issue["type"]
if isinstance(issue_type, dict):
    type_value = issue_type.get("key") or issue_type.get("id")
else:
    type_value = issue_type

issue_priority = issue["priority"]
if isinstance(issue_priority, dict):
    priority_value = issue_priority.get("key") or issue_priority.get("id")
else:
    priority_value = issue_priority

# Создаем задачу с правильными значениями
new_issue = await client.issues.create(
    summary="Копия задачи",
    queue="TESTBOT",
    type=type_value,        # ✅ Строка: "milestone" или "21"
    priority=priority_value  # ✅ Строка: "normal" или "3"
)
```

### Универсальная функция

```python
def extract_field_value(field_data):
    """
    Извлечь значение поля для API запроса.

    Args:
        field_data: Поле из ответа API (может быть строкой, числом или объектом)

    Returns:
        Значение для передачи в API (строка или число)
    """
    if isinstance(field_data, dict):
        # Приоритет: key > id
        return field_data.get("key") or field_data.get("id")
    return field_data

# Использование
new_issue = await client.issues.create(
    summary="Копия задачи",
    queue="TESTBOT",
    type=extract_field_value(issue.get("type")),
    priority=extract_field_value(issue.get("priority"))
)
```

### Важно

- ✅ Передавайте только `key` или `id`
- ❌ Не передавайте полные объекты с `self`, `display`
- ✅ Предпочитайте `key` (читаемее): `"milestone"`, `"normal"`
- ⚠️ Fallback на `id` если `key` отсутствует

---

## Получение сущностей с полным набором полей

### Проблема

При использовании `entities.get()` без параметра `fields`, API возвращает только базовые поля. Такие важные поля как `description`, `lead`, `teamUsers`, `parentEntity` **не включаются** в ответ по умолчанию.

### Поведение

#### Без fields:
```python
project = await client.entities.get(
    entity_id=project_id,
    entity_type="project"
)
# В ответе НЕТ: description, lead, teamUsers, parentEntity
```

#### С fields:
```python
project = await client.entities.get(
    entity_id=project_id,
    entity_type="project",
    fields="summary,description,lead,teamUsers,teamAccess,parentEntity"
)
# Все поля присутствуют в ответе
```

### Решение

Всегда явно указывайте нужные поля через параметр `fields`:

```python
# Получение проекта со всеми необходимыми полями
project = await client.entities.get(
    entity_id=project_id,
    entity_type="project",
    fields="summary,description,lead,teamUsers,teamAccess,parentEntity,clients,followers,start,end,tags"
)
```

### Доступные поля для проектов

**Основные поля:**
- `summary` - название проекта
- `description` - описание
- `lead` - руководитель/ответственный
- `teamUsers` - участники команды
- `teamAccess` - настройки доступа
- `parentEntity` - родительский портфель

**Дополнительные поля:**
- `clients` - клиенты
- `followers` - наблюдатели
- `start` - дата начала
- `end` - дата окончания
- `tags` - теги
- `entityStatus` - статус проекта

### Важно

⚠️ Если не указать `fields`, большинство полей **не вернется** в ответе, даже если они заполнены в проекте.

---

## Ограничения на изменение системных полей

### Поля, которые НЕЛЬЗЯ изменить

API Yandex Tracker **не позволяет** изменять следующие системные поля:

#### Для проектов (entities):
- ❌ `createdBy` - автор проекта
- ❌ `createdAt` - дата создания
- ❌ `author` - автор (алиас createdBy)

#### Для задач (issues):
- ❌ `createdBy` - автор задачи
- ❌ `createdAt` - дата создания
- ❌ `author` - автор (алиас createdBy)

### Причина

Эти поля используются для **аудита и истории** изменений. API автоматически устанавливает их на основе OAuth токена пользователя, выполнившего запрос.

### Что можно изменить вместо автора

#### Для проектов:
```python
await client.entities.update(
    entity_id=project_id,
    lead="user_login",              # ✅ Руководитель
    teamUsers=["user1", "user2"],   # ✅ Участники
    followers=["user3"]             # ✅ Наблюдатели
)
```

#### Для задач:
```python
await client.issues.update(
    issue_id="TESTBOT-1",
    assignee="user_login",          # ✅ Исполнитель
    followers={"add": ["user1"]}    # ✅ Наблюдатели
)
```

### Практическое применение при клонировании

При клонировании проектов/задач:

**✅ Копируются:**
- Руководитель проекта (`lead`)
- Участники (`teamUsers`)
- Исполнитель задачи (`assignee`)
- Наблюдатели (`followers`)
- Описание, теги, приоритет, тип

**❌ НЕ копируются (устанавливаются автоматически):**
- Автор (`createdBy`) - всегда текущий пользователь
- Дата создания (`createdAt`) - текущее время

### Важно

🔐 Невозможность изменения `createdBy` - это **защита целостности** аудита. Все создания и изменения должны быть прослеживаемы до реального пользователя.

---

## Дополнительные замечания

### Параметры запросов

Библиотека YaTrackerApi автоматически конвертирует snake_case параметры в camelCase для API:
- `per_page` → `perPage`
- `issue_id` → `issueId`

Поэтому в Python коде всегда используйте **snake_case**.

### Обработка ошибок

API возвращает детальные ошибки в формате:
```json
{
    "errors": {"field_name": "error description"},
    "errorsData": {},
    "errorMessages": [],
    "statusCode": 400
}
```

Используйте debug логирование для диагностики:
```python
logging.getLogger("YaTrackerApi").setLevel(logging.DEBUG)
```

---

**Дата создания**: 2025-10-07
**Версия YaTrackerApi**: 2.1.0
**Автор**: Даниил Павлючик
