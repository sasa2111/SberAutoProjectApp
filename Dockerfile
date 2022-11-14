FROM python:3

WORKDIR /usr/src/app

COPY ./App/requirements.txt requirements.txt

COPY ./App/sessions_pipe.pkl sessions_pipe.pkl

COPY ./App/main.py main.py

COPY ./App/!geo_city_location_dict.pickle !geo_city_location_dict.pickle

COPY ./App/!geo_country_location_dict.pickle !geo_country_location_dict.pickle
COPY ./App/Reduced_categories_lists.pickle Reduced_categories_lists.pickle

RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт 8000 чтобы он был доступен снаружи контейнера
EXPOSE 8000


CMD uvicorn main:app --host 0.0.0.0 --port 8000 --reload

