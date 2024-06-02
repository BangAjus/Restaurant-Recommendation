from sanic import Sanic
from sanic.response import json, text
from sanic.request import Request
import pandas as pd
import numpy as np

app = Sanic("ml_api")

@app.route("/")
async def home(request : Request):
    return text("Hello, Welcome!")

@app.route("/recommendation1", methods=["GET"])
async def recommendation1(request : Request):

    rest_data = request.json
    data1 = pd.read_csv('data/data1.csv')
    items = pd.read_csv('data/data.csv')

    index = data1.loc[:,rest_data['name']]\
                           .to_numpy()\
                           .argpartition(range(-1, -rest_data['n_data'], -1))
    closest = data1.columns[index[-1:-(rest_data['n_data']+2):-1]]
    closest = np.unique(closest[closest != rest_data['name']])

    result = pd.DataFrame({'name':closest}).merge(items, on='name')\
                                           .drop_duplicates()\
                                           .head(rest_data['n_data'])\
                                           [['name', 'rest_type']]\
                                           .to_dict('list')
    return json(result, 200)

@app.route("/recommendation2", methods=["GET"])
async def recommendation2(request : Request):

    rest_data = request.json
    data2 = pd.read_csv('data/data2.csv')
    items = pd.read_csv('data/data.csv')

    index = data2.loc[:,rest_data['name']]\
                           .to_numpy()\
                           .argpartition(range(-1, -rest_data['n_data'], -1))
    closest = data2.columns[index[-1:-(rest_data['n_data']+2):-1]]
    closest = np.unique(closest[closest != rest_data['name']])

    result = pd.DataFrame({'name':closest}).merge(items, on='name')\
                                           .drop_duplicates()\
                                           .head(rest_data['n_data'])\
                                           [['name', 'cuisines']]\
                                           .to_dict('list')
    return json(result, 200)