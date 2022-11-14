import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import time
import dill


app = FastAPI()
# документация доступна после запуска по адресу: http://127.0.0.1:8000/docs

class Form(BaseModel):
    # напишем поля вводных данных и типы данных для их валидации:
    session_id: object
    client_id: object
    visit_date: object
    visit_time: object
    visit_number: int
    utm_source: object
    utm_medium: object
    utm_campaign: object
    utm_adcontent: object
    utm_keyword: object
    device_category: object
    device_os: object
    device_brand: object
    device_model: object
    device_screen_resolution: object
    device_browser: object
    geo_country: object
    geo_city: object


class Prediction(BaseModel):
    Session_id: str
    Conversion_prediction: int
    Predict_proba:  list
    Threashold_used: float
    Response_time_sec: float


with open('sessions_pipe.pkl', 'rb') as file:
    model = dill.load(file)


def combine_small_categories(df: pd.DataFrame) -> pd.DataFrame:
    # функция для объединения мелких категорий в трех столбцах датафрейма
    # есть списки основных категорий - сверяем с ними значения, все неподходящее относим к rare.

    with open('Reduced_categories_lists.pickle', 'rb') as file:
        reduced_categ_dict = dill.load(file)

    col_list = ['utm_keyword', 'utm_campaign', 'utm_source']

    for col in col_list:
        df.loc[df[col].isin(list(reduced_categ_dict[col])) == False, col] = 'rare'

    return df

def time_date_features(df):
    df['month'] = np.nan
    df['month'][0] = df['visit_date'][0].month

    df['day'] = np.nan
    df['day'][0] = df['visit_date'][0].day

    df['day_of_week'] = np.nan
    df['day_of_week'][0] = df['visit_date'][0].dayofweek

    df['hour'] = np.nan
    df['hour'][0] = df['visit_time'][0].hour

    return df

def geo_features(df):
    #добавление 4 параметров с координатами города и страны:

    filename = '!geo_country_location_dict.pickle'
    with open(filename, 'rb') as file:
        dict_geo_country = dill.load(file)

    filename = '!geo_city_location_dict.pickle'
    with open(filename, 'rb') as file:
        dict_geo_city = dill.load(file)

    df['lat'] = np.nan
    if (dict_geo_city[df['geo_city'][0]] is not None) & (df['geo_city'][0] != '(not set)'):
        df['lat'][0] = dict_geo_city[df['geo_city'][0]][1][0]
    else:
        df['lat'][0] = dict_geo_country[df['geo_country'][0]][1][0]

    df['long'] = np.nan
    if (dict_geo_city[df['geo_city'][0]] is not None) & (df['geo_city'][0] != '(not set)'):
        df['long'][0] = dict_geo_city[df['geo_city'][0]][1][1]
    else:
        df['long'][0] = dict_geo_country[df['geo_country'][0]][1][1]

    df['country_lat'] = np.nan
    df['country_lat'][0] = dict_geo_country[df['geo_country'][0]][1][0]

    df['country_long'] = np.nan
    df['country_long'][0] = dict_geo_country[df['geo_country'][0]][1][1]

    return df

@app.get('/')
def root():
    return {'message': ' Hi!'}

@app.get('/status')
def status():
    return 'I\'m OK'


@app.get('/version')
def version():
    return model['metadata']


@app.get('/feature_importances')
def feature_imp():
    return model['model'][-1].get_feature_importance(prettified=True)


@app.post('/predict', response_model=Prediction)
def predict(form: Form):
    df = pd.DataFrame.from_dict([form.dict()])
    threashold = model['threashold']

    start = time.time()
    # пара преобразований, которые требуют дозагрузки данных из других файлов:
    df = combine_small_categories(df)
    df = geo_features(df)
    df['visit_date'] = pd.to_datetime(df.visit_date)
    df['visit_time'] = pd.to_datetime(df.visit_time)
    df = time_date_features(df)

    y = model['model'].predict_proba(df)
    end = time.time()


    return {
        'Session_id': form.session_id,
        'Conversion_prediction': (y.tolist()[0][1]>threashold)*1,
        'Predict_proba': y.tolist()[0],
        'Threashold_used': threashold,
        'Response_time_sec': (end-start)
    }



