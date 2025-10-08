from typing import List, Dict, Any, Union
from ..base import BaseAPI

class UsersAPI(BaseAPI):
    """API для работы с пользователями в Yandex Tracker"""

    async def get(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех пользователей организации.

        Returns:
            List[Dict[str, Any]]: Список пользователей с их информацией

        Raises:
            aiohttp.ClientResponseError: При ошибках HTTP запроса
                - 403 если недостаточно прав доступа

        Examples:
            # Получение всех пользователей
            users = await client.users.get()

            # Анализ полученных пользователей
            for user in users:
                user_id = user.get('id')
                login = user.get('login')
                display_name = user.get('display')
                email = user.get('email')

                print(f"ID: {user_id}")
                print(f"Логин: {login}")
                print(f"Имя: {display_name}")
                print(f"Email: {email}")

                # Проверка активности пользователя
                if user.get('dismissed', False):
                    print("Статус: Уволен")
                else:
                    print("Статус: Активен")

                # Информация о департаменте
                if 'department' in user:
                    dept_name = user['department'].get('display', 'Не указан')
                    print(f"Департамент: {dept_name}")

                print("---")

            # Фильтрация активных пользователей
            active_users = [
                user for user in users
                if not user.get('dismissed', False)
            ]
            print(f"Активных пользователей: {len(active_users)}")

            # Поиск пользователя по логину
            target_login = "username"
            target_user = next(
                (user for user in users if user.get('login') == target_login),
                None
            )

            if target_user:
                print(f"Найден пользователь: {target_user['display']}")
            else:
                print(f"Пользователь {target_login} не найден")

            # Группировка по департаментам
            departments = {}
            for user in users:
                if 'department' in user:
                    dept_name = user['department'].get('display', 'Без департамента')
                    if dept_name not in departments:
                        departments[dept_name] = []
                    departments[dept_name].append(user)

            for dept_name, dept_users in departments.items():
                print(f"{dept_name}: {len(dept_users)} пользователей")

            # Поиск пользователей по email домену
            target_domain = "@company.com"
            company_users = [
                user for user in users
                if user.get('email', '').endswith(target_domain)
            ]
            print(f"Пользователей с доменом {target_domain}: {len(company_users)}")

            # Получение списка логинов для использования в других API
            user_logins = [user['login'] for user in users if 'login' in user]
            print(f"Всего логинов: {len(user_logins)}")

            # Статистика по пользователям
            total_users = len(users)
            dismissed_users = len([u for u in users if u.get('dismissed', False)])
            active_users_count = total_users - dismissed_users

            print(f"Общее количество пользователей: {total_users}")
            print(f"Активных: {active_users_count}")
            print(f"Уволенных: {dismissed_users}")
        """
        self.logger.info("Получение списка пользователей организации")

        endpoint = '/users'

        result = await self._request(endpoint, 'GET')

        # Проверяем, что получили список
        if not isinstance(result, list):
            self.logger.warning(f"Неожиданный тип ответа: {type(result)}")
            result = []

        users_count = len(result)
        self.logger.info(f"Получено {users_count} пользователей")

        if users_count > 0:
            # Анализируем пользователей для логирования
            active_users = [user for user in result if not user.get('dismissed', False)]
            dismissed_users = [user for user in result if user.get('dismissed', False)]

            active_count = len(active_users)
            dismissed_count = len(dismissed_users)

            self.logger.debug(f"Активных пользователей: {active_count}")
            self.logger.debug(f"Уволенных пользователей: {dismissed_count}")

            # Анализируем департаменты
            departments = set()
            for user in result:
                if 'department' in user and 'display' in user['department']:
                    departments.add(user['department']['display'])

            if departments:
                self.logger.debug(f"Количество департаментов: {len(departments)}")

            # Анализируем email домены
            email_domains = set()
            for user in result:
                if 'email' in user:
                    email = user['email']
                    if '@' in email:
                        domain = email.split('@')[-1]
                        email_domains.add(domain)

            if email_domains:
                self.logger.debug(f"Email домены: {', '.join(sorted(email_domains))}")

        return result

    async def get_user(self, user_id: Union[str, int]) -> Dict[str, Any]:
        """
        Получение информации о конкретном пользователе.

        Args:
            user_id (Union[str, int]): Логин или ID пользователя

        Returns:
            Dict[str, Any]: Информация о пользователе

        Raises:
            ValueError: При некорректных параметрах
            aiohttp.ClientResponseError: При ошибках HTTP запроса
                - 404 если пользователь не найден
                - 403 если недостаточно прав доступа

        Examples:
            # Получение пользователя по логину
            user = await client.users.get_user('username')

            # Получение пользователя по ID
            user = await client.users.get_user(123456)

            # Анализ информации о пользователе
            user_id = user.get('id')
            login = user.get('login')
            display_name = user.get('display')
            email = user.get('email')

            print(f"ID: {user_id}")
            print(f"Логин: {login}")
            print(f"Имя: {display_name}")
            print(f"Email: {email}")

            # Проверка статуса пользователя
            if user.get('dismissed', False):
                print("Статус: Уволен")
                if 'dismissalDate' in user:
                    dismiss_date = user['dismissalDate']
                    print(f"Дата увольнения: {dismiss_date}")
            else:
                print("Статус: Активен")

            # Информация о департаменте
            if 'department' in user:
                dept_info = user['department']
                dept_name = dept_info.get('display', 'Не указан')
                dept_id = dept_info.get('id', 'N/A')
                print(f"Департамент: {dept_name} (ID: {dept_id})")

            # Информация о руководителе
            if 'chief' in user:
                chief_info = user['chief']
                chief_name = chief_info.get('display', 'Не указан')
                chief_login = chief_info.get('login', 'N/A')
                print(f"Руководитель: {chief_name} ({chief_login})")

            # Контактная информация
            if 'phone' in user:
                print(f"Телефон: {user['phone']}")

            if 'position' in user:
                print(f"Должность: {user['position']}")

            # Информация о последней активности
            if 'lastSeenAt' in user:
                last_seen = user['lastSeenAt']
                print(f"Последняя активность: {last_seen}")

            # Проверка прав доступа
            if 'hasFullAccess' in user:
                access_level = "Полный доступ" if user['hasFullAccess'] else "Ограниченный доступ"
                print(f"Уровень доступа: {access_level}")

            # Получение аватара пользователя
            if 'avatarUrl' in user:
                avatar_url = user['avatarUrl']
                print(f"Аватар: {avatar_url}")

            # Проверка на робота/служебный аккаунт
            if user.get('robot', False):
                print("Это робот/служебный аккаунт")

            # Информация о создании аккаунта
            if 'createdAt' in user:
                created_date = user['createdAt']
                print(f"Аккаунт создан: {created_date}")

            # Локаль пользователя
            if 'locale' in user:
                user_locale = user['locale']
                print(f"Локаль: {user_locale}")

            # Использование в других API вызовах
            # Например, назначение пользователя на задачу
            issue_data = {
                "assignee": user['login']  # или user['id']
            }
        """
        # Валидация параметров
        if not user_id:
            raise ValueError("user_id должен быть указан")

        if not isinstance(user_id, (str, int)):
            raise ValueError("user_id должен быть строкой или числом")

        if isinstance(user_id, str) and not user_id.strip():
            raise ValueError("user_id (строка) должен быть непустым")

        # Преобразуем в строку для URL
        user_identifier = str(user_id).strip()

        self.logger.info(f"Получение информации о пользователе: {user_identifier}")

        endpoint = f'/users/{user_identifier}'

        result = await self._request(endpoint, 'GET')

        # Логируем полученную информацию
        if isinstance(result, dict):
            login = result.get('login', 'N/A')
            display_name = result.get('display', 'N/A')
            user_id_response = result.get('id', 'N/A')

            self.logger.info(f"Получена информация о пользователе: {display_name} ({login}, ID: {user_id_response})")

            # Дополнительная информация для логирования
            if result.get('dismissed', False):
                self.logger.debug(f"Пользователь {login} уволен")
                if 'dismissalDate' in result:
                    dismiss_date = result['dismissalDate']
                    self.logger.debug(f"Дата увольнения: {dismiss_date}")
            else:
                self.logger.debug(f"Пользователь {login} активен")

            if 'department' in result:
                dept_name = result['department'].get('display', 'N/A')
                self.logger.debug(f"Департамент: {dept_name}")

            if 'chief' in result:
                chief_name = result['chief'].get('display', 'N/A')
                self.logger.debug(f"Руководитель: {chief_name}")

            if result.get('robot', False):
                self.logger.debug("Это робот/служебный аккаунт")

        return result