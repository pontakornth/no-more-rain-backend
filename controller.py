import os
import sys
sys.path.append('stub')
from swagger_server.models import *
import dotenv

dotenv.load_dotenv()
TMD_API_KEY = os.environ.get('TMD_API_KEY')
AQI_CN_API_KEY = os.environ.get('AQI_CN_API_KEY')
TAT_API_KEY = os.environ.get('TAT_API_KEY')

def search(keywords, geolocation, search_radius=None, number_of_result=None, page=None):
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
    return

def get_attraction_detail(attraction_id: str):
    """

    :rtype: AttractionDetailResult
    """
    return