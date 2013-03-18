import os
from flask import Flask, render_template, request, Response, session, escape, jsonify
import os, urllib2, sys, json, urllib

app = Flask(__name__)
sys.path.insert(0, "python")

foursquare_client_id = "FBZHIPP1BP5UYHHDOBS1LM3E5HQS1WUFCY4XFI5WZOE45TPD"
foursquare_client_secret = "WIAOI4PMNQUYNSQR4XGDYULWU3WTBFMC2XHMVZ4N1FXIZNOF"
# This is in meters per hour
walking_speed = 5000
# This is in hours
tour_length = 1

def sessionCheck():
    if 'lat' in session and 'locality' in session:
        return True
    return False

def getFoursquareVenuesNearby(lat, lon):
    # https://api.foursquare.com/v2/venues/search?query=ise%20sushi&ll=40.7143528%2C-74.00597309999999
    latlon = urllib.quote(str(lat) + "," + str(lon))
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    radius = (tour_length * walking_speed) / 2 # they have to walk back too

    url = "https://api.foursquare.com/v2/venues/explore?v=20130315&venuePhotos=1&client_id=" + foursquare_client_id + "&client_secret=" + foursquare_client_secret + "&intent=browse&ll=" + latlon + "&radius=" + str(radius)
    urlFood = url + "&section=food"
    urlSights = url + "&section=sights&limit=10"
    urlOutdoors = url + "&section=outdoors&limit=10"
    urlArts = url + "&section=arts&limit=10"
    resource = opener.open(urlFood)
    dataFood = resource.read()
    resource.close()
    resource = opener.open(urlSights)
    dataSights = resource.read()
    resource.close()
    resource = opener.open(urlOutdoors)
    dataOutdoors = resource.read()
    resource.close()
    resource = opener.open(urlArts)
    dataArts = resource.read()
    resource.close()
    dataFood = str(dataFood).decode('utf8')
    dataSights = str(dataSights).decode('utf8')
    dataOutdoors = str(dataOutdoors).decode('utf8')
    dataArts = str(dataArts).decode('utf8')
    print url
    sys.stdout.flush();

    data = json.dumps(
        dict(
            food=json.loads(dataFood),
            sights=json.loads(dataSights),
            outdoors=json.loads(dataOutdoors),
            arts=json.loads(dataArts))
        )

    return json.loads(data)



#@app.route('/get-wikipedia', methods=['GET'])
def getWikipediaDataFromSearchTerm(term):
    import wikipedia, wiki2plain
    from bs4 import BeautifulSoup

    article = urllib.quote(term)
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia needs this

    wikiurl = "http://en.wikipedia.org/wiki/" + article
    resource = opener.open(wikiurl)
    data = resource.read()
    resource.close()

    soup = BeautifulSoup(data)
    body = soup.find('div',id="bodyContent").p
    imageurl = "http://" + str(soup.find('img')['src'])[2:] #remove the leading // on the url

    wiki2plain = wiki2plain.Wiki2Plain(str(body))
    content = str(wiki2plain.text).decode('utf8')

    # text_file = open("Output.txt", "w")
    # text_file.write(str(content))
    # text_file.close()
    # print imageurl
    return dict(content=content, imageurl=imageurl, wikiurl=wikiurl)

    # import wikipedia, wiki2plain
    # lang = 'en'
    # wiki = wikipedia.Wikipedia(lang)

    # try:
    #     raw = wiki.article(term)
    # except:
    #     raw = None

    # if raw:
    #     wiki2plain = wiki2plain.Wiki2Plain(raw)
    #     content = wiki2plain.text
    #     # content = content.split('}}')[1].split('\n');

    # text_file = open("Output.txt", "w")
    # text_file.write(str(content))
    # text_file.close()
    # sys.stdout.flush()

def get_geonames(lat, lng, types):
    url = 'http://maps.googleapis.com/maps/api/geocode/json' + \
            '?latlng={},{}&sensor=false'.format(lat, lng)
    jsondata = json.load(urllib2.urlopen(url))
    address_comps = jsondata['results'][0]['address_components']
    filter_method = lambda x: len(set(x['types']).intersection(types))
    return filter(filter_method, address_comps)

@app.route('/')
def getLocation():
    if sessionCheck():
        #get the session data
        lat = float(escape(session['lat']))
        lon = float(escape(session['lon']))
        city = str(escape(session['locality']))
        state_long = str(escape(session['city_long']))
        state_short = str(escape(session['city_short']))
        queryStr = city + ', ' + state_long
        jsonContent = getWikipediaDataFromSearchTerm(queryStr)
        # jsonContent = getWikipediaDataFromSearchTerm('San Jose, California')
        # print jsonContent
        # sys.stdout.flush()

        return render_template('home.html', 
            homeActive = 'current_page_item',
            lat = lat,
            lon = lon,
            city = city,
            state_long = state_long,
            state_short = state_short,
            content = jsonContent)
    else:
        return render_template('get-location.html')

@app.route('/user-location', methods=['GET', 'POST'])
def storeLocation():
    from flask import make_response, redirect, url_for
    import time
    from datetime import timedelta
    if request.method == 'POST':
        response = make_response(redirect('/'))
        if 'redirect' in request.form:
            response = make_response(redirect(request.form['redirect']))
        lat = request.form['lat']
        lon = request.form['lon']
        #reverse geocode lat and lon
        types = ['locality', 'administrative_area_level_1']
        for geoname in get_geonames(lat, lon, types):
            # set name of city and state in a session
            if 'locality' in geoname['types']:
                session['locality'] = geoname['long_name']
            elif 'administrative_area_level_1' in geoname['types']:
                session['city_long'] = geoname['long_name']
                session['city_short'] = geoname['short_name']

        session['lat'] = lat
        session['lon'] = lon
        #set the session to expire
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=1)
        return response
    if request.method == 'GET':
        data = dict(
                lat = str(escape(session['lat'])),
                lon = str(escape(session['lon'])),
                city = str(escape(session['locality'])),
                state_long = str(escape(session['city_long'])),
                state_short = str(escape(session['city_short']))
                )
        return jsonify(data)

@app.route('/nearby')
def nearby():
    if sessionCheck():
        lat = float(escape(session['lat']))
        lon = float(escape(session['lon']))
        city = str(escape(session['locality']))
        state_long = str(escape(session['city_long']))
        state_short = str(escape(session['city_short']))
        data = getFoursquareVenuesNearby(lat, lon)
        return render_template('nearby.html',
            data = data,
            lat = lat,
            lon = lon,
            city = city,
            state_long = state_long,
            state_short = state_short,
            nearbyActive = 'current_page_item')
    else:
        return render_template('get-location.html',
            redirect = 'nearby')

@app.route('/walking-tour')
def walkingTour():
    if sessionCheck():
        return render_template('walking-tour.html',
    	   walkingActive = 'current_page_item')
    else:
        return render_template('get-location.html',
            redirect = 'walking-tour')

@app.route('/photo-tour')
def photoTour():
    if sessionCheck():
        return render_template('photo-tour.html', 
    	   photoActive = 'current_page_item')
    else:
        return render_template('get-location.html',
            redirect = 'photo-tour')

app.secret_key = '\xa3\x8c[?\xff\xd2O\xcd\xc7^\x9f\xe9'

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
else:
    app.debug = True