from tradingview_ta import TA_Handler, Interval
import time

def get_stock_data(symbol):
    time.sleep(1)
    handler = TA_Handler(
        symbol=symbol,
        exchange='NSE',
        screener='INDIA',
        interval=Interval.INTERVAL_15_MINUTES
        )
    analysis = handler.get_analysis()
    return analysis
