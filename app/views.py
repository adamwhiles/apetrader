from flask import render_template
from .ibob_screener import get_charts
import os
import datetime
import path_config

from . import app

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/strategy/inside-bar-pattern')
def ib_pattern():
    return render_template("ib_strategy.html")
@app.route('/tools/ibob_stock_screener')
def ibob_screener():
    img_files = []
    img_dir = ""
    end = datetime.date.today() - datetime.timedelta(days=1)

    # Set start/end date for our dataframes (21 days)
    current_EST_Time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5), 'EST'))
    start=datetime.date.today() - datetime.timedelta(days=14)

    # check if it's a weekend
    weekno = datetime.datetime.today().weekday()
    today = datetime.date.today()
    if os.path.exists(f"{path_config.imageDir}/{today}") == True:
        end = today
        img_dir = f"{path_config.imageDir}/images/{end}"
    elif weekno > 5:
        # it's the weekend, get the past friday
        now = datetime.date.today()
        last_friday = now + datetime.timedelta(days=(4-now.weekday()))
        end = last_friday
        img_dir = f"{path_config.imageDir}/{end}"
    # If before 5PM EST, get previous day stats
    elif weekno == 0 and current_EST_Time.hour < 17:
        now = datetime.date.today()
        last_friday = now - datetime.timedelta(days=now.weekday()) + datetime.timedelta(days=4, weeks=-1)
        end = last_friday
        img_dir = f"{path_config.imageDir}/{end}"
    elif weekno < 5 and current_EST_Time.hour < 17:
        end=datetime.date.today() - datetime.timedelta(days=1)
        img_dir = f"{path_config.imageDir}/{end}"
    elif weekno < 5:
        end=datetime.date.today()
        img_dir = f"{path_config.imageDir}/{end}"
    else:
        img_dir = f"{path_config.imageDir}/{end}"
    for img in os.listdir(img_dir):
        f = os.path.join(img_dir, img)
        if os.path.isfile(f):
            img_files.append(f"/{end}/{img}")
    return render_template('ibob_screener.html', images=img_files)