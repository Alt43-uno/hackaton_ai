# Импортируем необходимые библиотеки
import cv2
import face_recognition
import sqlite3

# Создаем объект для работы с камерой
cap = cv2.VideoCapture(0)

# Создаем объект для работы с базой данных
conn = sqlite3.connect('faces.db')
cur = conn.cursor()

# Создаем таблицу для хранения путей к файлам и имен пользователей
cur.execute('CREATE TABLE IF NOT EXISTS faces (face TEXT, name TEXT)')

# Загружаем пути к файлам и имена пользователей из базы данных в память
faces = []
names = []
for row in cur.execute('SELECT face, name FROM faces'):
    face = row[0] # Присваиваем путь к файлу переменной face
    name = row[1]
    # Загружаем изображение с помощью cv2.imread или face_recognition.load_image_file
    face = cv2.imread(face) # или face = face_recognition.load_image_file(face)
    # Преобразуем изображение в формат RGB для работы с библиотекой face_recognition
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    # Извлекаем кодировку лица с помощью face_recognition.face_encodings
    face = face_recognition.face_encodings(face)
    # Проверяем, что список не пустой
    if face:
        # Берем первый элемент списка
        face = face[0]
        faces.append(face)
        names.append(name)

# Закрываем соединение с базой данных
conn.close()

# Основной цикл программы
while True:
    # Считываем кадр с камеры
    ret, frame = cap.read()
    if not ret:
        break

    # Преобразуем кадр в формат RGB для работы с библиотекой face_recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Обнаруживаем лица на кадре
    face_locations = face_recognition.face_locations(rgb_frame)

    # Для каждого лица на кадре
    for face_location in face_locations:
        # Получаем координаты лица
        top, right, bottom, left = face_location

        # Вырезаем лицо из кадра
        face = rgb_frame[top:bottom, left:right]

        # Извлекаем кодировку лица с помощью face_recognition.face_encodings
        face = face_recognition.face_encodings(face)
        # Проверяем, что список не пустой
        if face:
            # Берем первый элемент списка
            face = face[0]

            # Сравниваем лицо с лицами из базы данных
            matches = face_recognition.compare_faces(faces, face)

            # Если есть совпадение, то получаем имя пользователя
            if True in matches:
                match_index = matches.index(True)
                name = names[match_index]
            else:
                name = 'Unknown'
        else:
            name = 'Unknown'
        # Рисуем прямоугольник вокруг лица
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Выводим имя пользователя под лицом
        cv2.putText(frame, name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Показываем кадр с распознанными лицами на экране
    cv2.imshow('Face Recognition', frame)

    # Ждем нажатия клавиши Esc для выхода из программы
    if cv2.waitKey(1) == 27:
        break

# Освобождаем ресурсы камеры и закрываем окно
cap.release()
cv2.destroyAllWindows()
