import pandas as pd

def heikin_ashi(df):
    heikin_ashi_df = pd.DataFrame(index=df.index.values, columns=['open', 'high', 'low', 'close'])
    
    heikin_ashi_df['close'] = round(((df['open'] + df['high'] + df['low'] + df['close']) / 4),2)
    
    for i in range(len(df)):
        if i == 0:
            heikin_ashi_df.iat[0, 0] = round(((df['open'].iloc[0] + df['close'].iloc[0])/2),2)
        else:
            heikin_ashi_df.iat[i, 0] = round(((heikin_ashi_df.iat[i-1, 0] + heikin_ashi_df.iat[i-1, 3]) / 2),2)
        
    heikin_ashi_df['high'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['high']).max(axis=1)
    
    heikin_ashi_df['low'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['low']).min(axis=1)
    
    return heikin_ashi_df
    
