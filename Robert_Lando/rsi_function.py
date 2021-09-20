def rsi(df,column_name,n, ema = True):
    """
    Returns a pd.Series with the relative strength index.
    
    inputs:
    
    df: dataframe
    columns_name: str, columns label to calculat the rsi of
    n: rsi period length
    ema: Bool, whether or not to use exponantial moving average or simple moving average in calculation
    
    """
    delta = df[column_name].diff(1)

    # Make two series: one for lower closes and one for higher closes
    
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    if ema == True:
        
        ma_up = up.ewm(com = n - 1, adjust=True, min_periods = n).mean()
        ma_down = down.ewm(com = n - 1, adjust=True, min_periods = n).mean()
        
    else:
        # Use simple moving average
        ma_up = up.rolling(window = n).mean()
        ma_down = down.rolling(window = n).mean()
        
    rsi = ma_up / ma_down
    rsi = 100 - (100/(1 + rsi))
    return rsi