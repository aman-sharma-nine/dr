#!/usr/bin/env python
# coding: utf-8


import requests
import os
import datarobot as dr
import numpy as np
import datetime
import sys
import time
import yaml
import warnings
import json
import pandas as pd
import nbconvert
warnings.filterwarnings("ignore")

class DataRobotPredictionError(Exception):
    pass

# Credentials
API_KEY = ''
USERNAME =''

#deployment
deployment_id = ''

def make_datarobot_deployment_predictions(data, deployment_id):
    """
    Make predictions on data provided using DataRobot deployment_id provided.
    See docs for details:
         https://app.datarobot.com/docs/users-guide/predictions/api/new-prediction-api.html

    Parameters
    ----------
    data : str
        Feature1,Feature2
        numeric_value,string
    deployment_id : str
        The ID of the deployment to make predictions with.

    Returns
    -------
    Response schema:
        https://app.datarobot.com/docs/users-guide/predictions/api/new-prediction-api.html#response-schema

    Raises
    ------
    DataRobotPredictionError if there are issues getting predictions from DataRobot
    """
    # Set HTTP headers. The charset should match the contents of the file.
    # You will need to put your datarobot-key (for cloud accounts)
    headers = {'Content-Type': 'text/plain; charset=UTF-8', 'datarobot-key': ''}

    url = 'https://cfds-ccm-prod.orm.datarobot.com/predApi/v1.0/deployments/{deployment_id}/'          'predictions'.format(deployment_id=deployment_id)
    # Make API request for predictions
    predictions_response = requests.post(
        url, auth=(USERNAME, API_KEY), data=data, headers=headers)
    _raise_dataroboterror_for_status(predictions_response)
    # Return a Python dict following the schema in the documentation
    return predictions_response.json()


def _raise_dataroboterror_for_status(response):
    """Raise DataRobotPredictionError if the request fails along with the response returned"""
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        err_msg = '{code} Error: {msg}'.format(
            code=response.status_code, msg=response.text)
        raise DataRobotPredictionError(err_msg)

def main(filename, deployment_id):
    """
    Return an exit code on script completion or error. Codes > 0 are errors to the shell.
    Also useful as a usage demonstration of
    `make_datarobot_deployment_predictions(data, deployment_id)`
    """
    if not filename:
        print(
            'Input file is required argument. '
            'Usage: python datarobot-predict.py <input-file.csv>')
        return 1
    data = open(filename, 'rb').read()
    data_size = sys.getsizeof(data)
    if data_size >= MAX_PREDICTION_FILE_SIZE_BYTES:
        print(
            'Input file is too large: {} bytes. '
            'Max allowed size is: {} bytes.'
        ).format(data_size, MAX_PREDICTION_FILE_SIZE_BYTES)
        return 1
    try:
        predictions = make_datarobot_deployment_predictions(data, deployment_id)
    except DataRobotPredictionError as exc:
        print(exc)
        return 1
    print(predictions)
    return 0

# Make predictions on scoring data against deployment id one replacement model
#prediction dataset
data = open('../../../demo/lendingclub/lendingclubGR/driftdata.csv','rb').read()


predictions = pd.DataFrame.from_dict(make_datarobot_deployment_predictions(data, deployment_id))

#Feedback actuals

def feedback_actuals(data, deployment_id):
 	headers = {
 		'Content-Type': 'application/json',
 		'Authorization':  'Token {}'.format(API_KEY)}
 	url = 'https://app.datarobot.com/api/v2/deployments/{deployment_id}/actuals/fromJSON/'.format(
 		deployment_id=deployment_id)
 	resp = requests.post(url, data=data, headers=headers)
 	return resp

def set_association_id(deployment_id, association_id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization':  'Token {}'.format(API_KEY)
    }
    url = 'https://app.datarobot.com/api/v2/modelDeployments/{deployment_id}/associationIdSettings/'.format(deployment_id=deployment_id)
    data = {'allowMissingValues': False, 'columnName': association_id}
    data = json.dumps(data)
    resp = requests.patch(url, data=data, headers=headers)
    resp.raise_for_status()
    return resp

actuals = pd.read_csv('') # actual.csv
actuals['associationId'] = actuals['member_id']
actuals['actualValue'] = actuals['actuals']

#put the df in json format
data = json.dumps({
    'data':
    actuals[['associationId', 'actualValue']].to_dict('records')
})

actual_response = feedback_actuals(data, deployment_id)
