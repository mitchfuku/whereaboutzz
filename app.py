import os
from flask import Flask, render_template, request, Response

app = Flask(__name__)

@app.route('/')
def getLocation():
    return render_template('get-location.html')
# def home():
#     return render_template('home.html', 
#     	homeActive = 'current_page_item')

@app.route('/home', methods=['GET', 'POST'])
def home():
    lat = request.form['lat']
    lon = request.form['lon']
    return render_template('home.html', 
        homeActive = 'current_page_item',
        lat = lat,
        lon = lon)

@app.route('/nearby')
def nearby():
    return render_template('nearby.html', 
    	nearbyActive = 'current_page_item')

@app.route('/walking-tour')
def walkingTour():
    return render_template('walking-tour.html',
    	walkingActive = 'current_page_item')

@app.route('/photo-tour')
def photoTour():
    return render_template('photo-tour.html', 
    	photoActive = 'current_page_item')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)