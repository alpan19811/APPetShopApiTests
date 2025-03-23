import allure
import requests

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
            response = requests.post(f'{BASE_URL}/pet', json=payload)

            with allure.step("Проверка статуса ответа"):
                assert response.status_code == 200, 'Код ответа не совпал с ожидаемым'

            with allure.step("Проверка данных питомца в ответе"):
                response_data = response.json()
                assert response_data['id'] == payload['id'], 'ID питомца не совпал с ожидаемым'
                assert response_data['name'] == payload['name'], 'Имя питомца не совпало с ожидаемым'
                assert response_data['status'] == payload['status'], 'Статус питомца не совпал с ожидаемым'



