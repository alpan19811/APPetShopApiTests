import allure
import jsonschema
import pytest
import requests
from .schemas.pet_schema import PET_SCHEMA

BASE_URL = 'http://5.181.109.28:9090/api/v3'


@allure.feature('Pet')
class TestPet:
    @allure.title('Попытка удалить несуществующего питомца')
    def test_delete_nonexistent_pet(self):
        with allure.step('Отправка запроса на удаление несуществующего питомца'):
            response = requests.delete(url=f'{BASE_URL}/pet/9999')

        with allure.step('Проверка статуса ответа'):
            assert response.status_code == 200, 'Код ответа не совпал с ожидаемым'

        with allure.step('Проверка текстового значения ответа'):
            assert response.text == 'Pet deleted', 'Текст ошибки не совпал с ожидаемым'

    @allure.title('Попытка обновить несуществующего питомца')
    def test_update_nonexistent_pet(self):
        with allure.step('Отправка запроса на обновление несуществующего питомца'):
            payload = {
                "id": 9999,
                "name": "Non-existent Pet",
                "status": "available"
            }
            response = requests.put(f'{BASE_URL}/pet', json=payload)

        with allure.step("Проверка статуса ответа"):
            assert response.status_code == 404, 'Код ответа не совпал с ожидаемым'

        with allure.step("Проверка текстового содержимого ответа"):
            assert response.text == "Pet not found", 'Текст ошибки не совпал с ожидаемым'

    @allure.title('Попытка получить информацию о несуществующем питомце')
    def test_get_nonexistent_pet(self):
        with allure.step('Отправка запроса на получение информации о несуществующем питомце'):
            response = requests.get(url=f'{BASE_URL}/pet/9999')

        with allure.step('Проверка статуса ответа'):
            assert response.status_code == 404, 'Код ответа не совпал с ожидаемым'

    @allure.title('Попытка добавить нового питомца')
    def test_add_new_pet(self):
        with allure.step('Отправка запроса на добавление нового питомца'):
            payload = {
                "id": 1,
                "name": "Non-existent Buddy",
                "status": "available"
            }
        with allure.step("Отправка запроса на создание питомца"):
                response = requests.post(f'{BASE_URL}/pet', json=payload)

        with allure.step("Проверка статуса ответа"):
                assert response.status_code == 200, 'Код ответа не совпал с ожидаемым'
                jsonschema.validate(response.json(), PET_SCHEMA)

        with allure.step("Проверка данных питомца в ответе"):
                response_data = response.json()
                assert response_data['id'] == payload['id'], 'ID питомца не совпал с ожидаемым'
                assert response_data['name'] == payload['name'], 'Имя питомца не совпало с ожидаемым'
                assert response_data['status'] == payload['status'], 'Статус питомца не совпал с ожидаемым'

    @allure.title('Получение информации о питомце по ID')
    def test_get_pet_by_id(self, create_pet):
        with allure.step('Получение ID созданного питомца'):
            pet_id = create_pet['id']

        with allure.step("Отправка запроса на получение информации о питомце по ID"):
            response = requests.get(f"{BASE_URL}/pet/{pet_id}")

        with allure.step("Проверка статуса ответа и данных питомца"):
            assert response.status_code == 200
            assert response.json()['id'] == pet_id


    @allure.title("Обновление информации о питомце")
    def test_update_pet(self, create_pet):
        with allure.step('Получение ID созданного питомца'):
            pet_id = create_pet['id']

        with allure.step('Подготовка данных для обновления'):
            update_payload = {
                "id": pet_id,
                "name": "Buddy Updated",
                "status": "sold"
            }

        with allure.step('Отправка PUT-запроса для обновления информации о питомце'):
            response = requests.put(f'{BASE_URL}/pet', json=update_payload)
        with allure.step('Проверка статуса ответа'):
            assert response.status_code == 200, 'Код ответа не совпал с ожидаемым'
            jsonschema.validate(response.json(), PET_SCHEMA)

        with allure.step('Проверка обновленных данных питомца'):
            response_data = response.json()
            assert response_data['id'] == pet_id, 'ID питомца не совпал с ожидаемым'
            assert response_data['name'] == update_payload['name'], 'Имя питомца не обновилось'
            assert response_data['status'] == update_payload['status'], 'Статус питомца не обновился'

    @allure.title('Удаление питомца по ID с использованием фикстуры')
    def test_delete_pet_by_id(self, create_pet):
        with allure.step('Получение ID созданного питомца из фикстуры'):
            pet_id = create_pet['id']

        with allure.step('Отправка DELETE-запроса на удаление питомца'):
            delete_response = requests.delete(f'{BASE_URL}/pet/{pet_id}')

        with allure.step('Проверка статуса и текста ответа'):
            assert delete_response.status_code == 200, 'Код ответа не 200'
            assert delete_response.text == 'Pet deleted', 'Текст ответа не совпадает'

        with allure.step('Проверка, что питомец удалён (GET-запрос должен вернуть 404)'):
            get_response = requests.get(f'{BASE_URL}/pet/{pet_id}')
            assert get_response.status_code == 404, 'Питомец не удалён или ответ не 404'

    @allure.title("Получение списка питомцев по статусу")
    @pytest.mark.parametrize(
        "status, expected_status_code",
        [("available", 200),
         ("pending", 200),
         ("sold", 200),
         ("--", 400),
         (" ", 400)
        ],
    )
    def test_get_pets_status(self, status, expected_status_code):
        with allure.step(f"Отправка запроса на получение питомцев по статусу {status}"):
            response = requests.get(f"{BASE_URL}/pet/findByStatus", params={"status": status})

        with allure.step(f"Проверка статуса ответа и формата данных {expected_status_code}"):
            assert response.status_code == expected_status_code

        if expected_status_code == 200:
            with allure.step("Проверка, что ответ — список питомцев"):
                assert isinstance(response.json(), list)

        else:
            with allure.step("Проверка ошибки 400"):
                error_data = response.json()
                assert isinstance(error_data, dict)

