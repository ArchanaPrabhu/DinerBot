#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pyzomato import Pyzomato
import os

p = Pyzomato('d67aae36be44be5d4483e0546ff03360')
cuisine_list = []
latitude = 40
longitude = -73


def get_cuisines(location=None):
    global latitude, longitude
    latitude = location['latitude']
    longitude = location['longitude']
    geocode = p.getByGeocode(latitude, longitude)
    city_id = geocode['location']['city_id']
    nearby_cuisines = geocode['popularity']['top_cuisines']
    cuisines_dict = p.getCuisines(city_id)
    global cuisine_list
    for i in range(len(cuisines_dict['cuisines'])):
        cuisine_list.append(cuisines_dict['cuisines'][i]['cuisine'])
    return nearby_cuisines


def get_values(result, lat, long, title, address):
    l = result['results_shown']
    for i in range(0, l):
        if result['restaurants'][i]['restaurant']['name'] not in title and len(lat) < 5:
            lat.append(result['restaurants'][i]['restaurant']['location']['latitude'])
            long.append(result['restaurants'][i]['restaurant']['location']['longitude'])
            address.append(result['restaurants'][i]['restaurant']['location']['address'])
            title.append(result['restaurants'][i]['restaurant']['name'])


def get_values_price(result, lat, long, title, address, price):
    l = result['results_shown']
    for i in range(0, l):
        if result['restaurants'][i]['restaurant']['price_range'] == price and len(lat) < 5 and \
                        result['restaurants'][i]['restaurant']['name'] not in title:
            lat.append(result['restaurants'][i]['restaurant']['location']['latitude'])
            long.append(result['restaurants'][i]['restaurant']['location']['longitude'])
            address.append(result['restaurants'][i]['restaurant']['location']['address'])
            title.append(result['restaurants'][i]['restaurant']['name'])


def search_by_cuisine(cuisine):
    cuisine = cuisine.title()
   # print(cuisine)
    cuisine_loc = (next((item for item in cuisine_list if item['cuisine_name'] == cuisine), False))
    if not cuisine_loc:
        return None, None, None, None
    cuisine_id = cuisine_loc['cuisine_id']
    result = p.search(lat=latitude, lon=longitude, radius='15000', sort='real_distance', order='asc',
                      cuisines=cuisine_id, count='1')
    #print(result)
    lat = []
    long = []
    address = []
    title = []
    get_values(result, lat, long, title, address)
    print(lat)
    print(long)
    print(title)
    print(address)
    return lat, long, title, address


def search_by_price(price):
    result = p.search(lat=latitude, lon=longitude, radius='20000', sort='rating', order='desc', count='20')
    #print(result)
    lat = []
    long = []
    address = []
    title = []
    get_values_price(result, lat, long, title, address, price)
    print(lat)
    print(long)
    print(title)
    print(address)
    return lat, long, title, address


def search_by_query(query):
    result = p.search(lat=latitude, lon=longitude, radius='15000', sort='real_distance', order='asc',
                      q=query, count='20')
    #print(result)
    lat = []
    long = []
    address = []
    title = []
    get_values(result, lat, long, title, address)
    print(lat)
    print(long)
    print(title)
    print(address)
    return lat, long, title, address
