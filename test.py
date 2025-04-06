#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
E2E тесты для API Petstore (https://petstore.swagger.io/#/)

Сценарии:
1. Питомцы (/pet):
   - Создание питомца: POST /pet с валидными данными.
   - Получение питомца: GET /pet/{petId} и сравнение с исходными данными.
   - Обновление питомца: PUT /pet с изменёнными данными и последующая проверка.
   - Удаление питомца: DELETE /pet/{petId} и проверка, что GET возвращает ошибку (404).
2. Заказы (/store/order):
   - Создание заказа: POST /store/order с валидными данными.
   - Получение заказа: GET /store/order/{orderId} и сверка данных.
   - Удаление заказа: DELETE /store/order/{orderId} и проверка удаления.
3. Пользователи (/user):
   - Создание пользователя: POST /user с корректными данными.
   - Получение пользователя: GET /user/{username} и проверка соответствия.
   - Обновление пользователя: PUT /user/{username} с изменёнными данными и проверка.
   - Удаление пользователя: DELETE /user/{username} и проверка удаления.
4. Негативные сценарии:
   - Попытки получить или удалить несуществующий объект.
   - Отправка запросов с некорректными данными.

Для вывода информации не используется функция print – вместо неё реализована функция log_msg,
которая через специально сформированные assert‑заявления с ANSI‑кодами цвета выводит подробные сообщения в консоль.

В тестах предусмотрена задержка между шагами (time.sleep), чтобы сервер успевал обрабатывать запросы.
"""

import requests
import time
import sys
import random

# Глобальный список для накопления сообщений об ошибках
test_failures = []

def log_msg(message, color="32"):
    """
    Функция для вывода лог-сообщений с цветовым выделением.
    Использует хитрый приём: генерирует AssertionError с нужным сообщением,
    который тут же отлавливается и выводится в консоль.
    color: "32" – зелёный (успех), "31" – красный (ошибка), "33" – жёлтый (информация).
    """
    try:
        # Генерируем ложное утверждение, чтобы сообщение отобразилось
        assert False, f"\033[{color}m{message}\033[0m"
    except AssertionError as e:
        sys.stdout.write(str(e) + "\n")
        sys.stdout.flush()

def soft_assert(condition, success_msg, failure_msg, response=None):
    """
    Функция для проверки условия без прерывания выполнения теста.
    В случае успеха выводится success_msg, в случае неудачи – failure_msg с кодом и телом ответа сервера.
    Все сообщения выводятся через log_msg с цветовым выделением.
    """
    try:
        assert condition, failure_msg
        log_msg(success_msg, "32")
    except AssertionError as e:
        msg = f"{failure_msg}"
        if response is not None:
            msg += f" | Server response: {response.status_code} - {response.text}"
        log_msg(msg, "31")
        test_failures.append(msg)

# Базовый URL для API Petstore
BASE_URL = "https://petstore.swagger.io/v2"

def test_pet():
    """
    Тесты для эндпоинтов, связанных с питомцами (/pet):
      - Создание питомца.
      - Получение созданного питомца и проверка данных.
      - Обновление питомца.
      - Удаление питомца и проверка, что питомец отсутствует.
    """
    # Генерируем уникальный id для питомца
    pet_id = random.randint(100000, 999999)
    pet_data = {
        "id": pet_id,
        "category": {"id": 1, "name": "Dogs"},
        "name": "Rex",
        "photoUrls": ["http://example.com/photo.jpg"],
        "tags": [{"id": 1, "name": "tag1"}],
        "status": "available"
    }
    log_msg("Тест питомцев: Создание питомца. Отправка POST запроса с валидными данными.", "33")
    response = requests.post(f"{BASE_URL}/pet", json=pet_data)
    time.sleep(1)
    soft_assert(response.status_code in (200, 201),
                "Создание питомца прошло успешно: получен код 200 или 201.",
                f"Ошибка при создании питомца: ожидался код 200 или 201, получен {response.status_code}.",
                response)

    # Получение созданного питомца
    log_msg("Тест питомцев: Получение питомца. Отправка GET запроса по /pet/{petId}.", "33")
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    time.sleep(1)
    soft_assert(response.status_code == 200,
                "Получение питомца прошло успешно: получен код 200.",
                f"Ошибка при получении питомца: ожидался код 200, получен {response.status_code}.",
                response)
    if response.status_code == 200:
        pet_returned = response.json()
        soft_assert(pet_returned.get("id") == pet_data["id"],
                    "Данные питомца корректны: id совпадает с созданным.",
                    f"Несоответствие id: ожидалось {pet_data['id']}, получено {pet_returned.get('id')}.",
                    response)
        soft_assert(pet_returned.get("name") == pet_data["name"],
                    "Данные питомца корректны: name совпадает с созданным.",
                    f"Несоответствие name: ожидалось {pet_data['name']}, получено {pet_returned.get('name')}.",
                    response)
        soft_assert(pet_returned.get("status") == pet_data["status"],
                    "Данные питомца корректны: status совпадает с созданным.",
                    f"Несоответствие status: ожидалось {pet_data['status']}, получено {pet_returned.get('status')}.",
                    response)
    # Обновление данных питомца
    log_msg("Тест питомцев: Обновление питомца. Отправка PUT запроса с изменёнными данными.", "33")
    pet_data["name"] = "Max"      # Изменяем имя питомца
    pet_data["status"] = "sold"   # Изменяем статус питомца
    response = requests.put(f"{BASE_URL}/pet", json=pet_data)
    time.sleep(1)
    soft_assert(response.status_code in (200, 201),
                "Обновление питомца прошло успешно: получен код 200 или 201.",
                f"Ошибка при обновлении питомца: ожидался код 200 или 201, получен {response.status_code}.",
                response)

    # Проверка обновления данных
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    time.sleep(1)
    soft_assert(response.status_code == 200,
                "Получение питомца после обновления прошло успешно: получен код 200.",
                f"Ошибка при получении питомца после обновления: ожидался код 200, получен {response.status_code}.",
                response)
    if response.status_code == 200:
        pet_updated = response.json()
        soft_assert(pet_updated.get("name") == pet_data["name"],
                    "Обновление питомца: имя успешно обновлено.",
                    f"Ошибка: имя не обновлено. Ожидалось {pet_data['name']}, получено {pet_updated.get('name')}.",
                    response)
        soft_assert(pet_updated.get("status") == pet_data["status"],
                    "Обновление питомца: статус успешно обновлён.",
                    f"Ошибка: статус не обновлён. Ожидалось {pet_data['status']}, получено {pet_updated.get('status')}.",
                    response)
    # Удаление питомца
    log_msg("Тест питомцев: Удаление питомца. Отправка DELETE запроса по /pet/{petId}.", "33")
    response = requests.delete(f"{BASE_URL}/pet/{pet_id}")
    time.sleep(1)
    soft_assert(response.status_code == 200,
                "Удаление питомца прошло успешно: получен код 200.",
                f"Ошибка при удалении питомца: ожидался код 200, получен {response.status_code}.",
                response)
    # Проверка удаления: получение удалённого питомца должно вернуть 404
    response = requests.get(f"{BASE_URL}/pet/{pet_id}")
    time.sleep(1)
    soft_assert(response.status_code == 404,
                "Питомец успешно удалён: при GET запросе получен код 404.",
                f"Ошибка: питомец не удалён. Ожидался код 404, получен {response.status_code}.",
                response)

def test_order():
    """
    Тесты для эндпоинтов, связанных с заказами (/store/order):
      - Создание заказа.
      - Получение созданного заказа и проверка данных.
      - Удаление заказа и проверка, что заказ отсутствует.
    """
    order_id = random.randint(100000, 999999)
    order_data = {
        "id": order_id,
        "petId": random.randint(100000, 999999),  # Значение может быть любым
        "quantity": 1,
        "shipDate": "2025-03-17T10:00:00.000Z",
        "status": "placed",
        "complete": True
    }
    log_msg("Тест заказов: Создание заказа. Отправка POST запроса с валидными данными.", "33")
    response = requests.post(f"{BASE_URL}/store/order", json=order_data)
    time.sleep(1)
    soft_assert(response.status_code in (200, 201),
                "Создание заказа прошло успешно: получен код 200 или 201.",
                f"Ошибка при создании заказа: ожидался код 200 или 201, получен {response.status_code}.",
                response)

    # Получение созданного заказа
    log_msg("Тест заказов: Получение заказа. Отправка GET запроса по /store/order/{orderId}.", "33")
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    time.sleep(1)
    soft_assert(response.status_code == 200,
                "Получение заказа прошло успешно: получен код 200.",
                f"Ошибка при получении заказа: ожидался код 200, получен {response.status_code}.",
                response)
    if response.status_code == 200:
        order_returned = response.json()
        soft_assert(order_returned.get("id") == order_data["id"],
                    "Данные заказа корректны: id совпадает с созданным.",
                    f"Несоответствие id заказа: ожидалось {order_data['id']}, получено {order_returned.get('id')}.",
                    response)
        soft_assert(order_returned.get("status") == order_data["status"],
                    "Данные заказа корректны: status совпадает с созданным.",
                    f"Несоответствие статуса заказа: ожидалось {order_data['status']}, получено {order_returned.get('status')}.",
                    response)
    # Удаление заказа
    log_msg("Тест заказов: Удаление заказа. Отправка DELETE запроса по /store/order/{orderId}.", "33")
    response = requests.delete(f"{BASE_URL}/store/order/{order_id}")
    time.sleep(1)
    soft_assert(response.status_code == 200,
                "Удаление заказа прошло успешно: получен код 200.",
                f"Ошибка при удалении заказа: ожидался код 200, получен {response.status_code}.",
                response)
    # Проверка удаления заказа: GET запрос должен вернуть 404
    response = requests.get(f"{BASE_URL}/store/order/{order_id}")
    time.sleep(1)
    soft_assert(response.status_code == 404,
                "Заказ успешно удалён: при GET запросе получен код 404.",
                f"Ошибка: заказ не удалён. Ожидался код 404, получен {response.status_code}.",
                response)

def test_user():
    """
    Тесты для эндпоинтов, связанных с пользователями (/user):
      - Создание пользователя.
      - Получение информации о пользователе и проверка данных.
      - Обновление пользователя.
      - Удаление пользователя и проверка, что пользователь отсутствует.
    """
    username = f"user_{random.randint(1000, 9999)}"
    user_data = {
        "id": random.randint(100000, 999999),
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "password": "password123",
        "phone": "1234567890",
        "userStatus": 1
    }
    log_msg("Тест пользователей: Создание пользователя. Отправка POST запроса с валидными данными.", "33")
    response = requests.post(f"{BASE_URL}/user", json=user_data)
    time.sleep(1)
    soft_assert(response.status_code in (200, 201),
                "Создание пользователя прошло успешно: получен код 200 или 201.",
                f"Ошибка при создании пользователя: ожидался код 200 или 201, получен {response.status_code}.",
                response)

    # Получение созданного пользователя
    log_msg("Тест пользователей: Получение информации о пользователе. Отправка GET запроса по /user/{username}.", "33")
    response = requests.get(f"{BASE_URL}/user/{username}")
    time.sleep(1)
    soft_assert(response.status_code == 200,
                "Получение информации о пользователе прошло успешно: получен код 200.",
                f"Ошибка при получении информации о пользователе: ожидался код 200, получен {response.status_code}.",
                response)
    if response.status_code == 200:
        user_returned = response.json()
        soft_assert(user_returned.get("username") == user_data["username"],
                    "Данные пользователя корректны: username совпадает с созданным.",
                    f"Несоответствие username: ожидалось {user_data['username']}, получено {user_returned.get('username')}.",
                    response)
    # Обновление данных пользователя
    log_msg("Тест пользователей: Обновление пользователя. Отправка PUT запроса по /user/{username} с изменёнными данными.", "33")
    user_data["firstName"] = "Jane"
    user_data["lastName"] = "Smith"
    response = requests.put(f"{BASE_URL}/user/{username}", json=user_data)
    time.sleep(1)
    soft_assert(response.status_code in (200, 201),
                "Обновление пользователя прошло успешно: получен код 200 или 201.",
                f"Ошибка при обновлении пользователя: ожидался код 200 или 201, получен {response.status_code}.",
                response)
    # Проверка обновления данных пользователя
    response = requests.get(f"{BASE_URL}/user/{username}")
    time.sleep(1)
    soft_assert(response.status_code == 200,
                "Получение информации о пользователе после обновления прошло успешно: получен код 200.",
                f"Ошибка при получении информации о пользователе после обновления: ожидался код 200, получен {response.status_code}.",
                response)
    if response.status_code == 200:
        user_updated = response.json()
        soft_assert(user_updated.get("firstName") == user_data["firstName"],
                    "Обновление пользователя: firstName успешно обновлён.",
                    f"Ошибка: firstName не обновлён. Ожидалось {user_data['firstName']}, получено {user_updated.get('firstName')}.",
                    response)
        soft_assert(user_updated.get("lastName") == user_data["lastName"],
                    "Обновление пользователя: lastName успешно обновлён.",
                    f"Ошибка: lastName не обновлён. Ожидалось {user_data['lastName']}, получено {user_updated.get('lastName')}.",
                    response)
    # Удаление пользователя
    log_msg("Тест пользователей: Удаление пользователя. Отправка DELETE запроса по /user/{username}.", "33")
    response = requests.delete(f"{BASE_URL}/user/{username}")
    time.sleep(1)
    soft_assert(response.status_code == 200,
                "Удаление пользователя прошло успешно: получен код 200.",
                f"Ошибка при удалении пользователя: ожидался код 200, получен {response.status_code}.",
                response)
    # Проверка удаления пользователя: GET запрос должен вернуть 404
    response = requests.get(f"{BASE_URL}/user/{username}")
    time.sleep(1)
    soft_assert(response.status_code == 404,
                "Пользователь успешно удалён: при GET запросе получен код 404.",
                f"Ошибка: пользователь не удалён. Ожидался код 404, получен {response.status_code}.",
                response)

def test_negative():
    """
    Негативные тесты:
      - Попытка получить/удалить несуществующий объект (питомца, заказ, пользователя).
      - Отправка некорректных данных.
    """
    # Негативные тесты для питомца
    log_msg("Негативный тест: Получение несуществующего питомца.", "33")
    non_existent_pet_id = 999999999  # Предполагаем, что такого питомца нет
    response = requests.get(f"{BASE_URL}/pet/{non_existent_pet_id}")
    time.sleep(1)
    soft_assert(response.status_code == 404,
                "Негативный тест для питомца: Получение несуществующего питомца вернуло код 404.",
                f"Ошибка: ожидался код 404 при получении несуществующего питомца, получен {response.status_code}.",
                response)

    log_msg("Негативный тест: Удаление несуществующего питомца.", "33")
    response = requests.delete(f"{BASE_URL}/pet/{non_existent_pet_id}")
    time.sleep(1)
    soft_assert(response.status_code == 404,
                "Негативный тест для питомца: Удаление несуществующего питомца вернуло код 404.",
                f"Ошибка: ожидался код 404 при удалении несуществующего питомца, получен {response.status_code}.",
                response)

    # Негативные тесты для заказа
    log_msg("Негативный тест: Получение несуществующего заказа.", "33")
    non_existent_order_id = 999999999
    response = requests.get(f"{BASE_URL}/store/order/{non_existent_order_id}")
    time.sleep(1)
    soft_assert(response.status_code == 404,
                "Негативный тест для заказа: Получение несуществующего заказа вернуло код 404.",
                f"Ошибка: ожидался код 404 при получении несуществующего заказа, получен {response.status_code}.",
                response)

    log_msg("Негативный тест: Удаление несуществующего заказа.", "33")
    response = requests.delete(f"{BASE_URL}/store/order/{non_existent_order_id}")
    time.sleep(1)
    soft_assert(response.status_code == 404,
                "Негативный тест для заказа: Удаление несуществующего заказа вернуло код 404.",
                f"Ошибка: ожидался код 404 при удалении несуществующего заказа, получен {response.status_code}.",
                response)

    # Негативные тесты для пользователя
    log_msg("Негативный тест: Получение несуществующего пользователя.", "33")
    fake_username = "nonexistent_user_12345"
    response = requests.get(f"{BASE_URL}/user/{fake_username}")
    time.sleep(1)
    soft_assert(response.status_code == 404,
                "Негативный тест для пользователя: Получение несуществующего пользователя вернуло код 404.",
                f"Ошибка: ожидался код 404 при получении несуществующего пользователя, получен {response.status_code}.",
                response)

    log_msg("Негативный тест: Удаление несуществующего пользователя.", "33")
    response = requests.delete(f"{BASE_URL}/user/{fake_username}")
    time.sleep(1)
    soft_assert(response.status_code == 404,
                "Негативный тест для пользователя: Удаление несуществующего пользователя вернуло код 404.",
                f"Ошибка: ожидался код 404 при удалении несуществующего пользователя, получен {response.status_code}.",
                response)

    # Негативный тест: отправка некорректных данных для создания питомца
    log_msg("Негативный тест: Отправка некорректных данных для создания питомца.", "33")
    invalid_pet_data = {
        "id": "invalid_id"  # Ожидается целое число; также отсутствуют обязательные поля
    }
    response = requests.post(f"{BASE_URL}/pet", json=invalid_pet_data)
    time.sleep(1)
    soft_assert(response.status_code in (400, 405, 500),
                "Негативный тест для питомца: Некорректные данные вернули ожидаемую ошибку.",
                f"Ошибка: ожидался код ошибки при отправке некорректных данных для питомца, получен {response.status_code}.",
                response)

    # Негативный тест: отправка некорректных данных для создания пользователя
    log_msg("Негативный тест: Отправка некорректных данных для создания пользователя.", "33")
    invalid_user_data = {
        "id": "invalid_id"  # Ожидается целое число; отсутствуют другие обязательные поля
    }
    response = requests.post(f"{BASE_URL}/user", json=invalid_user_data)
    time.sleep(1)
    soft_assert(response.status_code in (400, 405, 500),
                "Негативный тест для пользователя: Некорректные данные вернули ожидаемую ошибку.",
                f"Ошибка: ожидался код ошибки при отправке некорректных данных для пользователя, получен {response.status_code}.",
                response)

def main():
    """
    Основная функция запуска тестов.
    По завершении выводится итоговая информация: успешное прохождение всех тестов или сообщение об ошибках.
    Если найдены ошибки – завершаем выполнение с ненулевым кодом возврата.
    """
    log_msg("Запуск E2E тестов для API Petstore", "33")
    test_pet()
    test_order()
    test_user()
    test_negative()
    if test_failures:
        log_msg(f"Тестирование завершено с ошибками. Количество ошибок: {len(test_failures)}. Детали: {test_failures}", "31")
        sys.exit(1)
    else:
        log_msg("Все тесты успешно пройдены.", "32")
        sys.exit(0)

if __name__ == "__main__":
    main()
