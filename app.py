import os
from flask import Flask, render_template, request, Response
import Cookie
import os
import time

app = Flask(__name__)

def cookieCheck():
    if request.cookies:
        return True
    return False

@app.route('/')
def getLocation():
    if cookieCheck():
        lat = float(request.cookies['lat'])
        lon = float(request.cookies['lon'])
        # get cookie data as lat and lon
        return render_template('home.html', 
            homeActive = 'current_page_item',
            lat = lat,
            lon = lon)
    else:
        return render_template('get-location.html')

@app.route('/set-location', methods=['GET', 'POST'])
def storeLocation():
    from flask import make_response, redirect, url_for

    response = make_response(redirect('/'))
    # if cookieCheck():
    #     print "here"
    #     #reset cookie
    #     #return response
    # print "here"
    lat = request.form['lat']
    lon = request.form['lon']
    response.set_cookie('lat', lat)
    response.set_cookie('lon', lon)

    return response

@app.route('/nearby')
def nearby():
    return render_template('nearby.html', 
	   nearbyActive = 'current_page_item')

@app.route('/walking-tour')
def walkingTour():
    if 'HTTP_COOKIE' in os.environ:
        return render_template('walking-tour.html',
    	   walkingActive = 'current_page_item')

@app.route('/photo-tour')
def photoTour():
    if 'HTTP_COOKIE' in os.environ:
        return render_template('photo-tour.html', 
    	   photoActive = 'current_page_item')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)