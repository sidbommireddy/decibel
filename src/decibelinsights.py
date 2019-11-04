from flask import Flask, jsonify, request, json
import ast
import pandas as pd
from itertools import count
import numpy as np
from scipy.spatial.distance import mahalanobis
from werkzeug.exceptions import HTTPException

app = Flask(__name__)


def nd_rolling(data, window_size):
    """
    Generate the moving window

    data: pandas.core.frame.DataFrame
    window_size: float

    yield: tuple
    """

    # calculate the moving window for each idx-th point
    sample = list(zip(count(), data.values[:, 0], data.values[:, 1]))
    for idx in range(0, len(sample)):
        idx0 = idx if idx - window_size < 0 else idx - window_size
        window = [it for it in sample
                  if it[0] >= idx0 or it[1] <= idx0 + window_size]
        x = np.array([it[1] for it in window])
        y = np.array([it[2] for it in window])

        yield {'idx': idx,
               'value': np.array(tuple(sample[idx][1:])),
               'window_avg': np.array((np.mean(x), np.mean(y))),
               'window_cov': np.cov(x, y, rowvar=0)}


def get_anomalous_values(data, window_size, prob=0.99):
    """
    return a list of anomalous values, i.e. the ones that exceed md times
    in terms of Mohalanobis distance the expected multivariate average. Both
    multivariate average and Mahalanobis distance are calculated considering
    the moving windows, i.e. the value computed considering window_size
    neighbours, moving the window for each value of the serie.

    data : pandas.core.frame.DataFrame
    window_size: int
    md: float

    return: list
    """

    # under normal hypotesis, the Mohalanobis dinstance is Chi-squared
    # distribuited
    threshold = np.sqrt(-2 * np.log(1 - prob))

    # calculate the moving window for each point, and report the anomaly if
    # the distance of the idx-th point is greater than md times the mahalanobis
    # distance
    return [(p['idx'], p['value']) for p in nd_rolling(data, window_size)
            if mahalanobis(p['value'], p['window_avg'],
                           np.linalg.inv(p['window_cov'])) > threshold]


@app.route('/')
def decibelhome():
    user_agent = request.headers.get('User-Agent')
    user_host = request.headers.get('Host')
    print("Host is " + user_host)
    print("Accept-encoding :" + request.headers.get('Accept-Encoding'))
    return '<p>Your browser is %s and Host is </p>' % user_agent


@app.route('/get_anomalous_data', methods=['POST'])
def getanamalouspage():

        inputbytes = request.data
        # Convert bytes to string
        str1 = inputbytes.decode("utf-8")
        # Convert String to a list
        lista = str1.split(" ")
        print(len(lista))
        if len(lista) < 50:
            message = {
                'status': 202,
                'message': 'Insufficient Data: ' + request.url,
            }
            resp = jsonify(message)
            resp.status_code = 202

            return resp

        listforpandas = [ast.literal_eval(x) for x in lista]
        data1 = pd.DataFrame(listforpandas)

        temp_result = get_anomalous_values(data1, 50)
        # Convert into a list of dictionaries
        result = [{x: y.tolist()} for x, y in temp_result]
        if not result:
            return json.dumps(result), 204

        return json.dumps(result)


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


@app.errorhandler(500)
def internal_error(error=None):
    message = {
        'status': 500,
        'message': 'Sorry for the inconvenience. Internal server error: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 500

    return resp


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
