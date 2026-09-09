# llm_agent/tool_random_user.py
import json
from typing import Optional, List, Dict, Any
import requests


class RandomUserTool:
    name = "random_user"
    description = (
        "Генерирует фейковые дпользовательские данные"
        "через API randomuser.me. Принимает количество пользователей, пол и национальность"
    )

    def use(
            self,
            count: int = 1,
            include_fields: Optional[List[str]] = None,
    )-> str:
        try:
            print(f"> Генерирует {count} пользователей...")

            if count > 1:
                count = 1
            elif count > 500:
                count = 500
                print(f"> Количество ограничено до 500")

            params = {
                "results": count,
                "inc": "name,email,phone,cell,location,dob,picture,gender,nat,login",
                "noinfo": True
            }
            print(f"> Отправлет запрос...")
            response = requests.get("https://randomuser.me/api/", params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            users = data.get("results", [])

            if not users:
                return "Ошибка: API не вернул данных"

            print(f"> Получено {len(users)} пользователей")

            processed_users= []
            for user in users:
                processed_users.append(self._process_user(user, include_fields))

            print(f"> Успешно обработано {len(processed_users)} пользователей")

            return json.dumps(processed_users, ensure_ascii=False, indent=2)

        except requests.exceptions.RequestException as e:
            print(f"> Ошибка при запросе к API: {e}")
            return f"Ошибка при запросе к API randomuser.me: {e}"
        except Exception as e:
            print(f"> Ошибка при генерации пользователей: {e}")
            return f"Произошла ошибка при генерации пользовательских данных: {e}"

    def _process_user(self, user: Dict[str, Any], include_fields: Optional[List[str]]) -> Dict[str, Any]:
        user["full_name"] = self._get_full_name(user)
        user["address"] = self._get_address(user)

        if not include_fields:
            return user

        return {field: user[field] for field in include_fields if field in user}

    def _get_full_name(self, user: Dict[str, Any]) -> str:
        name_data = user.get("name", {})
        first = name_data.get("first", "")
        last = name_data.get("last", "")
        return f"{first} {last}".strip()

    def _get_address(self, user: Dict[str, Any]) -> str:
        location = user.get("location", {})
        street = location.get("street", {})
        street_name = street.get("name", "")
        street_number = street.get("number", "")
        city = location.get("city", "")
        state = location.get("state", "")
        country = location.get("country", "")
        postcode = location.get("postcode", "")

        address_parts = []
        if street_number and street_name:
            address_parts.append(f"{street_number} {street_name}")
        elif street_name:
            address_parts.append(street_name)

        if city:
            address_parts.append(city)
        if state:
            address_parts.append(state)
        if postcode:
            address_parts.append(str(postcode))
        if country:
            address_parts.append(country)

        return ", ".join(address_parts)