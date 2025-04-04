import pytest
import requests
from datetime import datetime

BASE_URL = 'http://5.181.109.28:9090/api/v3'

@pytest.fixture(scope="function")
def create_pet():
    '''Фикстура для создания питомца.'''
    payload = {
        "id": 1,
        "name": "Non-existent Buddy",
        "status": "available"
    }
    response = requests.post(f'{BASE_URL}/pet', json=payload)
    assert response.status_code == 200
    return response.json()

@pytest.fixture(scope="function")
def create_order():
    '''Фикстура для создания заказа.'''
    order_data = {
        "id": 1,
        "petId": 1,
        "quantity": 1,
        "shipDate": datetime.utcnow().isoformat() + "Z",
        "status": "approved",
        "complete": True
    }
    response = requests.post(f'{BASE_URL}/store/order', json=order_data)
    assert response.status_code == 200
    return response.json()