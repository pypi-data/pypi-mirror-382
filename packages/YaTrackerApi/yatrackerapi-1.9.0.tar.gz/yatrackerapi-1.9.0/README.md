# Yandex Tracker API Client

Асинхронный Python клиент для работы с Yandex Tracker API с **модульной архитектурой**.

## 🚀 Особенности

- **Асинхронная работа** с aiohttp
- **Модульная архитектура** с lazy loading для разных API модулей
- **Context manager** для автоматического управления HTTP сессиями
- **Полная поддержка CRUD операций** для задач (GET, POST, PATCH, MOVE)
- **Умная типизация** с валидацией данных на клиенте
- **Операции add/remove** для массивов (followers, tags, project.secondary)
- **Кастомные поля пользователя** (localfields) 🆕 - любые JSON данные
- **Перенос задач между очередями** с полным контролем настроек
- **Предотвращение дубликатов** через unique поле
- **Управление чек-листами** - создание, обновление, удаление элементов 🆕
- **Health Check** для проверки работоспособности API
- **Структурированные примеры** использования всех методов
- **Подробное логгирование** на русском языке с JSON форматированием
- **Обработка ошибок** с детализированной информацией

## 📦 Установка

```bash
# Клонирование проекта
git clone <repository-url>
cd ya_tracker_test

# Установка зависимостей через uv
uv sync

# Или через pip
pip install -r requirements.txt
```

## ⚙️ Настройка

Создайте файл `.env` в корне проекта:

```env
TRACKER_API_KEY=ваш_oauth_токен
TRACKER_ORG_ID=ваш_organization_id
```

### Получение токенов:

1. **OAuth токен**: https://oauth.yandex.ru/
2. **Organization ID**: консоль Yandex Cloud

## 🎯 Использование

### Базовое использование

```python
import asyncio
from client import YandexTrackerClient
from env import TRACKER_API_KEY, TRACKER_ORG_ID

async def main():
    async with YandexTrackerClient(
        oauth_token=TRACKER_API_KEY,
        org_id=TRACKER_ORG_ID,
        log_level="INFO"
    ) as client:
        # Проверка работоспособности
        user_info = await client.health_check()
        print(f"API работает! Пользователь: {user_info['display']}")
        
        # Создание новой задачи с кастомными полями
        new_issue = await client.issues.create(
            summary="Тестовая задача",
            queue="PROJ",
            localfields={
                "customPriority": "Очень высокий",
                "businessValue": 85,
                "estimatedHours": 16.5
            }
        )
        print(f"Создана задача: {new_issue['key']}")
        
        # Получение задачи
        issue = await client.issues.get(new_issue['key'])
        print(f"Задача: {issue['summary']}")
        
        # Обновление задачи с кастомными полями
        await client.issues.update(
            new_issue['key'], 
            description="Обновленное описание",
            localfields={
                "progress": "50%",
                "reviewRequired": True
            }
        )
        print("Задача обновлена!")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📋 API Модули

### Fields (Поля) - ✅ Полностью реализован

#### Получение всех полей (GET)
```python
# Получение списка всех доступных полей
fields = await client.fields.get()

# Анализ системных полей
system_fields = [f for f in fields if f.get('schema') and not f.get('schema', {}).get('required')]

# Поиск обязательных полей для создания задач
required_fields = [f for f in fields if f.get('schema', {}).get('required')]

# Группировка полей по типам
field_types = {}
for field in fields:
    field_type = field.get('type', 'unknown')
    if field_type not in field_types:
        field_types[field_type] = []
    field_types[field_type].append(field.get('key'))
```

#### Создание кастомных полей (POST) - 🆕 Полная поддержка!
```python
# Простое текстовое поле
field = await client.fields.create(
    name={"en": "Custom Priority", "ru": "Кастомный приоритет"},
    id="custom_priority_field",
    category="category_id_here",  # Получить из GET /v3/fields/categories
    type="ru.yandex.startrek.core.fields.StringFieldType",
    description="Пользовательское поле для приоритета",
    visible=True,
    readonly=False
)

# Выпадающий список
list_field = await client.fields.create(
    name={"en": "Project Stage", "ru": "Стадия проекта"},
    id="project_stage_field",
    category="category_id_here",
    type="ru.yandex.startrek.core.fields.StringFieldType",
    options_provider={
        "type": "FixedListOptionsProvider",
        "values": ["Planning", "Development", "Testing", "Release"]
    },
    container=False
)

# Поле для множественного выбора пользователей
team_field = await client.fields.create(
    name={"en": "Project Team", "ru": "Команда проекта"},
    id="project_team_field",
    category="category_id_here",
    type="ru.yandex.startrek.core.fields.UserFieldType",
    container=True,  # Множественный выбор
    visible=True
)

# Числовое поле
budget_field = await client.fields.create(
    name={"en": "Project Budget", "ru": "Бюджет проекта"},
    id="project_budget_amount",
    category="category_id_here",
    type="ru.yandex.startrek.core.fields.FloatFieldType",
    description="Выделенный бюджет на проект в рублях",
    visible=True
)

# Поле даты
deadline_field = await client.fields.create(
    name={"en": "Client Deadline", "ru": "Дедлайн клиента"},
    id="client_deadline_date",
    category="category_id_here",
    type="ru.yandex.startrek.core.fields.DateFieldType",
    description="Дата, к которой клиент ожидает завершения работ"
)
```

#### Поддерживаемые типы полей:
- `ru.yandex.startrek.core.fields.DateFieldType` — Дата
- `ru.yandex.startrek.core.fields.DateTimeFieldType` — Дата/Время
- `ru.yandex.startrek.core.fields.StringFieldType` — Текстовое однострочное
- `ru.yandex.startrek.core.fields.TextFieldType` — Текстовое многострочное
- `ru.yandex.startrek.core.fields.FloatFieldType` — Дробное число
- `ru.yandex.startrek.core.fields.IntegerFieldType` — Целое число
- `ru.yandex.startrek.core.fields.UserFieldType` — Пользователь
- `ru.yandex.startrek.core.fields.UriFieldType` — Ссылка

#### Типы провайдеров опций:
- `FixedListOptionsProvider` — Список строковых или числовых значений
- `FixedUserListOptionsProvider` — Список пользователей (для UserFieldType)

#### Настройки отображения:
- `visible` — Отображение поля в интерфейсе
- `hidden` — Скрытие поля даже если оно заполнено
- `readonly` — Только чтение (нельзя изменить)
- `container` — Множественный выбор (как теги)
- `order` — Порядковый номер в списке полей

#### Интеграция с задачами:
После создания поля можно использовать в localfields:
```python
# Использование созданных полей в задачах
await client.issues.create(
    summary='Новый проект',
    queue='PROJ',
    localfields={
        'custom_priority_field': 'Высокий',
        'project_stage_field': 'Development',
        'project_budget_amount': 500000.0,
        'client_deadline_date': '2025-12-31'
    }
)
```

### Issues (Задачи) - ✅ Полностью реализован

#### Получение задач (GET)
```python
# Получение базовой информации о задаче
issue = await client.issues.get('TASK-123')

# Получение задачи с вложениями
issue = await client.issues.get('TASK-123', expand='attachments')

# Получение задачи с переходами и вложениями
issue = await client.issues.get('TASK-123', expand=['transitions', 'attachments'])
```

#### Создание задач (POST) - 🆕 С кастомными полями!
```python
# Минимальное создание
new_issue = await client.issues.create(
    summary="Test Issue",
    queue="TREK"
)

# Создание с кастомными полями
new_issue = await client.issues.create(
    summary="Задача с кастомными полями",
    queue="PROJ",
    description="Описание задачи",
    localfields={
        "customPriority": "Очень высокий",
        "businessValue": 85,
        "estimatedHours": 16.5,
        "clientName": "ООО Рога и Копыта",
        "isDraft": False
    }
)

# Создание с полным набором полей + кастомные поля
new_issue = await client.issues.create(
    summary="Test Issue",
    queue="TREK",
    parent="JUNE-2",
    issue_type="bug",
    assignee="userlogin",
    attachment_ids=[55, 56],
    tags=["тег1", "тег2"],
    localfields={
        "department": "Backend Team",
        "complexity": 7,
        "deadline": "2025-12-31",
        "customerImpact": "Высокий"
    }
)

# Бизнес-задача с метриками и предотвращением дубликатов
new_issue = await client.issues.create(
    summary="Оптимизация производительности",
    queue={"key": "PERF"},
    description="Улучшение скорости загрузки",
    issue_type={"key": "improvement"},
    priority={"key": "major"},
    assignee="performance-team",
    unique="perf-task-2025-001",  # Предотвращение дубликатов
    localfields={
        "currentLoadTime": "3.2s",
        "targetLoadTime": "1.5s",
        "affectedUsers": 15000,
        "businessImpact": "Высокий",
        "technicalDebt": True,
        "estimatedROI": 25.5
    }
)
```

#### Обновление задач (PATCH) - 🆕 С кастомными полями!
```python
# Базовое обновление с кастомными полями
await client.issues.update(
    'TEST-1',
    summary="Обновленное название",
    description="Новое описание",
    localfields={
        "customPriority": "Критический",
        "estimatedHours": 24,
        "clientFeedback": "Требует срочного исправления"
    }
)

# Обновление с операциями add/remove + кастомные поля
await client.issues.update(
    'TEST-1',
    followers={"add": ["reviewer1", "reviewer2"]},
    tags={"add": ["срочно"], "remove": ["можно-отложить"]},
    localfields={
        "department": "Frontend Team",
        "complexity": 9,
        "reviewRequired": True,
        "lastUpdatedBy": "project-manager"
    }
)

# Обновление метрик и статистики
await client.issues.update(
    'PERF-123',
    localfields={
        "currentLoadTime": "2.1s",        # Улучшили с 3.2s
        "testsCompleted": 45,             # Прогресс тестирования
        "performanceGain": "34%",         # Достигнутое улучшение
        "deploymentReady": False,         # Готовность к деплою
        "lastBenchmark": "2025-09-24"     # Дата последнего теста
    }
)
```

#### Поддерживаемые поля

**Для создания (POST) - обязательные:**
- `summary` ⭐ - название задачи
- `queue` ⭐ - очередь для создания

**Для создания (POST) - опциональные:**
- `description` - описание задачи
- `parent` - родительская задача
- `markup_type` - тип разметки ('md' для YFM)
- `sprint` - список спринтов
- `issue_type` - тип задачи (bug, task, etc.)
- `priority` - приоритет (critical, major, minor, etc.)
- `assignee` - исполнитель задачи
- `author` - автор задачи
- `followers` - наблюдатели задачи
- `project` - проекты (primary/secondary)
- `unique` - уникальное поле для предотвращения дубликатов
- `attachment_ids` - ID временных файлов для вложений
- `description_attachment_ids` - ID файлов для описания
- `tags` - теги задачи
- `localfields` 🆕 - **кастомные поля пользователя**

**Для обновления (PATCH):**
- Все поля из создания (кроме обязательных)
- `followers` - с операциями add/remove
- `tags` - с операциями add/remove
- `project.secondary` - с операциями add/remove
- `localfields` 🆕 - **кастомные поля пользователя**

#### 🚚 Перенос задач (MOVE) - 🆕 Между очередями!
```python
# Простой перенос в другую очередь
await client.issues.move('TEST-1', 'ARCHIVE')

# Перенос с отключением уведомлений
await client.issues.move('TEST-1', 'ARCHIVE', notify=False)

# Полный перенос с сохранением всех данных
await client.issues.move(
    'PROJ-5', 'NEWQUEUE',
    move_all_fields=True,      # Перенести версии/компоненты/проекты
    initial_status=True,       # Сбросить в начальный статус новой очереди
    notify_author=False,       # Не уведомлять автора
    expand=['transitions', 'attachments']  # Получить дополнительные данные
)
```

#### 🔢 Подсчет задач (COUNT) - 🆕 С фильтрацией!
```python
# Подсчет задач без исполнителя в очереди
count = await client.issues.count(filter={
    "queue": "JUNE",
    "assignee": "empty()"
})

# Подсчет задач по нескольким критериям
count = await client.issues.count(filter={
    "queue": "PROJ",
    "status": "open",
    "priority": "major"
})

# Использование языка запросов Yandex Tracker
count = await client.issues.count(
    query="Queue: JUNE AND Status: Open AND Priority: Major"
)

# Подсчет задач с кастомными полями
count = await client.issues.count(filter={
    "queue": "TECH",
    "customPriority": "Высокий"
})

# Подсчет задач за период времени
count = await client.issues.count(
    query='Queue: PROJ AND Created: >= "2025-01-01"'
)
```

#### 🔍 Поиск задач (SEARCH) - 🆕 С расширенными возможностями!
```python
# Поиск всех задач в очереди
tasks = await client.issues.search(queue="TREK")

# Поиск конкретных задач по ключам
tasks = await client.issues.search(keys=["TASK-123", "TASK-124"])

# Поиск с фильтрацией и сортировкой
tasks = await client.issues.search(
    filter={"queue": "TREK", "assignee": "empty()"},
    order="+status",
    expand=["transitions", "attachments"],
    per_page=100
)

# Поиск с помощью языка запросов Yandex Tracker
tasks = await client.issues.search(
    query='Queue: TREK AND Status: Open "Sort by": Updated DESC',
    expand="attachments"
)

# Поиск задач с кастомными полями
tasks = await client.issues.search(filter={
    "queue": "TECH",
    "customPriority": "Высокий"
})

# Сложный поиск с множественными критериями
tasks = await client.issues.search(
    query='Queue: TREK AND (Priority: Major OR Priority: Critical) AND Status: != Closed "Sort by": Priority DESC',
    expand=["transitions", "attachments"],
    per_page=50
)
```

#### Параметры поиска:
- **queue** - поиск по очереди (наивысший приоритет)
- **keys** - поиск конкретных задач по ключам
- **filter** - фильтрация по полям задач
- **query** - язык запросов Yandex Tracker
- **order** - сортировка (только с filter): `"+поле"` или `"-поле"`
- **expand** - дополнительные поля (`transitions`, `attachments`)
- **per_page** - размер страницы (по умолчанию 50)

**Приоритеты параметров**: queue > keys > filter > query
**Ограничение**: максимум 2 основных параметра одновременно

#### 🧹 Очистка скролл-сессий (CLEAR_SCROLL) - 🆕 Управление ресурсами!
```python
# Очистка скролл-сессий после завершения поиска
# (scroll_id и scroll_token получаются из заголовков ответа на search)
scroll_sessions = {
    "cXVlcnlUaGVuRmV0Y2g7NjsyNDU5MzpmQ0gwd...": "c44356850f446b88e5b5cd65a34a1409...",
    "cXVlcnlUaGVuRmV0Y2g7NjsyMDQ0MzpTdGp6Wm...": "b8e1c56966f037d9c4e241af40d31dc8..."
}

# Освобождение серверных ресурсов
result = await client.issues.clear_scroll(scroll_sessions)

# Типичный сценарий использования:
# 1. Выполнить поиск задач (search)
# 2. Получить scroll_id/scroll_token из заголовков ответа
# 3. Обработать результаты поиска
# 4. Очистить скролл-сессии для освобождения ресурсов
```

#### 📋 Получение приоритетов (PRIORITIES) - 🆕 Справочная информация!
```python
# Получение приоритетов на языке пользователя (по умолчанию)
priorities = await client.issues.priorities()

# Получение приоритетов на всех языках
all_priorities = await client.issues.priorities(localized=False)

# Использование результатов
for priority in priorities:
    print(f"Приоритет: {priority['display']} (ключ: {priority['key']})")

# Поиск конкретного приоритета
major_priority = next(
    (p for p in priorities if p['key'] == 'major'),
    None
)

# Создание словаря для быстрого доступа
priority_map = {p['key']: p for p in priorities}

# Валидация приоритета перед использованием
if 'critical' in priority_map:
    # Можно безопасно использовать в создании задач
    await client.issues.create(
        summary="Критическая задача",
        queue="PROJ",
        priority="critical"
    )
```

#### 📚 История изменений (CHANGELOG) - 🆕 Аудит активности!
```python
# Получение всех изменений задачи
changelog = await client.issues.changelog('TASK-123')

# Анализ изменений
for change in changelog:
    author = change.get('updatedBy', {}).get('display', 'System')
    updated_at = change.get('updatedAt', 'Unknown')
    print(f"Изменение от {author} в {updated_at}")

    # Просмотр конкретных изменений полей
    for field_change in change.get('fields', []):
        field_name = field_change.get('field', {}).get('display', 'Unknown')
        from_value = field_change.get('from', {}).get('display', 'None')
        to_value = field_change.get('to', {}).get('display', 'None')
        print(f"  {field_name}: {from_value} -> {to_value}")

# Получение изменений с пагинацией
changelog_page = await client.issues.changelog('TASK-123', per_page=20)

# Фильтрация по полю статуса
status_changes = await client.issues.changelog('TASK-123', field='status')

# Фильтрация по типу изменения
updates_only = await client.issues.changelog('TASK-123', type='IssueUpdated')

# Получение изменений чеклиста
checklist_changes = await client.issues.changelog('TASK-123', field='checklists')

# Комбинированная фильтрация
assignee_updates = await client.issues.changelog(
    'TASK-123',
    field='assignee',
    type='IssueUpdated',
    per_page=10
)

# Анализ активности задачи
total_changes = len(changelog)
authors = set(change.get('updatedBy', {}).get('login') for change in changelog)
print(f"Всего изменений: {total_changes}, участников: {len(authors)}")

# Группировка изменений по дням
from collections import defaultdict
changes_by_date = defaultdict(list)
for change in changelog:
    date = change.get('updatedAt', '')[:10]  # YYYY-MM-DD
    changes_by_date[date].append(change)
```

#### 🔍 Анализ переходов (GET) - Получение доступных переходов
```python
# Получение доступных переходов для задачи
transitions = await client.issues.transitions.get('TASK-123')

# Обработка результатов
for transition in transitions:
    print(f"Переход: {transition['display']} -> {transition['to']['display']}")

# Поиск конкретного перехода
close_transition = next(
    (t for t in transitions if 'close' in t.get('display', '').lower()),
    None
)

# Проверка доступности перехода
can_resolve = any(
    'resolve' in t.get('display', '').lower()
    for t in transitions
)

# Анализ воркфлоу
if transitions:
    print(f"Доступно {len(transitions)} переходов")

    # Категоризация переходов
    close_transitions = [
        t for t in transitions
        if 'close' in t.get('display', '').lower()
    ]

    # Получение целевых статусов
    target_statuses = [t['to']['display'] for t in transitions]

    # Проверка обязательных полей
    screen_required = [t for t in transitions if t.get('screen')]
```

#### 🔄 Переходы по жизненному циклу (TRANSITIONS) - 🆕 Управление воркфлоу!
```python
# Получение доступных переходов для задачи
transitions = await client.issues.transitions.get('TASK-123')

# Анализ переходов
for transition in transitions:
    trans_id = transition['id']
    display_name = transition['display']
    to_status = transition['to']['display']
    print(f"Переход '{display_name}' -> {to_status} (ID: {trans_id})")

# Поиск конкретного перехода
close_transition = next(
    (t for t in transitions if 'close' in t['display'].lower()),
    None
)

# Простой переход без дополнительных параметров
result = await client.issues.transitions.update('TASK-123', 'transition_id')

# Переход с комментарием
result = await client.issues.transitions.update(
    'TASK-123',
    'close_transition_id',
    comment="Задача выполнена успешно"
)

# Переход с обновлением полей
result = await client.issues.transitions.update(
    'TASK-123',
    'resolve_transition_id',
    comment="Исправлено в версии 1.2.3",
    assignee="tester",
    resolution="fixed"
)

# Переход с кастомными полями
result = await client.issues.transitions.update(
    'TASK-123',
    'transition_id',
    comment="Переход с метриками",
    resolution="completed",
    localfields={
        "completionTime": "2.5h",
        "quality": "excellent",
        "performanceScore": 95
    }
)

# Получение ID перехода из списка доступных
transitions = await client.issues.transitions.get('TASK-123')
close_transition = next(
    (t for t in transitions if 'close' in t['display'].lower()),
    None
)
if close_transition:
    result = await client.issues.transitions.update(
        'TASK-123',
        close_transition['id'],
        comment="Автоматическое закрытие"
    )

# Новый статус после перехода
new_status = result['status']['display']
```

#### 🔗 Связи между задачами (LINKS) - 🆕 Управление отношениями!
```python
# Получение всех связей задачи
links = await client.issues.links.get('TASK-123')

# Анализ связей
for link in links:
    object_key = link['object']['key']
    subject_key = link['subject']['key']
    relationship = link['relationship']['display']
    print(f"Связь: {object_key} [{relationship}] {subject_key}")

# Фильтрация связей по типу
dependencies = [
    link for link in links
    if link['relationship']['key'] == 'depends on'
]

subtasks = [
    link for link in links
    if link['relationship']['key'] == 'is parent task for'
]

blocked_tasks = [
    link['subject']['key'] for link in links
    if link['relationship']['key'] == 'is dependent by'
]

# Создание различных типов связей
# Простая связь между задачами
link = await client.issues.links.create(
    'TASK-123',
    'relates',
    'TASK-456'
)

# Создание зависимости (TASK-123 зависит от TASK-456)
link = await client.issues.links.create(
    'TASK-123',
    'depends on',
    'TASK-456'
)

# Создание подзадачи (TASK-123 является подзадачей TASK-456)
link = await client.issues.links.create(
    'TASK-123',
    'is subtask for',
    'TASK-456'
)

# Создание родительской задачи (TASK-123 является родительской для TASK-456)
link = await client.issues.links.create(
    'TASK-123',
    'is parent task for',
    'TASK-456'
)

# Создание связи дублирования
link = await client.issues.links.create(
    'TASK-123',
    'duplicates',
    'TASK-456'
)

# Создание эпика (только для задач типа "Эпик")
epic_link = await client.issues.links.create(
    'EPIC-1',
    'is epic of',
    'TASK-123'
)

# Создание блокирующей связи
blocker_link = await client.issues.links.create(
    'BLOCKER-1',
    'is dependent by',
    'TASK-123'
)

# Удаление связей
if links:
    # Удаление конкретной связи
    result = await client.issues.links.delete('TASK-123', links[0]['id'])
    print(f"Удалена связь: {result['object']['key']} -> {result['subject']['key']}")

    # Пакетное удаление связей определенного типа
    dependency_links = [
        link for link in links
        if link['relationship']['key'] == 'depends on'
    ]

    for link in dependency_links:
        await client.issues.links.delete('TASK-123', link['id'])
        print(f"Удалена зависимость: {link['subject']['key']}")

# Результат содержит информацию о связи
print(f"Создана связь: {link['object']['key']} -> {link['subject']['key']}")
print(f"Тип связи: {link['relationship']['display']}")
```

##### Поддерживаемые типы связей:
- `relates` - простая связь между задачами
- `is dependent by` - текущая задача является блокером для связываемой
- `depends on` - текущая задача зависит от связываемой
- `is subtask for` - текущая задача является подзадачей связываемой
- `is parent task for` - текущая задача является родительской для связываемой
- `duplicates` - текущая задача дублирует связываемую
- `is duplicated by` - связываемая задача дублирует текущую
- `is epic of` - текущая задача является эпиком связываемой (только для эпиков)
- `has epic` - связываемая задача является эпиком текущей (только для эпиков)

##### Методы API для связей:
- `client.issues.links.get(issue_id)` - получение всех связей задачи (GET)
- `client.issues.links.create(issue_id, relationship, linked_issue)` - создание связи (POST)
- `client.issues.links.delete(issue_id, link_id)` - удаление связи (DELETE)
```

## 📋 Чек-листы - `client.issues.checklists` ✅ ПОЛНОСТЬЮ ЗАВЕРШЕН

### 1. Получение чек-листа

```python
# Получить все элементы чек-листа задачи
checklist_items = await client.issues.checklists.get('TASK-123')

# Анализ элементов
for item in checklist_items:
    print(f"Элемент: {item['text']}")
    print(f"Статус: {'✓' if item['checked'] else '○'}")
    print(f"ID: {item['id']}")

    # Проверка назначения
    if 'assignee' in item:
        assignee = item['assignee']['display']
        print(f"Исполнитель: {assignee}")

    # Проверка дедлайна
    if 'deadline' in item:
        deadline = item['deadline']['date']
        print(f"Дедлайн: {deadline}")
```

### 2. Создание элемента чек-листа

```python
# Простое создание элемента
item = await client.issues.checklists.create(
    'TASK-123',
    'Протестировать новый API модуль',
    checked=False
)

# С назначением исполнителя (различные форматы)
item = await client.issues.checklists.create(
    'TASK-123',
    'Подготовить документацию',
    checked=False,
    assignee="username"                    # строка с логином
    # assignee=12345                       # ID пользователя
    # assignee={"login": "username"}       # объект с логином
    # assignee={"id": "12345"}            # объект с ID
)

# С дедлайном
item = await client.issues.checklists.create(
    'TASK-123',
    'Подготовить релиз к 31 декабря',
    checked=False,
    deadline={
        'date': '2025-12-31T23:59:59.000+0000',
        'deadlineType': 'date'
    }
)

# Полный пример со всеми параметрами
item = await client.issues.checklists.create(
    'TASK-123',
    'Выполнить комплексную задачу',
    checked=False,
    assignee={"login": "project_manager"},
    deadline={
        'date': '2025-06-15T12:00:00.000+0000',
        'deadlineType': 'date'
    }
)
```

### 3. Обновление элемента чек-листа

```python
# Простое обновление текста
updated_checklist = await client.issues.checklists.update(
    'TASK-123',
    'checklist_item_id',
    'Обновленный текст задачи'
)

# Изменение статуса выполнения
updated_checklist = await client.issues.checklists.update(
    'TASK-123',
    'checklist_item_id',
    'Завершенная задача',
    checked=True
)

# Переназначение исполнителя
updated_checklist = await client.issues.checklists.update(
    'TASK-123',
    'checklist_item_id',
    'Переназначенная задача',
    checked=False,
    assignee="new_assignee"
)

# Полное обновление с дедлайном
updated_checklist = await client.issues.checklists.update(
    'TASK-123',
    'checklist_item_id',
    'Финальная версия задачи',
    checked=True,
    assignee={"login": "reviewer"},
    deadline={
        'date': '2025-07-01T15:30:00.000+0000',
        'deadlineType': 'date'
    }
)

# API возвращает весь обновленный чек-лист
print(f"Обновлено элементов в чек-листе: {len(updated_checklist)}")
```

### 4. Удаление элементов чек-листа

```python
# Удаление одного элемента
result = await client.issues.checklists.delete('TASK-123', 'item_id_to_delete')
print(f"Удален элемент: {result['text']}")

# Удаление всего чек-листа целиком
result = await client.issues.checklists.delete_all('TASK-123')
print("Весь чек-лист удален")

# Пример управления чек-листом
checklist = await client.issues.checklists.get('TASK-123')
if checklist:
    print(f"Найдено элементов: {len(checklist)}")

    # Удаление завершенных элементов
    for item in checklist:
        if item['checked']:
            await client.issues.checklists.delete('TASK-123', item['id'])
            print(f"Удален завершенный элемент: {item['text']}")
```

### 5. Работа с чек-листом в контексте задачи

```python
# Создание задачи с последующим добавлением чек-листа
issue = await client.issues.create(
    summary="Проект с чек-листом",
    queue="PROJECT",
    description="Задача с подробным планом выполнения"
)

# Добавление элементов плана
checklist_items = [
    "Проанализировать требования",
    "Создать техническое задание",
    "Разработать архитектуру",
    "Реализовать функциональность",
    "Провести тестирование",
    "Подготовить документацию",
    "Выполнить деплой"
]

for i, item_text in enumerate(checklist_items, 1):
    await client.issues.checklists.create(
        issue['key'],
        f"{i}. {item_text}",
        checked=False
    )

print(f"Создан проект {issue['key']} с {len(checklist_items)} этапами")

# Отслеживание прогресса
checklist = await client.issues.checklists.get(issue['key'])
completed = sum(1 for item in checklist if item['checked'])
total = len(checklist)
progress = (completed / total) * 100 if total > 0 else 0

print(f"Прогресс: {completed}/{total} ({progress:.1f}%)")
```

### 6. Типичные сценарии использования

```python
# Создание шаблона чек-листа для типовых задач
async def create_deployment_checklist(issue_key):
    checklist_template = [
        ("Подготовить код к релизу", "developer"),
        ("Провести code review", "senior_dev"),
        ("Выполнить тестирование", "tester"),
        ("Обновить документацию", "tech_writer"),
        ("Подготовить план деплоя", "devops"),
        ("Выполнить деплой на staging", "devops"),
        ("Провести приемочные тесты", "qa_lead"),
        ("Деплой на production", "devops"),
        ("Мониторинг после деплоя", "sre")
    ]

    for text, assignee in checklist_template:
        await client.issues.checklists.create(
            issue_key,
            text,
            checked=False,
            assignee=assignee
        )

# Автоматическое отслеживание готовности
async def check_deployment_readiness(issue_key):
    checklist = await client.issues.checklists.get(issue_key)

    # Критические элементы для деплоя
    critical_items = [
        "code review", "тестирование", "staging"
    ]

    ready_for_production = True
    for item in checklist:
        for critical in critical_items:
            if critical.lower() in item['text'].lower():
                if not item['checked']:
                    ready_for_production = False
                    print(f"Не завершено: {item['text']}")

    return ready_for_production
```

#### Планируется:
```python
# Удаление задачи
await client.issues.delete('TASK-123')
```

### 🆕 Кастомные поля (localfields)

Кастомные поля позволяют добавлять произвольные данные к задачам:

```python
# Различные типы данных
localfields = {
    "customPriority": "Очень высокий",    # Строка
    "businessValue": 85,                  # Число
    "estimatedHours": 16.5,               # Десятичное
    "isDraft": False,                     # Boolean
    "deadline": "2025-12-31",             # Дата
    "clientName": "ООО Компания",         # Текст
    "complexity": 7,                      # Рейтинг (1-10)
    "tags_custom": ["urgent", "client"],  # Массив
    "metadata": {                         # Объект
        "source": "api",
        "version": "1.0"
    }
}

# Использование в создании
await client.issues.create(
    summary="Задача",
    queue="PROJ",
    localfields=localfields
)

# Использование в обновлении
await client.issues.update(
    'PROJ-123',
    localfields={
        "progress": "75%",
        "reviewRequired": True,
        "lastModifiedBy": "developer1"
    }
)
```

**Особенности кастомных полей:**
- Поддерживают любые типы данных JSON
- Добавляются напрямую к задаче
- Могут перезаписывать стандартные поля (с предупреждением)
- Логгируются отдельно для отладки
- Работают как в создании, так и в обновлении

### Health Check
```python
# Проверка работоспособности API
user_info = await client.health_check()
print(f"Пользователь: {user_info['display']}")
print(f"Логин: {user_info['login']}")
print(f"Email: {user_info['email']}")
```

### Expand параметры для задач:
- `'transitions'` - переходы по жизненному циклу
- `'attachments'` - вложения

### Планируемые модули:

```python
# Users (Пользователи) - 📋 Планируется
user = await client.users.get(user_id)
users = await client.users.search(query='Иван')

# Queues (Очереди/Проекты) - 📋 Планируется
queue = await client.queues.get(queue_key)
queues = await client.queues.list()

# Comments (Комментарии) - 📋 Планируется
comments = await client.comments.list(issue_id)
comment = await client.comments.create(issue_id, text='Новый комментарий')
```

## 🔧 Настройки логгирования

```python
# Доступные уровни: DEBUG, INFO, WARNING, ERROR, CRITICAL
async with YandexTrackerClient(
    oauth_token=TRACKER_API_KEY,
    org_id=TRACKER_ORG_ID,
    log_level="DEBUG"  # Подробные логи с JSON данными
) as client:
    # ...
```

### Примеры логов с кастомными полями:

```
2025-09-24 17:20:06,865 - client.base.YandexTrackerClient - INFO - HTTP сессия успешно инициализирована
2025-09-24 17:20:06,865 - client.base.YandexTrackerClient - INFO - Выполнение POST запроса к: /issues/
2025-09-24 17:20:06,866 - client.base.YandexTrackerClient - DEBUG - Добавление кастомных полей: ['customPriority', 'businessValue', 'estimatedHours']
2025-09-24 17:20:06,867 - client.base.YandexTrackerClient - DEBUG - Данные запроса: {
  "summary": "Test Issue",
  "queue": {"key": "TREK"},
  "customPriority": "Очень высокий",
  "businessValue": 85,
  "estimatedHours": 16.5
}
2025-09-24 17:20:07,479 - client.base.YandexTrackerClient - INFO - Задача TEST-123 успешно создана
```

## 🏗️ Архитектура

### Модульная структура с lazy loading
```
client/
├── __init__.py      # Экспорт YandexTrackerClient
├── base.py          # YandexTrackerClient + BaseAPI + Health Check
├── issues.py        # IssuesAPI модуль (ПОЛНОСТЬЮ ЗАВЕРШЕН)
├── links.py         # LinksAPI модуль (ПОЛНОСТЬЮ ЗАВЕРШЕН)
├── transitions.py   # TransitionsAPI модуль (ПОЛНОСТЬЮ ЗАВЕРШЕН)
└── checklists.py    # ChecklistAPI модуль (ПОЛНОСТЬЮ ЗАВЕРШЕН)

examples/            # 📚 Структурированные примеры использования
├── EXAMPLE_CONTEXT.md  # Описание системы примеров
└── issues/          # Примеры для модуля задач
    ├── get.py       # ✅ Демонстрация получения задач
    ├── create.py    # ✅ Демонстрация создания задач
    ├── update.py    # ✅ Демонстрация обновления задач
    ├── move.py      # ✅ Демонстрация переноса задач
    ├── count.py     # ✅ Демонстрация подсчета задач с фильтрацией
    ├── search.py    # ✅ Демонстрация поиска задач с расширенными возможностями
    ├── clear_scroll.py # ✅ Демонстрация очистки скролл-сессий
    ├── priorities.py # ✅ Демонстрация получения списка приоритетов
    ├── changelog.py # ✅ Демонстрация получения истории изменений
    ├── transitions.py # ✅ Демонстрация анализа переходов воркфлоу
    ├── execute_transition.py # ✅ Демонстрация выполнения переходов
    ├── links.py     # ✅ Демонстрация создания связей между задачами
    ├── list.py      # ⏳ Заглушка (метод в разработке)
    └── delete.py    # ⏳ Заглушка (метод в разработке)

llm/                 # 🆕 Документация для LLM
└── issues_api.md    # ✅ Краткий справочник Issues API для ИИ
```

### Использование API модулей:
```python
client.health_check()           # Проверка работоспособности API
client.issues.get()             # Получение задач с expand параметрами
client.issues.create()          # Создание задач (POST) + кастомные поля
client.issues.update()          # Обновление задач (PATCH) + кастомные поля
client.issues.move()            # Перенос задач между очередями
client.issues.count()           # Подсчет задач с фильтрацией (POST)
client.issues.search()          # Поиск задач с расширенными возможностями (POST)
client.issues.clear_scroll()    # Очистка скролл-сессий (POST)
client.issues.priorities()      # Получение списка приоритетов (GET)
client.issues.changelog()       # ✅ Получение истории изменений задачи (GET)
client.issues.transitions.get()    # ✅ Получение переходов воркфлоу задачи (GET)
client.issues.transitions.update() # ✅ Выполнение переходов воркфлоу (POST)
client.issues.links.get()          # ✅ Получение связей задачи (GET)
client.issues.links.create()       # ✅ Создание связей между задачами (POST)
client.issues.links.delete()       # ✅ Удаление связей между задачами (DELETE)
client.issues.checklists.get()      # ✅ Получение чек-листа задачи (GET)
client.issues.checklists.create()   # ✅ Создание элемента чек-листа (POST)
client.issues.checklists.update()   # ✅ Обновление элемента чек-листа (PUT)
client.issues.checklists.delete()   # ✅ Удаление элемента чек-листа (DELETE)
client.issues.checklists.delete_all() # ✅ Удаление всего чек-листа (DELETE)
```

### Планируемые модули:
```python
client.users.get()              # 📋 Модуль пользователей
client.queues.list()            # 📋 Модуль очередей/проектов
client.comments.create()        # 📋 Модуль комментариев
```

## 🧪 Тестирование

```bash
# Запуск демонстрации с тестами кастомных полей
python main.py
```

## 📝 Примеры API ответов

### Созданная задача с кастомными полями:
```json
{
  "id": "5fa15a24ac894475dd14ff06",
  "key": "TREK-123",
  "summary": "Test Issue",
  "status": {
    "key": "open",
    "display": "Открыт"
  },
  "queue": {
    "key": "TREK", 
    "display": "Проект Trek"
  },
  "assignee": {
    "id": "1234567890",
    "display": "userlogin"
  },
  "tags": ["тег1", "тег2"],
  "customPriority": "Очень высокий",
  "businessValue": 85,
  "estimatedHours": 16.5,
  "isDraft": false,
  "createdAt": "2025-09-24T14:30:00Z"
}
```

## 🔄 Гибкая типизация

API поддерживает множественные форматы для удобства:

```python
# Очередь (обязательно для создания) - все варианты эквивалентны:
queue="TREK"                    # Строка-ключ
queue=123                       # Число-ID
queue={"key": "TREK"}           # Объект с ключом
queue={"id": "123"}             # Объект с ID

# Исполнитель/Автор:
assignee="userlogin"            # Логин пользователя
assignee=123456                 # ID пользователя  
assignee={"login": "userlogin"} # Объект с логином
assignee={"id": "123456"}       # Объект с ID

# Кастомные поля - любые типы JSON:
localfields = {
    "stringField": "текст",                    # Строка
    "numberField": 42,                         # Число
    "floatField": 3.14,                        # Десятичное
    "booleanField": True,                      # Boolean
    "dateField": "2025-12-31",                 # Дата (строка)
    "arrayField": ["item1", "item2"],          # Массив
    "objectField": {"nested": "value"}         # Объект
}
```

## ⚠️ Обработка ошибок

```python
try:
    # Создание задачи с кастомными полями
    new_issue = await client.issues.create(
        summary="Test Task",
        queue="NONEXISTENT",
        localfields={"customField": "value"}
    )
except aiohttp.ClientResponseError as e:
    if e.status == 404:
        print("Очередь не найдена")
    elif e.status == 403:
        print("Нет доступа к очереди")
    elif e.status == 409:
        print("Задача с таким unique уже существует")
    elif e.status == 401:
        print("Проблема с авторизацией - проверьте токен")
    else:
        print(f"Ошибка API: {e.status}")
except ValueError as e:
    print(f"Ошибка валидации: {e}")
except Exception as e:
    print(f"Неожиданная ошибка: {e}")
```

## 📚 Реальные примеры использования

### Техническая задача с метриками:
```python
issue = await client.issues.create(
    summary="Оптимизация базы данных",
    queue="TECH",
    issue_type="improvement",
    assignee="database-admin",
    localfields={
        "currentResponseTime": "2.5s",
        "targetResponseTime": "500ms",
        "affectedQueries": 15,
        "expectedImprovement": "80%",
        "migrationRequired": True,
        "estimatedDowntime": "30min"
    }
)
```

### Бизнес-задача с клиентскими данными:
```python
issue = await client.issues.create(
    summary="Интеграция с CRM системой клиента",
    queue="INTEGRATION",
    issue_type="feature",
    priority="major",
    assignee="integration-team",
    localfields={
        "clientName": "ООО Ромашка",
        "clientSize": "Enterprise",
        "contractValue": 500000,
        "integrationComplexity": "High",
        "technicalContact": "ivan@romashka.ru",
        "businessContact": "maria@romashka.ru",
        "deadline": "2025-12-31",
        "slaRequired": True
    }
)
```

### Обновление прогресса разработки:
```python
await client.issues.update(
    'TECH-456',
    localfields={
        "developmentProgress": "75%",
        "testsCompleted": 23,
        "testsPassed": 21,
        "testsFailed": 2,
        "codeReviewStatus": "In Progress",
        "performanceBenchmark": "Passed",
        "securityScanStatus": "Clean",
        "deploymentReady": False
    }
)
```

## 💡 Предотвращение дубликатов

Используйте поле `unique` для предотвращения создания дубликатов:

```python
try:
    issue1 = await client.issues.create(
        summary="Уникальная задача",
        queue="PROJ",
        unique="task-2025-001",
        localfields={"version": "1.0"}
    )
    
    # Повторная попытка с тем же unique
    issue2 = await client.issues.create(
        summary="Другое название",
        queue="PROJ", 
        unique="task-2025-001",  # Тот же unique
        localfields={"version": "2.0"}
    )
    
except aiohttp.ClientResponseError as e:
    if e.status == 409:
        print("Задача с таким unique уже существует")
```

## ⚠️ Ограничения

- **Rate limiting**: Yandex Tracker имеет ограничения на количество запросов
- **Права доступа**: API возвращает только доступные пользователю данные
- **OAuth токен**: Требует периодического обновления
- **Очереди**: Для создания задач нужны права на запись в очередь
- **Unique поле**: Должно быть уникально в пределах организации
- **Кастомные поля**: Могут конфликтовать со стандартными полями
- **Валидация**: Клиент проверяет типы, но сервер может иметь дополнительные ограничения

## 🤝 Разработка

### Добавление нового API модуля:

1. Создайте файл `client/new_module.py`
2. Наследуйтесь от `BaseAPI`
3. Добавьте property в `YandexTrackerClient`

```python
# client/new_module.py
from .base import BaseAPI

class NewModuleAPI(BaseAPI):
    async def some_method(self):
        return await self._request('/some-endpoint')

# client/base.py  
@property
def new_module(self):
    if self._new_module is None:
        from .new_module import NewModuleAPI
        self._new_module = NewModuleAPI(self)
    return self._new_module
```

## 📚 Ссылки

- [Yandex Tracker API документация](https://cloud.yandex.ru/docs/tracker/)
- [aiohttp документация](https://docs.aiohttp.org/)
- [Получение OAuth токена](https://oauth.yandex.ru/)

## 📄 Лицензия

Этот проект разрабатывается для внутреннего использования.

---

**Версия**: 1.9.0
**Статус**: FieldsAPI + IssuesAPI + ChecklistAPI ПОЛНОСТЬЮ ЗАВЕРШЕНЫ
**Python**: 3.13+
**Текущий этап**: FieldsAPI РАСШИРЕН - получение и создание кастомных полей с полной типизацией
**Следующий этап**: новые API модули (Users, Queues, Comments)

### История версий:
- **v1.9** - 🆕 **FieldsAPI.create() - создание кастомных полей с полной типизацией и поддержкой всех типов полей**
- **v1.8** - 🆕 **FieldsAPI.get() - получение справочной информации о всех полях задач**
- **v1.7** - 🆕 **ChecklistAPI полностью реализован - управление чек-листами задач (GET, CREATE, UPDATE, DELETE, DELETE_ALL)**
- **v1.6** - 🆕 **IssuesAPI.changelog() + Документация для LLM - ПОЛНОЕ ЗАВЕРШЕНИЕ Issues API**
- **v1.5** - 🆕 **IssuesAPI.links (GET + POST + DELETE) - полное управление связями между задачами**
- **v1.4** - 🆕 **IssuesAPI.transitions() + execute_transition() - полное управление воркфлоу задач**
- **v1.3** - 🆕 **IssuesAPI.priorities() - получение справочной информации о приоритетах**
- **v1.2** - 🆕 **IssuesAPI.clear_scroll() - управление ресурсами при работе с большими данными**
- **v1.1** - 🆕 **IssuesAPI.search() - поиск задач с расширенными возможностями, сортировкой и пагинацией**
- **v1.0** - 🆕 **IssuesAPI.count() - подсчет задач с фильтрацией и языком запросов**
- **v0.9** - 🆕 **Структурированная система примеров examples/ - готовые демонстрации для всех методов**
- **v0.8** - 🆕 **IssuesAPI.move() - перенос задач в другие очереди с полным контролем**
- **v0.7** - 🆕 **Поддержка кастомных полей (localfields) в create() и update()**
- **v0.6** - IssuesAPI.create() + полная поддержка POST
- **v0.5** - IssuesAPI.update() + Health Check + удаление совместимости
- **v0.4** - Модульная архитектура + IssuesAPI.get()
- **v0.3** - Добавление логгирования на русском языке
- **v0.2** - Исправление заголовков и SSL
- **v0.1** - Базовый HTTP клиент с авторизацией
