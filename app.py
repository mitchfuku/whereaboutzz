import os
from flask import Flask, render_template, request, Response
import Cookie, os, json, urllib2, sys

app = Flask(__name__)
sys.path.insert(0, "python")

def cookieCheck():
    if request.cookies:
        if request.cookies.get('lat') is not None and request.cookies.get('locality') is not None:
            return True
    return False

#@app.route('/get-wikipedia', methods=['GET'])
def getWikipediaDataFromSearchTerm(term):
    import wikipedia
    import wiki2plain

    lang = 'en'
    wiki = wikipedia.Wikipedia(lang)
    content = None
    try:
        raw = wiki.article(term)
    except:
        raw = None

    if raw:
        wiki2plain = wiki2plain.Wiki2Plain(raw)
        content = wiki2plain.text

    print content

def get_geonames(lat, lng, types):
    url = 'http://maps.googleapis.com/maps/api/geocode/json' + \
            '?latlng={},{}&sensor=false'.format(lat, lng)
    jsondata = json.load(urllib2.urlopen(url))
    address_comps = jsondata['results'][0]['address_components']
    filter_method = lambda x: len(set(x['types']).intersection(types))
    return filter(filter_method, address_comps)

@app.route('/')
def getLocation():
    if cookieCheck():
        lat = float(request.cookies.get('lat'))
        lon = float(request.cookies.get('lon'))
        city = str(request.cookies.get('locality'))
        state_long = str(request.cookies.get('city_long'))
        state_short = str(request.cookies.get('city_short'))
        queryStr = city + ', ' + state_long
        content = getWikipediaDataFromSearchTerm(queryStr)
        # get cookie data as lat and lon
        return render_template('home.html', 
            homeActive = 'current_page_item',
            lat = lat,
            lon = lon,
            city = city,
            state_long = state_long,
            state_short = state_short,
            content = content)
    else:
        return render_template('get-location.html')

@app.route('/set-location', methods=['GET', 'POST'])
def storeLocation():
    from flask import make_response, redirect, url_for
    import time
    response = make_response(redirect('/'))
    if 'redirect' in request.form:
        response = make_response(redirect(request.form['redirect']))
    lat = request.form['lat']
    lon = request.form['lon']
    exp = time.time() + 1 * 24 * 3600
    #reverse geocode lat and lon
    types = ['locality', 'administrative_area_level_1']
    for geoname in get_geonames(lat, lon, types):
        # set name of city and state in cookie
        if 'locality' in geoname['types']:
            response.set_cookie('locality', geoname['long_name'], expires=exp)
        elif 'administrative_area_level_1' in geoname['types']:
            response.set_cookie('city_long', geoname['long_name'], expires=exp)
            response.set_cookie('city_short', geoname['short_name'], expires=exp)

    response.set_cookie('lat', lat, expires=exp)
    response.set_cookie('lon', lon, expires=exp)
    return response

@app.route('/nearby')
def nearby():
    if cookieCheck():
        return render_template('nearby.html', 
    	   nearbyActive = 'current_page_item')
    else:
        return render_template('get-location.html',
            redirect = 'nearby')

@app.route('/walking-tour')
def walkingTour():
    if cookieCheck():
        return render_template('walking-tour.html',
    	   walkingActive = 'current_page_item')
    else:
        return render_template('get-location.html',
            redirect = 'walking-tour')

@app.route('/photo-tour')
def photoTour():
    if cookieCheck():
        return render_template('photo-tour.html', 
    	   photoActive = 'current_page_item')
    else:
        return render_template('get-location.html',
            redirect = 'photo-tour')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
else:
    app.debug = True