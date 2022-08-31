# apetrader
Apetrader is a stock screening tool built with Python, Flask and a few different libraries like pandas, matplotlib etc.

# Requirements
Install mplfinance, matplotlib, pandas-datareader, requests_cache[all]
Update the path_config.py file located in the app directory with your desired images path and path to the sqlite database file

The get_data.py script should run using a cron job at a scheduled time to generate the charts which are then picked up by the Flask website.
