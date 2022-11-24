import os
import sys
from swagger_server import models
import dotenv
import requests
from flask import abort

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

    if response.status_code == 404:
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
    headers = {
        "Authorization": f"Bearer {TAT_API_KEY}",
        "Accept-Language": "EN"
    }
    tat_response = requests.get(f'https://tatapi.tourismthailand.org/tatapi/v5/attraction/{attraction_id}',
                            headers=headers)
    # No data for that attraction
    if tat_response.status_code == 404:
        abort(404)

    tat_response_json = tat_response.json()
    place_id = tat_response_json['result']['place_id']
    lat = tat_response_json['result']['latitude']
    lon = tat_response_json['result']['longitude']
    destination = tat_response_json['result']['destination']
    thumbnail_url = tat_response_json['result']['thumbnail_url']
    location = tat_response_json['result']['location']
    contact = tat_response_json['result']['contact']

    tmd_response = ...

    aqicn_response = ...


    # result = [place_id, lat, lon, destination, thumbnail_url, location, contact]
    # return result
