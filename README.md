# sfx_weather
Python script to populate weather metrics and create weather (text) chart

Edit the `config.yaml`

Create a default text chart in SFx and note the chart ID

Run `weather.py` as a cron job e.g.

`*/30 * * * * cd /home/rwc/sfx_weather/; python3 /home/rwc/sfx_weather/weather.py`

![SFx Weather Screenshot](https://github.com/rcastley/sfx_weather/blob/master/icons/screenshot.png)
