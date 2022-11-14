Как развернуть приложение:

1. запустить Docker

2. скачать/скопировать на диск папку SberProjectApp, в которой:

    - папка App (с файлами приложения):
        requirements.txt - список пакетов для установки при создании образа docker
        sessions_pipe.pkl - пайплайн
        main.py - скрипт самого приложения (api)
        !geo_city_location_dict.pickle - вспомогательный файл для подкачивания гео-данных в приложении
        !geo_country_location_dict.pickle - вспомогательный файл для подкачивания гео-данных в приложении
        Reduced_categories_lists.pickle - вспомогательный файл для оптимизации категориальных признаков в приложении

    - Dockerfile
    - Readme - данная инструкция

3. в Git Bash перейти в папку SberProject

4. выполнить команду:
    docker build -t sberimage .
    (сгенерируется образ sberimage со всеми нужными библиотеками)

5. Запуск контейнера по созданному образу sberimage:

запуск контейнера с нормальным именем (predictapp) и указанием портов!:
    docker run -p 8000:8000 --name=predictapp sberimage

остановка контейнера
    docker stop predictapp

проверить, что контейнер запущен/скопировать id:
    docker ps

зайти внутрь контейнера (bash)
    docker exec -it <id_контейнера> bash

После запуска контейнера наше приложение становится доступно по адресу:
    localhost:8000 или http://127.0.0.1:8000

    1. localhost:8000 - приветственное сообщение
    2. localhost:8000/docs - документация и возможность сделать предикт, + проверить остальные запросы:
        2.1) GET: status, version, feature_importances
            - раскрываем нужный вид запроса GET и жмем Try it out -> Execute
            - получаем ответ и сопутствующую информацию
        2.2) POST: predict
            - раскрываем запрос и жмем Try it out
            - в Request body копируем содержимое json-файла с входными данными и конкретной сессии (можно в 1 строку),
            например (конверсионная сессия):

           {"session_id":"5699237400857151385.1622542232.1622542238",
		"client_id":"1326957112.1622542233",
		"visit_date":"2021-06-01","visit_time":"13:00:00",
		"visit_number":1,"utm_source":"bByPQxmDaMXgpHeypKSM",
		"utm_medium":"referral",
		"utm_campaign":"LTuZkdKfxRGVceoWkVyg",
		"utm_adcontent":"JNHcPlZPxEMWDnRiyoBf",
		"utm_keyword":null,
		"device_category":"desktop",
		"device_os":null,
		"device_brand":"",
		"device_model":null,"device_screen_resolution":"1920x1080",
		"device_browser":"Chrome","geo_country":"Russia","geo_city":"Moscow"}

            - жмем Execute
            - получаем Response body с деталями ответа:
                номер сессии,
                прогноз - 0/1,
                предикт-проба - [вероятность 0, вероятность 1],
                порог принятия решения - установленная константа,
                время ответа сервера в секундах.

    3. localhost:8000/status - статус
    4. localhost:8000/version - информация о приложении
