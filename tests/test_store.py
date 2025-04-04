import allure
import jsonschema
import requests
from datetime import datetime
from .schemas.store_schema import ORDER_SCHEMA

BASE_URL = 'http://5.181.109.28:9090/api/v3'

@allure.feature('Store')
class TestStore:
    allure.title('Размещение нового заказа')
    def test_place_order(self):
        order_data = {
            "id": 1,
            "petId": 1,
            "quantity": 1,
            "shipDate": datetime.utcnow().isoformat() + "Z",
            "status": "approved",
            "complete": True
        }

        with allure.step('Отправка POST-запроса для размещения заказа'):
            response = requests.post(url=f'{BASE_URL}/store/order', json=order_data)

        with allure.step('Проверка статус-кода 200'):
            assert response.status_code == 200, f"Фактический код: {response.status_code}"

        with allure.step("Валидация JSON-схемы ответа"):
            jsonschema.validate(response.json(), ORDER_SCHEMA)

        with allure.step("Проверка значений в ответе"):
            response_data = response.json()
            assert response_data["id"] == order_data["id"], "Некорректный ID заказа"
            assert response_data["petId"] == order_data["petId"], "Некорректный petId"
            assert response_data["quantity"] == order_data["quantity"], "Некорректное quantity"
            assert response_data["status"] == order_data["status"], "Некорректный статус"
            assert response_data["complete"] == order_data["complete"], "Некорректный флаг complete"

    @allure.title('Получение информации о заказе по ID')
    def test_get_order_by_id(self):
        test_order_id = 1

        with allure.step("Отправка GET-запроса для получения заказа"):
            response = requests.get(url=f'{BASE_URL}/store/order/{test_order_id}')

        with allure.step('Проверка статус-кода 200'):
            assert response.status_code == 200, f"Фактический код: {response.status_code}"

        with allure.step("Валидация JSON-схемы ответа"):
            jsonschema.validate(response.json(), ORDER_SCHEMA)

        with allure.step("Проверка ID в ответе"):
            response_data = response.json()
            assert response_data["id"] == test_order_id, "ID заказа не соответствует запрошенному"

        with allure.step("Проверка обязательных полей"):
            assert "petId" in response_data, "Отсутствует petId в ответе"
            assert "quantity" in response_data, "Отсутствует quantity в ответе"
            assert "status" in response_data, "Отсутствует status в ответе"
            assert "complete" in response_data, "Отсутствует complete в ответе"

    @allure.title('Удаление заказа по ID')
    def test_delete_order(self):
        """Тест проверяет корректное удаление заказа через DELETE endpoint"""

        valid_order_id = 1

        with allure.step('0. Создание тестового заказа'):
            order_data = {
                "id": 1,
                "petId": 1,
                "quantity": 1,
                "shipDate": datetime.utcnow().isoformat() + "Z",
                "status": "approved",
                "complete": True
            }
            create_response = requests.post(f'{BASE_URL}/store/order', json=order_data)
            assert create_response.status_code == 200, "Не удалось создать тестовый заказ"

        with allure.step('1. Отправка DELETE-запроса'):
            delete_response = requests.delete(url=f'{BASE_URL}/store/order/{valid_order_id}')


        with allure.step('2. Проверка ответа на удаление'):
            assert delete_response.status_code == 200, (
                f"Ожидался код 200, получен {delete_response.status_code}."
                )


        with allure.step("3. Проверка, что заказ удален"):
            get_response = requests.get(f'{BASE_URL}/store/order/{valid_order_id}')
            assert get_response.status_code == 404, "Заказ все еще доступен"

        with allure.step("4. Проверка обработки невалидных ID"):

            with allure.step('4.1. Проверка ID > 1000'):
                invalid_response = requests.delete(f'{BASE_URL}/store/order/1001')
                allure.attach(
                    f"Фактический код для ID > 1000: {invalid_response.status_code}",
                    name="Информация о поведении API"
                )

            with allure.step('4.2. Проверка строкового ID'):
                string_id_response = requests.delete(f'{BASE_URL}/store/order/abc')
                assert string_id_response.status_code == 400, (
                    f"Ожидался код 400 для строкового ID, получен {string_id_response.status_code}"
                )

    @allure.title('Попытка получить информацию о несуществующем заказе')
    def test_get_nonexistent_order(self):
        """Тест проверяет корректную обработку запроса несуществующего заказа"""

        non_existent_order_id = 9999

        with allure.step('1. Отправка GET-запроса для несуществующего заказа'):
            response = requests.get(f'{BASE_URL}/store/order/{non_existent_order_id}')

        with allure.step('2. Проверка статус-кода 404'):
            assert response.status_code == 404, (
                f"Ожидался код 404, получен {response.status_code}"
            )

        with allure.step('3. Проверка сообщения об ошибке (опционально)'):
            if response.text:
                allure.attach(f"Тело ответа: {response.text}", name="Детали ошибки")

    @allure.title('Получение инвентаря магазина')
    def test_get_store_inventory(self):
        """Тест проверяет корректное получение инвентаря магазина"""

        with allure.step('1. Отправка GET-запроса на /store/inventory'):
            response = requests.get(f'{BASE_URL}/store/inventory')

        with allure.step('2. Проверка статус-кода 200'):
            assert response.status_code == 200, (
                f'Ожидался статус код 200, получен {response.status_code}'
            )

        with allure.step('3. Валидация структры ответа по схеме'):
            inventory_schema = {
                "type": "object",
                "additionalProperties": {
                    "type": "integer"
                },
                "example": {
                    "additionalProp1": 0,
                    "additionalProp2": 0,
                    "additionalProp3": 0
                }
            }

            inventory_data = response.json()
            jsonschema.validate(inventory_data, inventory_schema)

        with allure.step('4. Проверка наличия данных'):
            assert inventory_data, "Инвентарь не должен быть пустым"
            allure.attach(
                f'Полученный инвентарь: {inventory_data}',
                name="Данные инвентаря"
            )







