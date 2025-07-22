import pandas as pd
import pandas_ta as ta
import requests
import json
from SmartApi import SmartConnect
from datetime import datetime, date, timedelta
import time
import random  # Optional, for jitter in sleep
import logging
import creds as l
import math, time, os
from logzero import logger
from retrying import retry
import pyotp
import numpy as np
from heikin_ashi import heikin_ashi

angelObj = None

#smartapi.angelbroking.com/docs/Historical
AB_15MIN = "FIFTEEN_MINUTE"
AB_5MIN = "FIVE_MINUTE"
AB_DAY = "ONE_DAY"

index_dict = {
        "NIFTY": {
            "spot_token": "99926000",
            "symbol_an": "Nifty 50"
            },
        "BANKNIFTY": {
            "spot_token": "99926009",
            "symbol_an": "Nifty Bank"
            },
        "CNXFINANCE": {
            "spot_token": "99926037",
            "symbol_an": "Nifty Fin Service"
            }
        }

stock_dict = {
        "DIXON" : {
            "spot_token": "21690",
            "symbol_an": "DIXON-EQ"
            },
        "ULTRACEMCO": {
            "spot_token": "11532",
            "symbol_an": "ULTRACEMCO-EQ"
            },
        "MARUTI": {
            "spot_token": "10999",
            "symbol_an": "MARUTI-EQ"
            },
        "BAJAJHLDNG": {
            "spot_token": "305",
            "symbol_an": "BAJAJHLDNG-EQ"
            },
        "NAUKRI": {
            "spot_token": "13751",
            "symbol_an": "NAUKRI-EQ"
            },
        "COFORGE": {
            "spot_token": "11543",
            "symbol_an": "COFORGE-EQ"
            },
        "BAJAJ_AUTO": {
            "spot_token": "16669",
            "symbol_an": "BAJAJ-AUTO-EQ"
            },
        "BAJFINANCE": {
            "spot_token": "317",
            "symbol_an": "BAJFINANCE-EQ"
            },
        "APOLLOHOSP": {
            "spot_token": "157",
            "symbol_an": "APOLLOHOSP-EQ"
            },
        "SIEMENS": {
            "spot_token": "3150",
            "symbol_an": "SIEMENS-EQ"
            },
        "TRENT": {
            "spot_token": "1964",
            "symbol_an": "TRENT-EQ"
            },
        "ABB": {
            "spot_token": "13",
            "symbol_an": "ABB-EQ"
            },
        "POLYCAB": {
            "spot_token": "9590",
            "symbol_an": "POLYCAB-EQ"
            },
        "LTIM": {
            "spot_token": "17818",
            "symbol_an": "LTIM-EQ"
            },
        "DIVISLAB": {
            "spot_token": "10940",
            "symbol_an": "DIVISLAB-EQ"
            },
        "PERSISTENT": {
            "spot_token": "18365",
            "symbol_an": "PERSISTENT-EQ"
            },
        "EICHERMOT": {
            "spot_token": "910",
            "symbol_an": "EICHERMOT-EQ"
            },
        "BRITANNIA": {
            "spot_token": "547",
            "symbol_an": "BRITANNIA-EQ"
            },
        "INDIGO": {
            "spot_token": "11195",
            "symbol_an": "INDIGO-EQ"
            },
        "TCS": {
            "spot_token": "11536",
            "symbol_an": "TCS-EQ"
            },
        "HEROMOTOCO": {
            "spot_token": "1348",
            "symbol_an": "HEROMOTOCO-EQ"
            },
        "HAL": {
            "spot_token": "2303",
            "symbol_an": "HAL-EQ"
            }, 
        "ICICIBANK": {
            "spot_token": "4963",
            "symbol_an": "ICICIBANK-EQ"
            },
        "HDFCBANK": {
            "spot_token": "1333",
            "symbol_an": "HDFCBANK-EQ"
            },
        "KOTAKBANK": {
            "spot_token": "1922",
            "symbol_an": "KOTAKBANK-EQ"
            },
        "SBIN": {
            "spot_token": "3045",
            "symbol_an": "SBIN-EQ"
            }
        }
@retry(stop_max_attempt_number=3)
def initAngel():
    time.sleep(1)
    print("Initializing Angel API...")
    try:
        global angelObj
        angelObj = SmartConnect(api_key=l.api_key)

        totp = pyotp.TOTP(l.token).now()
        data = angelObj.generateSession(l.username, l.password, totp)

        if data['status']:
            print("Session generated successfully.")
            refreshtoken = data['data']['refreshToken']
            feedtoken = angelObj.getfeedToken()
            userprofile = angelObj.getProfile(refreshtoken)
            print(userprofile)
            return angelObj
        else:
            print("Failed to generate session:", data['message'])
            return None

    except Exception as e:
        print("Error in initialization:", e)
        time.sleep(30)
        return None

def get_idx_symbol(key):
    if key in index_dict:
        spot_token = index_dict[key]["spot_token"]
        symbol_an = index_dict[key]["symbol_an"]
        return spot_token,symbol_an
    else:
        return "Key not found"

def get_stk_symbol(key):
    if key in stock_dict:
        spot_token = stock_dict[key]["spot_token"]
        symbol_an = stock_dict[key]["symbol_an"]
        return spot_token,symbol_an
    else:
        return "Key not found"

def getTokens():
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    d = requests.get(url).json()
    token_df = pd.DataFrame.from_dict(d)
    token_df['expiry'] = pd.to_datetime(token_df['expiry']).apply(lambda x: x.date())
    token_df = token_df.astype({'strike': float})
    return(token_df)

def getTokenInfo (symbol,exch_seg ='NSE',instrumenttype='OPTIDX',strike_price = '',pe_ce = 'PE',expiry_day = None):
    df = getTokens()
    print("inside getTokenInfo", df)
    strike_price = strike_price*100
    if exch_seg == 'NSE':
        eq_df = df[(df['exch_seg'] == 'NSE') ]
        return eq_df[eq_df['symbol'] == symbol]
    elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
    elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        return df[(df['exch_seg'] == 'NFO') & (df['expiry']==expiry_day) &  (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])
    #expiry_day = date(2022,7,28)

MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds (will increase with retries)

def get_ohlc_data_with_rate_limit(angelObj, historicParam):
    retries = 0

    while retries < MAX_RETRIES:
        try:
            response = angelObj.getCandleData(historicParam)
            if 'data' in response:
                return response['data']
            else:
                logging.warning("No 'data' key in response. Full response: %s", response)
                return None

        except Exception as e:
            retries += 1
            wait_time = RETRY_DELAY * retries + random.uniform(0, 1)  # Adding jitter
            logging.warning(f"API call failed (attempt {retries}/{MAX_RETRIES}): {e}")
            logging.info(f"Waiting for {wait_time:.2f} seconds before retrying...")
            time.sleep(wait_time)

    logging.error("Max retries reached. Failed to get OHLC data.")
    return None

def getHistoricalAPI(symbol, token, interval= 'FIVE_MINUTE'):
    to_date = datetime.now()
    from_date = to_date - timedelta(days=15)
    from_date_format = from_date.strftime("%Y-%m-%d %H:%M")
    to_date_format = to_date.strftime("%Y-%m-%d %H:%M")
    try:
        historicParam = {
            "exchange": "NSE",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "interval": interval,
            "fromdate": from_date_format,
            "todate": to_date_format
        }
        
        ohlc_data = get_ohlc_data_with_rate_limit(angelObj, historicParam)
        #ohlc_data = angelObj.getCandleData(historicParam)['data']

        print("OHLC Data fetched successfully.")


        ohlc_df = pd.DataFrame(ohlc_data)
        ohlc_df = ohlc_df.rename(
            columns={0: "date", 1: "open", 2: "high", 3: "low", 4: "close", 5: "Volume"}
        )
        history = heikin_ashi(ohlc_df)

        #history = pd.DataFrame(ohlc_data)

        #history = history.rename(
        #    columns={0: "Datetime", 1: "Open", 2: "High", 3: "Low", 4: "Close", 5: "Volume"}
        #)
        #history['Datetime'] = pd.to_datetime(history['Datetime'])
        #history = history.set_index('Datetime')
        return history
    except Exception as e:
        print("Error fetching OHLC data:", e)
        return None

def calculate_supertrend(ohlc_data, period=7, multiplier=3):

    """Calculate Supertrend and return the last close and its direction."""
    supertrend = ta.supertrend(ohlc_data['high'], ohlc_data['low'], ohlc_data['close'], period, multiplier)
    
    # Add Supertrend to the DataFrame
    ohlc_data['Supertrend'] = supertrend['SUPERT_7_3.0']
    
    # Determine Supertrend direction
    ohlc_data['Supertrend_Direction'] = np.where(ohlc_data['Supertrend'] > ohlc_data['close'], 'Downtrend', 'Uptrend')
    
    # Add RSI
    rsi15min = ta.rsi(ohlc_data['close'])
    # Add to ST
    ohlc_data['RSI15min'] = rsi15min

    # Get the last row
    last_row = ohlc_data.iloc[-1]
    last_bone = ohlc_data.iloc[-2]
    
    return {
        'Last_Close': last_row['close'],
        'RSI15min': last_row['RSI15min'],
        'Supertrend_Value': last_row['Supertrend'],
        'Supertrend_Direction': last_row['Supertrend_Direction'],
        'Strend_bone_Value': last_bone['Supertrend'],
        'Strend_bone_Direction': last_bone['Supertrend_Direction']
    }

def callAngelAPI():
    angelObj = initAngel()
    return angelObj

def callAngelInd(angelObj,symbolwo_suffix):
    print ("symbol: ",symbolwo_suffix)
    if (symbolwo_suffix == 'NIFTY') or (symbolwo_suffix == 'BANKNIFTY') or (symbolwo_suffix == 'CNXFINANCE'):
        symbol = symbolwo_suffix
        spot_token,symbol_an = get_idx_symbol(symbol)
    elif ((symbolwo_suffix == "DIXON")
        or (symbolwo_suffix == "ULTRACEMCO")
        or (symbolwo_suffix == "MARUTI")
        or (symbolwo_suffix == "BAJAJHLDNG")
        or (symbolwo_suffix == "NAUKRI")
        or (symbolwo_suffix == "COFORGE")
        or (symbolwo_suffix == "BAJAJ_AUTO")
        or (symbolwo_suffix == "BAJFINANCE")
        or (symbolwo_suffix == "APOLLOHOSP")
        or (symbolwo_suffix == "SIEMENS")
        or (symbolwo_suffix == "TRENT")
        or (symbolwo_suffix == "ABB")
        or (symbolwo_suffix == "POLYCAB")
        or (symbolwo_suffix == "LTIM")
        or (symbolwo_suffix == "DIVISLAB")
        or (symbolwo_suffix == "PERSISTENT")
        or (symbolwo_suffix == "EICHERMOT")
        or (symbolwo_suffix == "BRITANNIA")
        or (symbolwo_suffix == "INDIGO")
        or (symbolwo_suffix == "TCS")
        or (symbolwo_suffix == "HEROMOTOCO")
        or (symbolwo_suffix == "HAL")
        or (symbolwo_suffix == "ICICIBANK")
        or (symbolwo_suffix == "HDFCBANK")
        or (symbolwo_suffix == "KOTAKBANK")
        or (symbolwo_suffix == "SBIN")):
        symbol = symbolwo_suffix
        spot_token,symbol_an = get_stk_symbol(symbol)
    else:
        symbol = symbolwo_suffix + "-EQ"
        tokenInfo = getTokenInfo(symbol,'NSE')
        print("tokeinfo returned: ", tokenInfo)
        spot_token = tokenInfo.iloc[0]['token']
    
    print ("symbol: ",symbol)

    if angelObj:
        # Define parameters for OHLC data
        #symbol = "TCS-EQ"  # Change to your desired symbol
        print("spot token value: ",spot_token)
        #token = "3045"
        interval = AB_15MIN  # Define the interval
        
        # Fetch OHLC data
        ohlc_data = getHistoricalAPI(symbol, spot_token, interval)
        
        if ohlc_data is not None:
            # Calculate Supertrend
            result = calculate_supertrend(ohlc_data)

            # Print the results
            print(f"Last Close: {result['Last_Close']}")
            print(f"RSI 15min: {result['RSI15min']}")
            print(f"Supertrend Value: {result['Supertrend_Value']}")
            print(f"Supertrend Direction: {result['Supertrend_Direction']}")
            print(f"Supertrend Butone Value: {result['Strend_bone_Value']}")
            print(f"Supertrend Butone Direction: {result['Strend_bone_Direction']}")
            
        else:
            print("Failed to retrieve OHLC data.")
    
    return  {
            'close': result['Last_Close'],
            'RSI15min': result['RSI15min'],
            'Supertrend_Value': result['Supertrend_Value'],
            'Supertrend_Direction': result['Supertrend_Direction'],
            'Strend_bone_Value': result['Strend_bone_Value'],
            'Strend_bone_Direction': result['Strend_bone_Direction']
    }

