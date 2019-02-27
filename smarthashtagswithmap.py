import math
from typing import List, Any

import requests
import json

lat_ = None
lon_ = None


class BoundingBox(object):
    def __init__(self, *args, **kwargs):
        self.lat_min = None
        self.lon_min = None
        self.lat_max = None
        self.lon_max = None


def location_to_lonlat(location):  # Get LON and LAT from Instagram Explorer
    global lat_
    global lon_
    url = 'https://www.instagram.com/explore/locations/'
    url += '{},{}'.format(location, "?__a=1")
    req = requests.get(url)
    data = json.loads(req.text)

    lat_ = data['graphql']['location']['lat']
    lon_ = data['graphql']['location']['lng']
    #print(lat_, lon_)


def get_bounding_box(latitude_in_degrees, longitude_in_degrees, half_side_in_miles):
    assert half_side_in_miles > 0
    assert latitude_in_degrees >= -90.0 and latitude_in_degrees <= 90.0
    assert longitude_in_degrees >= -180.0 and longitude_in_degrees <= 180.0

    half_side_in_km = half_side_in_miles * 1.609344
    lat = math.radians(latitude_in_degrees)
    lon = math.radians(longitude_in_degrees)

    radius = 6371
    # Radius of the parallel at given latitude
    parallel_radius = radius * math.cos(lat)

    lat_min = lat - half_side_in_km / radius
    lat_max = lat + half_side_in_km / radius
    lon_min = lon - half_side_in_km / parallel_radius
    lon_max = lon + half_side_in_km / parallel_radius
    rad2deg = math.degrees

    box = BoundingBox()
    box.lat_min = rad2deg(lat_min)
    box.lon_min = rad2deg(lon_min)
    box.lat_max = rad2deg(lat_max)
    box.lon_max = rad2deg(lon_max)

    return (box)


def set_smart_hashtags_map(location1,
                           location2,
                           location3,
                           location4,
                           zooming,
                           limit=3,
                           log_tags=True):
    """Generate smart hashtags based on https://displaypurposes.com/map"""

    url = ' https://query.displaypurposes.com/local/?bbox='
    url += '{},{},{},{}&zoom={}'.format(location1, location2, location3, location4, zooming)
    req = requests.get(url)
    data = json.loads(req.text)
    if int(data['count']) > 0:  # Get how many hashtags we got
        count = data['count']
        i = 0
        tags: List[Any] = []
        while i < count:
            tags.append(data['tags'][i]['tag'])  # Adding each hashtag to the list
            i += 1
        final_tags = (tags[:limit])  # Limit the number of #

        if log_tags is True:
            print(u'[smart hashtag generated: {}]'.format(final_tags))
        return final_tags
    else:
        print(u'Too few results for #{} tag'.format(data['count']))


location_to_lonlat("204517928/chicago-illinois")

locate = get_bounding_box(lat_, lon_, half_side_in_miles=25)

set_smart_hashtags_map(locate.lon_min, locate.lat_min, locate.lon_max, locate.lat_max,
                       zooming=11, limit=3, log_tags=True)


