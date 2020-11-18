from googlemaps import Client as GoogleMaps
import time
from ratelimit import limits, sleep_and_retry
from fastprogress.fastprogress import progress_bar


@sleep_and_retry
@limits(calls=2800, period=60)
def get_lat_long(location, gmaps):
    try:
        geocode_result = gmaps.geocode(location)
        lat = geocode_result[0]['geometry']['location']['lat']
        long = geocode_result[0]['geometry']['location']['lng']
        return long, lat
    except Exception as e:
        print(e)
        return None,None

def add_coordinate_info(df, api_key):
    gmaps = GoogleMaps(api_key)
    df['long'] = ""
    df['lat'] = ""  
    long = []
    lat = []
    for location in progress_bar(df.location):
        long_, lat_ = get_lat_long(location, gmaps)
        long.append(long_)
        lat.append(lat_)
    df.long=long
    df.lat=lat
    return df.reset_index(drop=True)




    



