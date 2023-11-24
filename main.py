# импортируем необходимые библиотеки
import requests
import cv2
import face_recognition
from flask import Flask, request, jsonify

# создаем экземпляр приложения Flask
app = Flask(__name__)

# создаем глобальную переменную для хранения списка пользователей
users = []

# определяем функцию для загрузки пользователей из API JSON
def load_users():
    # делаем GET-запрос к API для получения JSON с данными пользователей
    response = requests.get("http://192.168.88.171:1337/api/bank-users?populate=image")
    # проверяем, что запрос успешный
    if response.status_code == 200:
        # преобразуем JSON в словарь Python
        data = response.json()
        # получаем список пользователей из словаря
        users = data["data"]
        # возвращаем список пользователей
        return users
    # если запрос неуспешный, возвращаем пустой список
    return []

# вызываем функцию для загрузки пользователей из API JSON и сохраняем результат в глобальную переменную
users = load_users()

# определяем функцию для проверки пользователя по фото
def check_user_by_photo(photo_url):
    # загружаем фото пользователя из URL
    user_photo = face_recognition.load_image_file(requests.get(photo_url, stream=True).raw)
    # извлекаем лицо пользователя из фото
    user_face = face_recognition.face_encodings(user_photo)[0]
    # перебираем всех пользователей в цикле
    for user in users:
        # получаем ID, имя и URL фото из каждого пользователя
        user_id = user["id"]
        user_name = user["attributes"]["full_name"]
        user_photo_url = user["attributes"]["image"]["data"][0]["attributes"]["url"]
        # добавляем базовый URL к относительному URL фото
        user_photo_url = "http://192.168.88.171:1337" + user_photo_url
        # загружаем фото из JSON из URL
        db_photo = face_recognition.load_image_file(requests.get(user_photo_url, stream=True).raw)
        # извлекаем лицо из фото
        db_face = face_recognition.face_encodings(db_photo)[0]
        # сравниваем лицо пользователя с лицом из JSON
        match = face_recognition.compare_faces([user_face], db_face)[0]
        # если лица совпадают, возвращаем ID и имя пользователя
        if match:
            return user_id, user_name
    # если ни одно лицо не совпало, возвращаем None
    return None

# определяем маршрут для API-запроса
@app.route("/api/check_user", methods=["GET"])
def api_check_user():
    # получаем параметр photo_url из запроса
    photo_url = request.args.get("photo_url")
    # проверяем, что параметр не пустой
    if photo_url:
        # вызываем функцию для проверки пользователя по фото
        result = check_user_by_photo(photo_url)
        # если результат не None, возвращаем JSON-ответ с ID и именем пользователя
        if result:
            user_id, user_name = result
            return jsonify({"user_id": user_id, "user_name": user_name})
        # иначе возвращаем JSON-ответ с сообщением об ошибке
        else:
            return jsonify({"error": "User not found"})
    # если параметр пустой, возвращаем JSON-ответ с сообщением об ошибке
    else:
        return jsonify({"error": "Missing photo_url parameter"})

# запускаем сервер Flask на локальном хосте и порту 5000
if __name__ == "__main__":
    app.run(host="localhost", port=5000)
