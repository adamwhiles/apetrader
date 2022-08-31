import mplfinance as mpf
import pandas as pd
import pandas_datareader.data as web
from pandas_datareader.yahoo.headers import DEFAULT_HEADERS
import requests_cache
import datetime
import numpy as np
import os
import path_config

# Setup folder structure to store images of charts
if os.path.exists(path_config.imageDir) == False:
    os.makedirs(path_config.imageDir)


# Setup session cache so we don't make repeated calls to API
expire_after = datetime.timedelta(hours=6)
session = requests_cache.CachedSession(cache_name=path_config.dbFile, backend='sqlite', expire_after=expire_after)
session.headers = DEFAULT_HEADERS

# Set start/end date for our dataframes (21 days)
current_EST_Time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5), 'EST'))
start=datetime.date.today() - datetime.timedelta(days=14)
print("Current EST Time:", current_EST_Time.hour)
print("Current Server Time:", datetime.datetime.now().hour)

# If before 5PM EST, get previous day stats
if current_EST_Time.hour < 15:
    print("Before 5PM EST")
    end=datetime.date.today() - datetime.timedelta(days=1)
    print(f"Setting End Date to: {end}")
    image_dir = f"{path_config.imageDir}/{end}"
    if os.path.exists(image_dir) == False:
        os.mkdir(image_dir)
else:
    session.cache.clear()
    end=datetime.date.today()
    image_dir = f"{path_config.imageDir}/{end}"
    if os.path.exists(image_dir) == False:
        os.mkdir(image_dir)

# Prep dict of ticker DF's with IB or OB on last reported day
flagged_DF = {}

# Prep array of figures to display
figures = []

# Define CandleStick colors for IB and OB bars
ib_mc = mpf.make_marketcolors(base_mpf_style='yahoo',up='white',down='white',
                            edge={'up':'green','down':'red'},wick='black')

ob_mc = mpf.make_marketcolors(base_mpf_style='yahoo',up='black',down='black',
                            edge={'up':'green','down':'red'},wick='black')

print(f"Start: {start} --- End: {end}")
# Define Tickers to lookup
tickers=["AMD","ADBE","ABNB","ALGN","AMZN","AMGN","AEP","ADI","ANSS","AAPL","AMAT","ASML","TEAM","ADSK","ATVI","ADP","AVGO","BIDU","BIIB","BMRN","BKNG","CDNS","CHTR","CPRT","CRWD","CTAS","CSCO","CMCSA","COST","CSX","CTSH","DDOG","DOCU","DXCM","DLTR","EA","EBAY","EXC","FAST","FB","FISV","FTNT","GILD","GOOGL","HON","ILMN","INTC","INTU","ISRG","MSFT","TSLA","NVDA","JPM","JNJ","UNH","HD","PG","V","BAC","MA","XOM","PFE","DIS","CVX","ABBV","PEP","KO","TMO","NFLX","WFC","ABT","CRM","VZ","ACN","MRK","PYPL","WMT","QCOM","LLY","T","MCD","NKE","DHR","TXN","LOW","LIN"]


# Received ticker name and dataframe, detect if last reported day had IB or OB
def detect_Recent_IBOB(ticker, df):
    short_df = df.tail(2)
    prevDayHigh = short_df.iloc[0,0]
    prevDayLow = short_df.iloc[0,1]
    lastDayHigh = short_df.iloc[1,0]
    lastDayLow = short_df.iloc[1,1]
    if lastDayHigh < prevDayHigh and lastDayLow > prevDayLow:
        #flagged_DF.append(df)
        flagged_DF[ticker] = df
    elif lastDayHigh > prevDayHigh and lastDayLow < prevDayLow:
        flagged_DF[ticker] = df

def detect_All_IBOB(ticker, df):
    # Add Columns for IB/OB and Candlestick colors to DataFrame
    df.insert(6, "IBorOB", None, True)
    df.insert(7, "MCOverrides", None, True)
    row_count = 0
    ib_markers = []
    ob_markers = []
    for index, row in df.iterrows():   
        if row_count != 0:
            currentDayHigh = row['High']
            currentDayLow = row['Low']
            prevDayHigh = df.iloc[row_count-1, 0]
            prevDayLow = df.iloc[row_count-1, 1]
            # Check for last reported day inside bar
            if currentDayHigh < prevDayHigh and currentDayLow > prevDayLow:
                df.iat[row_count, 6] = "IB"
                df.iat[row_count, 7] = ib_mc
                ib_markers.append(row['High']*1.01)
                ob_markers.append(np.nan)
            # Check for last reported day outside bar
            elif currentDayHigh > prevDayHigh and currentDayLow < prevDayLow:
                df.iat[row_count, 6] = "OB"
                df.iat[row_count, 7] = ob_mc
                ob_markers.append(row['Low']*0.99)
                ib_markers.append(np.nan)
            else:
                ib_markers.append(np.nan)
                ob_markers.append(np.nan)
        else:
            ib_markers.append(np.nan)
            ob_markers.append(np.nan)
        row_count = row_count + 1
    return ib_markers, ob_markers
    
def _add_candlestick_labels(ax, ohlc):
    transform = ax.transData.inverted()
    # show the text 10 pixels above/below the bar
    text_pad = transform.transform((0, 10))[1] - transform.transform((0, 0))[1]
    percentages = 100. * (ohlc.Close - ohlc.Open) / ohlc.Open
    kwargs = dict(horizontalalignment='center', color='#000000')
    for i, (idx, val) in enumerate(percentages.items()):
        if val != np.nan:
            row = ohlc.loc[idx]
            if row.IBorOB == "IB":
                ax.text(i, row.High + text_pad, "IB", verticalalignment='bottom', **kwargs)
            elif row.IBorOB == "OB":
                ax.text(i, row.Low - text_pad, "OB", verticalalignment='top', **kwargs)



print("Getting Data")
for ticker in tickers:
    print(f"Working on {ticker}")
    df=web.DataReader(ticker, 'yahoo', start, end, session=session)
    detect_Recent_IBOB(ticker, df)

for ticker, df in flagged_DF.items():
    ib_markers, ob_markers = detect_All_IBOB(ticker, df)
    mco = df['MCOverrides'].values
    figure, axlist = mpf.plot(df, type='candle', style='yahoo',title='{} Chart'.format(ticker), returnfig=True, marketcolor_overrides=mco, figscale=0.75, xrotation=90, datetime_format="%m/%d")
    _add_candlestick_labels(axlist[0], df)
    print(f"Saving image for {ticker}")
    fig_image = f"{path_config.imageDir}/{end}/{ticker}-{end}"
    print("Saving to: " + fig_image)
    if os.path.exists(f"{path_config.imageDir}/{end}") == False:
        os.mkdir(image_dir)
    figure.savefig(fig_image)




