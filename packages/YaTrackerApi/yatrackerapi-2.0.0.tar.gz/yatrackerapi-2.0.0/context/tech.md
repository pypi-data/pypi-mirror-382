## Описание проекта
**YaTrackerApi** - асинхронный API клиент для Яндекс Трекера на Python с модульной архитектурой. Цель - создать удобную, расширяемую библиотеку для работы с API Yandex.Tracker с полной типизацией и поддержкой всех основных операций.

**Статус**: Опубликован на PyPI - https://pypi.org/project/YaTrackerApi/
**Версия**: 1.9.0
**Лицензия**: MIT

## Технологический стек
- **Python**: 3.9+ (совместимость с широким спектром проектов)
- **Менеджер пакетов**: uv (современная замена pip/poetry)
- **HTTP клиент**: aiohttp (асинхронные HTTP запросы)
- **Загрузка env**: python-dotenv (переменные окружения)
- **Архитектура**: Модульная с lazy loading
- **Типизация**: Полная поддержка типов для всех методов
- **Публикация**: PyPI через uv publish

## Важные заметки для разработки
- **Всегда использовать** `async with` для создания клиента
- **Модули загружаются** только при первом обращении (lazy loading)
- **Все API модули** наследуются от BaseAPI
- **Логгирование** ведется через единый логгер основного клиента
- **Типизация** поддерживает множественные форматы данных
- **Валидация** происходит на стороне клиента перед отправкой
- **Создание задач** требует обязательных полей summary и queue
- **Поле unique** помогает предотвратить создание дубликатов
- **Различия POST/PATCH** - в создании нет операций add/remove
- **🆕 Кастомные поля** добавляются напрямую в payload задачи
- **🆕 Конфликты полей** - кастомные могут перезаписать стандартные (с предупреждением)
- **🆕 Любые типы JSON** поддерживаются в localfields
- **🆕 Примеры для каждого метода** обязательно создавать в examples/{module}/{method}.py

## Архитектурные преимущества
1. **Модульность** - легко добавлять новые API модули
2. **Переиспользование** - BaseAPI избавляет от дублирования
3. **Типизация** - четкие типы для всех методов с валидацией
4. **Расширяемость** - простое добавление новых методов
5. **Тестируемость** - каждый модуль можно тестировать отдельно
6. **Читаемость** - `client.issues.create()` интуитивно понятно
7. **Безопасность** - валидация данных перед отправкой
8. **Гибкость** - множественные форматы для одного поля
9. **Предсказуемость** - четкое различие между CREATE и UPDATE
10. **🆕 Расширяемость пользователем** - кастомные поля для любых нужд
11. **🆕 Отладка** - отдельное логгирование кастомных полей
12. **🆕 Обучаемость** - структурированные практические примеры

## Архитектурные принципы

### 🎯 Lazy Loading
```python
@property
def issues(self):
    if self._issues is None:
        from .issues import IssuesAPI
        self._issues = IssuesAPI(self)
    return self._issues
```

### 🔗 Единый HTTP интерфейс  
```python
class BaseAPI(ABC):
    async def _request(self, endpoint, method='GET', data=None, params=None):
        return await self.client.request(endpoint, method, data, params)
```

### 🏷️ Умная типизация с валидацией
```python
# Автоматическое определение формата данных
if isinstance(queue, str):
    payload['queue'] = {"key": queue}
elif isinstance(queue, int):
    payload['queue'] = {"id": str(queue)}
elif isinstance(queue, dict):
    payload['queue'] = queue
else:
    raise ValueError(f"queue должен быть строкой, числом или объектом")
```

### 🆕 Обработка кастомных полей
```python
# Добавление кастомных полей в payload
if localfields is not None:
    if not isinstance(localfields, dict):
        raise ValueError(f"localfields должен быть словарем")
    
    self.logger.debug(f"Добавление кастомных полей: {list(localfields.keys())}")
    
    # Добавляем каждое кастомное поле напрямую в payload
    for field_key, field_value in localfields.items():
        if field_key in payload:
            self.logger.warning(f"Кастомное поле '{field_key}' перезаписывает стандартное поле")
        payload[field_key] = field_value
```

### 🔍 Различие между CREATE и UPDATE
```python
# В CREATE - только списки
followers = ["user1", "user2"]           # Замена
tags = ["tag1", "tag2"]                  # Замена

# В UPDATE - списки или операции add/remove  
followers = ["user1", "user2"]           # Замена
followers = {"add": ["user1"]}           # Добавить
followers = {"remove": ["user2"]}        # Удалить
tags = {"add": ["tag1"], "remove": ["tag2"]}  # Комбинировать

# Кастомные поля - в обоих случаях одинаково
localfields = {"field1": "value1", "field2": 123}  # И для CREATE, и для UPDATE
```

## Настройки aiohttp
- **SSL контекст**: ssl.create_default_context()
- **Connector limits**: limit=100, limit_per_host=30
- **DNS cache**: ttl_dns_cache=300
- **Timeouts**: total=30s, connect=10s, sock_read=10s

## ✅ YandexTrackerClient (client/base.py)
- **Async context manager** для управления сессиями
- **HTTP методы**: request() - базовый метод для всех запросов
- **SSL/TLS поддержка** с правильными настройками  
- **Система логгирования** на русском языке с JSON форматированием
- **Обработка ошибок** с детализацией
- **Lazy loading** API модулей

## Логгирование
- **Уровни**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Язык**: русский
- **Формат**: %(asctime)s - %(name)s - %(levelname)s - %(message)s
- **JSON данные**: красивый вывод JSON в DEBUG режиме
- **Модульность**: каждый API модуль использует логгер основного клиента
- **🆕 Кастомные поля**: отдельное логгирование для отладки

### Примеры логов с кастомными полями
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