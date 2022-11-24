import os
import sys
import time

from rest_framework import status

from swagger_server import models
import dotenv
import requests
from flask import abort
from datetime import datetime, timedelta

sys.path.append('stub')
dotenv.load_dotenv()
TMD_API_KEY = os.environ.get('TMD_API_KEY')
AQI_CN_API_KEY = os.environ.get('AQI_CN_API_KEY')
TAT_API_KEY = os.environ.get('TAT_API_KEY')


def search(keywords, geolocation, search_radius=20, number_of_result=50, page=1):
    """

    :param keywords:
    :type keywords: str
    :param geolocation:
    :type geolocation: str
    :param search_radius:
    :type search_radius: float
    :param number_of_result:
    :type number_of_result: float
    :param page:
    :type page: float

    :rtype: List[AttractionSearchResult]
    """
    geo_data = geolocation.split(",")
    headers = {
        "Authorization": f"Bearer {TAT_API_KEY}",
        "Accept-Language": "EN"
    }
    response = requests.get(
        f'https://tatapi.tourismthailand.org/tatapi/v5/places/search?keyword={keywords}&location={geo_data[0]},'
        f'{geo_data[1]}&categorycodes=ATTRACTION&radius={search_radius}&numberOfResult={int(number_of_result)}'
        f'&pagenumber={int(page)}', headers=headers)

    if response.status_code == status.HTTP_404_NOT_FOUND:
        abort(404)

    json_result = response.json()
    result = [
        models.AttractionSearchResult(i['place_id'], i['latitude'], i['longitude'], i['destination'],
                                      i['thumbnail_url'], i['location'])
        for i in json_result['result']
    ]
    return result


def get_attraction_detail(attraction_id: str):
    """

    :rtype: AttractionDetailResult
    """
    tat_headers = {
        "Authorization": f"Bearer {TAT_API_KEY}",
        "Accept-Language": "EN"
    }
    tat_response = requests.get(f'https://tatapi.tourismthailand.org/tatapi/v5/attraction/{attraction_id}',
                                headers=tat_headers)
    # No data for that attraction
    if tat_response.status_code == status.HTTP_404_NOT_FOUND:
        abort(404)

    tat_response_json = tat_response.json()
    place_id = tat_response_json['result']['place_id']
    lat = tat_response_json['result']['latitude']
    lon = tat_response_json['result']['longitude']
    destination = tat_response_json['result']['destination']
    thumbnail_url = tat_response_json['result']['thumbnail_url']
    location = tat_response_json['result']['location']
    contact = tat_response_json['result']['contact']

    now = datetime.now()
    # forecast = datetime.now() + timedelta(days=6)
    date = now.strftime("%Y-%m-%d")
    # forecast_date = forecast.strftime("%Y-%m-%d")

    tmd_headers = {
        'accept': 'application/json',
        'authorization': f"Bearer {TMD_API_KEY}"
    }

    # TODO: Make request success -> currently error
    tmd_response = requests.get(
        f'https://data.tmd.go.th/nwpapi/v1/forecast/location/daily/at?lat={lat}&lon={lon}&duration=7',
        headers=tmd_headers)
    if tmd_response.status_code == status.HTTP_404_NOT_FOUND:
        abort(404)
    tmd_response_json = tmd_response.json()
    # TODO: get forecasts max temp, min temp after fix the above problem
    temp_max = ...
    temp_min = ...

    aqicn_response = requests.get(f'https://api.waqi.info/feed/geo:{lat};{lon}/?token={AQI_CN_API_KEY}')
    if aqicn_response.status_code == status.HTTP_404_NOT_FOUND:
        abort(404)
    aqicn_response_json = aqicn_response.json()
    current_date = time.strptime(date, "%Y-%m-%d")

    pm25_data = aqicn_response_json['data']['forecast']['daily']['pm25']
    for data in pm25_data:
        date_of_data = time.strptime(data['day'], "%Y-%m-%d")
        if current_date > date_of_data:
            pm25_data.remove(data)

    pm10_data = aqicn_response_json['data']['forecast']['daily']['pm10']
    for data in pm10_data:
        date_of_data = time.strptime(data['day'], "%Y-%m-%d")
        if current_date > date_of_data:
            pm10_data.remove(data)

    # TODO: loop through models
    result = models.AttractionDetailResult(place_id, lat, lon, destination, thumbnail_url, location, contact)
    return result
