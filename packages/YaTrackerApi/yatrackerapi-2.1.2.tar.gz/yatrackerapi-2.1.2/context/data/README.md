# 📊 Структуры данных и API документация

Данная папка содержит полную документацию по структурам данных и API методам Yandex Tracker клиента.

## 📁 Структура документации

### 🏗️ [`types.md`](./types.md) - Базовые типы и структуры
- Определения всех типов данных (QueueType, AssigneeType, etc.)
- Примеры использования типов
- Структуры ответов API (Task, User, Comment, Entity, Field)
- Типы связей между задачами и сущностями

### 📋 [`issues.md`](./issues.md) - API для работы с задачами
- Полная документация IssuesAPI
- Основные операции: get, create, update, move
- Поиск и аналитика: search, count, priorities, changelog
- Подмодули: links, transitions, checklists, comments, fields

### 🏢 [`entities.md`](./entities.md) - API для работы с сущностями
- Управление проектами, портфелями, целями
- CRUD операции с сущностями
- Поиск и история изменений
- Подмодули: links, checklists, bulk операции

### 🏷️ [`fields.md`](./fields.md) - API для полей
- Управление кастомными полями
- Локальные поля очередей
- Типы полей и провайдеры опций
- Создание и обновление полей

### 👥 [`users.md`](./users.md) - API для пользователей
- Получение списка пользователей
- Получение информации о конкретном пользователе
- Структуры данных пользователей

## 🚀 Быстрый старт

### Создание простой задачи
```python
task = await client.issues.create(
    summary="Новая задача",
    queue="DEVELOPMENT",
    assignee="developer",
    priority="normal"
)
```

### Поиск задач
```python
issues = await client.issues.search(
    filter="assignee: me() AND status: open",
    order="updated"
)
```

### Создание проекта
```python
project = await client.entities.create(
    entity_type="project",
    summary="Новый проект",
    lead="manager"
)
```

### Добавление комментария
```python
await client.issues.comments.create(
    issue_id="TASK-123",
    text="Работа завершена ✅",
    summonees=["reviewer"]
)
```

## 📚 Навигация

- **Типы данных** → [`types.md`](./types.md)
- **Задачи** → [`issues.md`](./issues.md)
- **Сущности** → [`entities.md`](./entities.md)
- **Поля** → [`fields.md`](./fields.md)
- **Пользователи** → [`users.md`](./users.md)