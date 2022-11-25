import os
import sys
import time

from swagger_server import models
import dotenv
import requests
from flask import abort
from datetime import datetime

sys.path.append('stub')
dotenv.load_dotenv()
TMD_API_KEY = os.environ.get('TMD_API_KEY')
AQI_CN_API_KEY = os.environ.get('AQI_CN_API_KEY')
TAT_API_KEY = os.environ.get('TAT_API_KEY')


def search(keywords, geolocation, provincename, destination, search_radius=20, number_of_result=50, page=1):
    """

    :param keywords:
    :type keywords: str
    :param geolocation:
    :type geolocation: str
    :param provincename:
    :type provincename:str
    :param destination:
    :type destination:str
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
        f'{geo_data[1]}&categorycodes=ATTRACTION&provinceName={provincename}&radius={search_radius}&numberOfResult='
        f'{int(number_of_result)}&pagenumber={int(page)}&destination={destination}', headers=headers)

    if response.status_code == 404:
        abort(404)

    json_result = response.json()
    result = [
        models.AttractionSearchResult(result['place_id'], result['latitude'], result['longitude'],
                                      result['destination'], result['place_name'], result['thumbnail_url'],
                                      result['location'])
        for result in json_result['result']
    ]
    return result


def get_attraction_detail(attraction_id: str):
    """

    :rtype: AttractionDetailResult
    """
    # TAT API request
    tat_headers = {
        "Authorization": f"Bearer {TAT_API_KEY}",
        "Accept-Language": "EN"
    }
    tat_response = requests.get(f'https://tatapi.tourismthailand.org/tatapi/v5/attraction/{attraction_id}',
                                headers=tat_headers)
    # No data for that attraction
    if tat_response.status_code == 404:
        abort(404)
    tat_response_json = tat_response.json()
    place_id = tat_response_json['result']['place_id']
    lat = tat_response_json['result']['latitude']
    lon = tat_response_json['result']['longitude']
    destination = tat_response_json['result']['destination']
    place_name = tat_response_json['result']['place_name']
    thumbnail_url = tat_response_json['result']['thumbnail_url']
    location = tat_response_json['result']['location']
    contact = tat_response_json['result']['contact']

    # TMD API request
    tmd_headers = {
        'accept': 'application/json',
        'authorization': f"Bearer {TMD_API_KEY}"
    }
    tmd_response = requests.get(
        f'https://data.tmd.go.th/nwpapi/v1/forecast/location/daily/at?lat={lat}&lon={lon}&fields=tc_max,'
        f'tc_min&duration=7', headers=tmd_headers)
    if tmd_response.status_code == 404:
        abort(404)
    tmd_response_json = tmd_response.json()
    tc_max_data = []
    tc_min_data = []
    for forecast_weather_data in tmd_response_json['WeatherForecasts'][0]['forecasts']:
        tc_max_data.append(forecast_weather_data['data']['tc_max'])
        tc_min_data.append(forecast_weather_data['data']['tc_min'])

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    current_date = time.strptime(date, "%Y-%m-%d")

    # AQICN API request
    aqicn_response = requests.get(f'https://api.waqi.info/feed/geo:{lat};{lon}/?token={AQI_CN_API_KEY}')
    if aqicn_response.status_code == 404:
        abort(404)
    aqicn_response_json = aqicn_response.json()

    pm25_data = []
    for data in aqicn_response_json['data']['forecast']['daily']['pm25']:
        date_of_data = time.strptime(data['day'], "%Y-%m-%d")
        if current_date <= date_of_data:
            pm25_data.append([data['day'], data['avg']])

    pm10_data = []
    for data in aqicn_response_json['data']['forecast']['daily']['pm10']:
        date_of_data = time.strptime(data['day'], "%Y-%m-%d")
        if current_date <= date_of_data:
            pm10_data.append([data['day'], data['avg']])

    forecasts_result = [
        models.WeatherDetail(pm10_data[index][0], tc_max_data[index], tc_min_data[index], pm25_data[index][1],
                             pm10_data[index][1])
        for index in range(7)
    ]
    detail_result = models.AttractionDetailResult(place_id, place_name, lat, lon, destination, thumbnail_url, location, contact,
                                                  forecasts_result)
    return detail_result
