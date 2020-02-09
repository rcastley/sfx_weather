import json
import requests
import base64
import yaml

# Load configuration file
with open('config.yaml', 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)

# Imperial/metric unit/speed
if cfg['weather']['unit'] == 'metric':
    unit = 'C'
    speed = 'm/s'
else:
    unit = 'F'
    speed = 'mph'

# Set common URLs
weather_url = 'http://api.openweathermap.org/data/2.5'
sfx_ingest = 'https://ingest.' + cfg['signalfx']['realm'] + '.signalfx.com/v2/datapoint'
sfx_api = 'https://api.' + cfg['signalfx']['realm'] + '.signalfx.com/v2'

# Get weather for all city IDs
w_group = requests.get(weather_url + '/group?appid=' + cfg['weather']['api_key'] + '&id=' + cfg['weather']['city_ids'] + '&units=' + cfg['weather']['unit']).json()
city_count = int(w_group['cnt'])

# Get weather for main city
main_city = requests.get(weather_url + '/weather?appid=' + cfg['weather']['api_key'] +'&q=' + cfg['weather']['main_city'] + '&units=' + cfg['weather']['unit']).json()

# Set wind direction
deg=int((main_city['wind']['deg']/22.5)+.5)
arr=["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
direction = arr[(deg % 16)]

# Create JSON payload for SignalFx datapoint(s)
jsondata = []
sfxdata = {}

for i in range(city_count):    
    jsondata.append({
        'metric': 'temperature',
        'value': w_group['list'][i]['main']['temp'],
        'dimensions': {
            "city": w_group['list'][i]['name']
        }
    })

sfxdata['gauge'] = jsondata

# Get weather icon and base64 encode
iconfile = "icons/" + main_city['weather'][0]['icon'] + ".png"
with open(iconfile, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())

# Set SignalFx API headers
headers = {
    'Content-Type': 'application/json',
    'X-SF-TOKEN': cfg['signalfx']['access_token']
}

# Create Markdown for SignalFx Text Chart
chartData = {
    "customProperties" : {},
    "description": "",
    "name": main_city['name'] + ", " + main_city['sys']['country'],
    "options" : {
        "markdown" : "<table width=\"100%\" height=\"100%\" rules=\"none\">\n" +
        "<tr>\n" +
        "<td valign=\"middle\" align=\"center\">" +
        "<img src=\"data:image/png;base64, " + encoded_string.decode('utf-8') + " \" width=\"95\">\n" +
        "<font size=\"13\">" + str(round(main_city['main']['temp'])) + "&#176;" + unit + "</font>\n" +
        "<br />\n<font size=\"4\">" + main_city['weather'][0]['description'].title() + "</font>" +
        "<br /><font size=\"1\">Wind: " + direction + " " + str(round(main_city['wind']['speed'])) + " " + speed + "</font>\n" +
        "</td>\n</tr></table>",
        "type": "Text"}
    }

def post_data():
    # Send POST request
    requests.post(sfx_ingest, headers=headers, json=sfxdata)
    requests.put(sfx_api + '/chart/' + cfg['signalfx']['chart_id'], headers=headers, json=chartData)

if __name__ == "__main__":
    post_data()