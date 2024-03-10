from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Instructors, put in your YELP API KEY below.
YELP_API_KEY = 'INSERT YELP API KEY'

def get_yelp_locations(latitude, longitude, max_distance_miles, categories):
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {
        'Authorization': 'Bearer ' + YELP_API_KEY
    }
    locations = []
    for category in categories.split(','):
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'radius': max_distance_miles * 1609,  # converting miles to meters
            'limit': 10,  # number of results limit
            'categories': categories  # filter it by categories
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return None

        data = response.json()

        locations = []

        if 'businesses' in data:
            for business in data['businesses']:
                location_info = {
                    'name': business['name'],
                    'address': ', '.join(business['location']['display_address']),
                    'phone': business.get('phone', 'N/A'),
                    'distance': round(business['distance'] * 0.000621371, 2),  # convert meters to miles
                    'rating': business.get('rating', 'N/A'),
                    'image_url': business['image_url']
                }

                locations.append(location_info)
    return locations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    activities = request.form.getlist('activities')
    miles = int(request.form['miles'])
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    if latitude and longitude:
        latitude = float(latitude)
        longitude = float(longitude)
    else:
        # default location if current location not provided (downtown Seattle)
        latitude = 47.6062
        longitude = -122.3321

    selected_categories = []
    if 'cafes' in activities:
        selected_categories.extend(['cafes', 'coffee'])
    if 'desserts' in activities:
        selected_categories.extend(['desserts', 'bakeries', 'icecream', 'yogurt', 'sweets', 'cake', 'pie', 'cookies'])
    if 'studying' in activities:
        selected_categories.extend(['libraries'])
    if 'physical_activity' in activities:
        selected_categories.extend(['parks', 'recreation', 'lakes'])
    if 'food' in activities:
        selected_categories.extend(['food'])

    selected_categories_str = ','.join(selected_categories)

    locations = get_yelp_locations(latitude, longitude, miles, selected_categories_str)

    if locations is None:
        message = "No results found. Please try again with different options."
        return render_template('results.html', message=message)
    else:
        return render_template('results.html', locations=locations)

if __name__ == '__main__':
    app.run(debug=True)
