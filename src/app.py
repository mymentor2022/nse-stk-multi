import dash
from dash import html, dcc, dash_table
import pandas as pd
from stock_data import get_stock_data
import time
import os
import logging
from datetime import datetime
import threading
import pytz
import creds as dwnld
from angel import *
from notif import send_notif

app = dash.Dash(__name__)
portfolio_stocks = ['SIEMENS']  # Default portfolio stock
watchlist_stocks = ['DIXON,ULTRACEMCO,MARUTI,BAJAJHLDNG,BAJAJ_AUTO,NAUKRI,COFORGE,ABB,SIEMENS,BAJFINANCE,APOLLOHOSP,TRENT,POLYCAB,LTIM,PERSISTENT,DIVISLAB,EICHERMOT,BRITANNIA,HEROMOTOCO,TCS,HAL,INDIGO,KOTAKBANK,HDFCBANK,ICICIBANK']  # Initialize watchlist
#portfolio_stocks = dwnld.portfolio_stk
#watchlist_stocks = dwnld.watchlist_stk
index_list = ['NIFTY','BANKNIFTY','CNXFINANCE']

# Initialize a log list to store log entries
log_entries = []
alerts_rsi = [] # List to store alerts
alerts_st = []

global anObj
anObj = callAngelAPI()
send_notif("TESTSTK","Trend Ind",99,999,0) #1-BOTH, 0-ONLY

# Function to log stock data every 180 seconds
def log_stock_data():
    while True:
        time.sleep(180)  # Sleep for 180 seconds
        for stock in portfolio_stocks:
            try:
                #data = get_stock_data(stock)
                #closeprice = data.indicators["close"]
                #rsi15min = round(data.indicators["RSI"],2)
                st = callAngelInd(anObj, stock)
                closeprice = round(st['close'],2)
                rsi15min = round(st['RSI15min'],2)
                strend_value = round(st['Supertrend_Value'], 2)
                strend_direction = st['Supertrend_Direction']
                strend_bone_direction = st['Strend_bone_Direction']
                    
                # Create log entry with IST timestamp
                ist_timezone = pytz.timezone('Asia/Kolkata')
                timestamp = datetime.now(ist_timezone).strftime('%Y-%m-%d %H:%M:%S')

                log_entry = f"{timestamp} - Stock Symbol: {stock}, Last Close Price: {str(closeprice)}, RSI_15min: {str(round(rsi15min, 2))}, STrend Value: {str(strend_value)}, STrend Direction: {strend_direction}"
                log_entries.append(log_entry)
                print(log_entry)
            except Exception as e:
                print(f"Error fetching data for {stock}: {e}")

        for stock in watchlist_stocks:
            try:
                #data = get_stock_data(stock)
                #closeprice = data.indicators["close"]
                #rsi15min = round(data.indicators["RSI"],2)

                st = callAngelInd(anObj, stock)
                closeprice = round(st['close'],2)
                rsi15min = round(st['RSI15min'],2)
                strend_value = round(st['Supertrend_Value'], 2)
                strend_direction = st['Supertrend_Direction']
                strend_bone_direction = st['Strend_bone_Direction']

                # Alert if RSI < 20 or RSI > 75
                if (rsi15min > 80 or rsi15min < 20): #>75 <20
                    send_notif(stock,"RSI",rsi15min,closeprice,0)

                # Alert if Super Trend direction change
                if (strend_direction=='Uptrend' and strend_bone_direction=='Downtrend'):
                    send_notif(stock,"SuperTrend Bullish",strend_value,closeprice,1)

                if (strend_direction=='Downtrend' and strend_bone_direction=='Uptrend'):
                    send_notif(stock,"SuperTrend Bearish",strend_value,closeprice,1)

                # Create log entry with IST timestamp
                ist_timezone = pytz.timezone('Asia/Kolkata')
                timestamp = datetime.now(ist_timezone).strftime('%Y-%m-%d %H:%M:%S')
 
                # Alert if RSI < 15 or RSI > 75
                if (rsi15min < 20): #<20
                    alerts_rsi.append(f"{timestamp} -Alert: {stock} RSI is below Threshold. RSI-Value: {rsi15min}. Closeprice: {closeprice}")
    
                if (rsi15min > 75 ): #>75
                    alerts_rsi.append(f"{timestamp} -Alert: {stock} RSI is above Threshold. RSI-Value: {rsi15min}. Closeprice: {closeprice}")
 
                # Alert if Super Trend direction change
                if (strend_direction=='Uptrend' and strend_bone_direction=='Downtrend'):
                    alerts_st.append(f"{timestamp} -Alert: {stock} SuperTrend is Bullish. SuperTrend-Value: {strend_value}. Closeprice: {closeprice}")
  
                if (strend_direction=='Downtrend' and strend_bone_direction=='Uptrend'):
                    alerts_st.append(f"{timestamp} -Alert: {stock} SuperTrend is Bearish. SuperTrend-Value: {strend_value}. Closeprice: {closeprice}")

            except Exception as e:
                print(f"Error fetching data for {stock}: {e}")

        #for index alerts
        for index in index_list:
            try:
                #data = get_stock_data(index)
                #closeprice = data.indicators["close"]
                #rsi15min = round(data.indicators["RSI"],2)

                st = callAngelInd(anObj, index)
                closeprice = round(st['close'],2)
                rsi15min = round(st['RSI15min'],2)
                strend_value = round(st['Supertrend_Value'], 2)
                strend_direction = st['Supertrend_Direction']
                strend_bone_direction = st['Strend_bone_Direction']

                # Alert if RSI < 20 or RSI > 80
                if (rsi15min > 80 or rsi15min < 20): #>80 <20
                    send_notif(index,"RSI",rsi15min,closeprice,1)

                # Alert if Super Trend direction change
                if (strend_direction=='Uptrend' and strend_bone_direction=='Downtrend'):
                    send_notif(index,"SuperTrend Bullish",strend_value,closeprice,1)

                if (strend_direction=='Downtrend' and strend_bone_direction=='Uptrend'):
                    send_notif(index,"SuperTrend Bearish",strend_value,closeprice,1)

                # do not send again
                already_sent_open = set()
                already_sent_close = set()

                # Create log entry with IST timestamp
                ist_timezone = pytz.timezone('Asia/Kolkata')
                timestamp = datetime.now(ist_timezone).strftime('%Y-%m-%d %H:%M:%S')
                
                current_time = datetime.now(ist_timezone)
                time_key = f"{current_time.hour}:{current_time.minute}"

                if (current_time.hour == 9 and 31 <= current_time.minute <= 34 and time_key not in already_sent_open):
                    send_notif(index,"RSI",rsi15min,closeprice,0)
                    if (strend_direction=='Uptrend'):
                        send_notif(index,"SuperTrend Bullish",strend_value,closeprice,0)
                    else:
                        send_notif(index,"SuperTrend Bearish",strend_value,closeprice,0)
                    already_sent_open.add(time_key)

                if (current_time.hour == 15 and 12 <= current_time.minute <= 15 and time_key not in already_sent_close):
                    send_notif(index,"RSI",rsi15min,closeprice,0)
                    if (strend_direction=='Uptrend'):
                        send_notif(index,"SuperTrend Bullish",strend_value,closeprice,0)
                    else:
                        send_notif(index,"SuperTrend Bearish",strend_value,closeprice,0)
                    already_sent_close.add(time_key)

                # Alert if RSI < 15 or RSI > 75
                if (rsi15min < 20): #<20
                    alerts_rsi.append(f"{timestamp} -Alert: {index} RSI is below Threshold. RSI-Value: {rsi15min}. Closeprice: {closeprice}")
    
                if (rsi15min > 75 ): #>75
                    alerts_rsi.append(f"{timestamp} -Alert: {index} RSI is above Threshold. RSI-Value: {rsi15min}. Closeprice: {closeprice}")
 
                # Alert if Super Trend direction change
                if (strend_direction=='Uptrend' and strend_bone_direction=='Downtrend'):
                    alerts_st.append(f"{timestamp} -Alert: {index} SuperTrend is Bullish. SuperTrend-Value: {strend_value}. Closeprice: {closeprice}")
  
                if (strend_direction=='Downtrend' and strend_bone_direction=='Uptrend'):
                    alerts_st.append(f"{timestamp} -Alert: {index} SuperTrend is Bearish. SuperTrend-Value: {strend_value}. Closeprice: {closeprice}")

            except Exception as e:
                print(f"Error fetching data for {index}: {e}")

# Start the logging thread
logging_thread = threading.Thread(target=log_stock_data, daemon=True)
logging_thread.start()

app.layout = html.Div(children=[
    dcc.Tabs([
        dcc.Tab(label='Portfolio', children=[
            html.Div(children=[
                html.H1(children='Stock Tracker'),
                dcc.Input(id='stock-symbol', value='SIEMENS', type='text'),
                html.Button('Submit', id='submit-button', n_clicks=0),
                html.Div(id='output-container'),
                html.Div(id='day-high-low'),
                dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0)  # Interval set to 30 seconds
            ], style={'width': '60%', 'display': 'inline-block'}),
            
            html.Div(children=[
                html.H2('Portfolio'),
                dcc.Textarea(id='portfolio-input', value='SIEMENS,TCS', style={'width': '100%', 'height': 100}),
                html.Button('Update Portfolio', id='portfolio-button', n_clicks=0),
            ], style={'width': '35%', 'display': 'inline-block', 'float': 'right'}),
            
            html.Div(children=[
                html.H2('Logs'),
                html.Ul(id='log-container'),
            ], style={'width': '60%', 'display': 'inline-block', 'float': 'left'})
        ]),
        
        dcc.Tab(label='Watchlist', children=[
            html.Div(children=[
                html.H2('Watchlist'),
                dcc.Textarea(id='watchlist-input', value='DIXON,ULTRACEMCO,MARUTI,BAJAJHLDNG,BAJAJ_AUTO,NAUKRI,COFORGE,ABB,SIEMENS,BAJFINANCE,POLYCAB,LTIM,PERSISTENT,DIVISLAB,BRITANNIA,HEROMOTOCO,TCS,APOLLOHOSP,TRENT,INDIGO,HAL,KOTAKBANK,HDFCBANK,ICICIBANK', style={'width': '100%', 'height': 100}),
                html.Button('Update Watchlist', id='watchlist-button', n_clicks=0),
                
                # Table for displaying watchlist data
                dash_table.DataTable(
                    id='watchlist-table',
                    columns=[
                        {'name': 'Stock Name', 'id': 'stock_name'},
                        {'name': 'Close Price', 'id': 'close_price'},
                        {'name': 'RSI Value', 'id': 'rsi_value'},
                        {'name': 'SuperTrend', 'id': 'supertrend'},
                        {'name': 'SuperTrend Direction', 'id': 'strend_direction'},
                    ],
                    data=[],
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left'},
                    page_size=10,  # Set page size to 3 for a 3-row table
                    sort_action="native",  # Enable native sorting
                    sort_by=[{'column_id': 'rsi_value', 'direction': 'asc'}]  # Default sort by RSI (ascending)
                ),
            ], style={'width': '60%', 'display': 'inline-block'}),

            html.Div(children=[
                
                # Table for displaying watchlist data
                dash_table.DataTable(
                    id='index-table',
                    columns=[
                        {'name': 'Index Name', 'id': 'index_name'},
                        {'name': 'Close Price', 'id': 'close_price'},
                        {'name': 'RSI Value', 'id': 'rsi_value'},
                        {'name': 'SuperTrend', 'id': 'supertrend'},
                        {'name': 'SuperTrend Direction', 'id': 'strend_direction'},
                    ],
                    data=[],
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left'},
                    page_size=3  # Set page size to 3 for a 3-row table
                ),
            ], style={'width': '60%', 'display': 'inline-block'}),

            html.Div(children=[
                html.H2('Alerts for SuperTrend and MACD'),
                html.Ul(id='alerts-st-container'),
            ], style={'width': '60%', 'display': 'inline-block', 'float': 'left'}),
            html.Div(children=[
                html.H2('Alerts for RSI'),
                html.Ul(id='alerts-rsi-container'),
            ], style={'width': '40%', 'display': 'inline-block', 'float': 'right'})
        ])
    ])
])

@app.callback(
    [dash.dependencies.Output('output-container', 'children'),
     dash.dependencies.Output('log-container', 'children'),
     dash.dependencies.Output('watchlist-table', 'data'),
     dash.dependencies.Output('index-table', 'data'),
     dash.dependencies.Output('alerts-st-container', 'children'),
     dash.dependencies.Output('alerts-rsi-container', 'children'),
     ],
    [dash.dependencies.Input('submit-button', 'n_clicks'),
     dash.dependencies.Input('interval-component', 'n_intervals'),
     dash.dependencies.Input('portfolio-button', 'n_clicks'),
     dash.dependencies.Input('watchlist-button', 'n_clicks')],
    [dash.dependencies.State('stock-symbol', 'value'),
     dash.dependencies.State('portfolio-input', 'value'),
     dash.dependencies.State('watchlist-input', 'value')]
)
def update_output(n_clicks, n_intervals, portfolio_clicks, watchlist_clicks, value, portfolio_input, watchlist_input):
    global portfolio_stocks, watchlist_stocks,alerts
    
    # Update portfolio and watchlist
    if portfolio_clicks > 0:
        portfolio_stocks = [stock.strip() for stock in portfolio_input.split(',') if stock.strip()]
    
    if watchlist_clicks >= 0:
        watchlist_stocks = [stock.strip() for stock in watchlist_input.split(',') if stock.strip()]
    
    output = []
    log_output = [html.Li(entry) for entry in reversed(log_entries)]
    
    # Update watchlist data
    watchlist_data = []
    for stock in watchlist_stocks:
        try:
            #data = get_stock_data(stock)
            #closeprice = data.indicators["close"]
            #rsi15min = data.indicators["RSI"]
            st = callAngelInd(anObj, stock)
            closeprice = round(st['close'],2)
            rsi15min = round(st['RSI15min'],2)
            strend_value = round(st['Supertrend_Value'], 2)
            strend_direction = st['Supertrend_Direction']
            strend_bone_direction = st['Strend_bone_Direction']
            
            watchlist_data.append({
                'stock_name': stock,
                'close_price': closeprice,
                'rsi_value': round(rsi15min, 2),
                'supertrend': strend_value,
                'strend_direction': strend_direction
            })
        except Exception as e:
            print(f"Error fetching data for watchlist stock {stock}: {e}")

    #prepare alerts for display
    alert_st_output = [html.Li(alert) for alert in alerts_st]
    alert_rsi_output = [html.Li(alert) for alert in alerts_rsi]

    # Update index data
    indexlist_data = []
    index_list = ['NIFTY','BANKNIFTY','CNXFINANCE']
    for index in index_list:
        try:
            #data = get_stock_data(index)
            #closeprice = data.indicators["close"]
            #rsi15min   = data.indicators["RSI"]
            #macd       = data.indicators['MACD.macd']
            #signal     = data.indicators['MACD.signal']
            #if (macd - signal) > 0:
            #    macd_direction = "UpTrend"
            #else:
            #    macd_direction = "DownTrend"
            st = callAngelInd(anObj, index)
            closeprice = round(st['close'],2)
            rsi15min = round(st['RSI15min'],2)
            strend_value = round(st['Supertrend_Value'], 2)
            strend_direction = st['Supertrend_Direction']
            indexlist_data.append({
                'index_name': index,
                'close_price': closeprice,
                'rsi_value': round(rsi15min, 2),
                'supertrend': strend_value,
                'strend_direction': strend_direction
            })
        except Exception as e:
            print(f"Error fetching data for index list {index}: {e}")

    # Update based on the button click for stock data
    if n_clicks > 0:
        try:
            #data = get_stock_data(value)
            #rsi15min = data.indicators["RSI"]
            #closeprice = data.indicators["close"]

            st = callAngelInd(anObj, value)
            closeprice = round(st['close'],2)
            rsi15min = round(st['RSI15min'],2)
            strend_value = st['Supertrend_Value']
            strend_direction = st['Supertrend_Direction']

            output = [
                html.Li(f"Stock Symbol: {value}"),
                html.Li(f"RSI_15min: {str(round(rsi15min, 2))}"),
                html.Li(f"Last Close Price: {str(closeprice)}"),
                html.Li(f"SuperTrend Value: {str(round(strend_value, 2))}"),
                html.Li(f"SuperTrend Direction: {strend_direction}")
            ]
        except Exception as e:
            output.append(f'Error fetching data for {value}: {e}')

    return output, log_output, watchlist_data, indexlist_data,alert_st_output,alert_rsi_output

if __name__ == '__main__':
    #send_notif('ABB',"RSI")
    app.run(host='0.0.0.0', port=8050)
    #app.run_server(debug=True)
