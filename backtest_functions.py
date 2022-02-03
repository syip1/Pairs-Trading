import numpy as np
import pandas as pd

def compute_mean_std(ret, n_days=250, risk_free=0.015):
    arr = np.exp((252/n_days) * (np.log(ret) - np.log(ret.shift(n_days))))
    m = np.mean(arr) - 1
    s = np.std(arr)
    sh = (m - risk_free) / s
    return (m, s, sh)

def pairs_trade_continuous(stock1_arr, stock2_arr, ref_days=250, leverage=1, 
                           transaction_cost=0.005, rebalancing=1, start=0):
    """Implements the following version of pairs trading:
    We hold x proportion of assets in stock1, (1-x) proportion of assets in stock2.
    Where x = leverage * rank of price ratio in the previous ref_days days.
    Transaction cost modelling is very naive at the moment, just a fixed percentage with minimum of 0.001.
    """
    assert(len(stock1_arr) == len(stock2_arr))
    assert(start < len(stock1_arr))
    assert(start >= 0)

    ratios = np.divide(stock1_arr, stock2_arr)
    
    #In the first ref_days days, just hold half in both stocks.
    stock1_hold = 0.5 / stock1_arr[start]
    stock2_hold = 0.5 / stock2_arr[start]
    capital_arr = []
    for i in range(start, ref_days):
        capital_arr.append(stock1_hold * stock1_arr[i] + stock2_hold * stock2_arr[i])

    #Start trading.
    for i in range(ref_days, len(stock1_arr)):
        current_value = stock1_hold * stock1_arr[i] + stock2_hold * stock2_arr[i]

        #Rebalance if needed.
        if (i % rebalancing == 0):
            bins = np.sort(ratios[i-ref_days:i]) #past ref_days data
            position = np.digitize(ratios[i], bins) #position of current ratio among past ratios
            #If position is large, stock1 is overvalued so hold quantity is less.
            proportion1 = 1.0/2 - leverage * (position / ref_days - 1.0/2)

            transaction_costs = min(transaction_cost * (abs(stock1_hold - current_value * proportion1 / stock1_arr[i]) \
                                + abs(stock2_hold - current_value * (1 - proportion1) / stock2_arr[i])), 0.001)
            current_value -= transaction_costs
            stock1_hold = current_value * proportion1 / stock1_arr[i]
            stock2_hold = current_value * (1 - proportion1) / stock2_arr[i]

        capital_arr.append(current_value)

    return pd.Series(capital_arr)

def pairs_trade_discrete(stock1_arr, stock2_arr, ref_days=250, leverage=1, 
                         threshold_buy=0.05, threshold_sell=0.5,
                         transaction_cost=0.005, start=0):
    """Implements the following version of pairs trading:
    On top of the buy-and-hold strategy, we long (leverage) amount of stock 1
    and short (leverage) amount of stock 2 (amount relative to current value
    of portfolio) if the ratio between stock 1 and stock 2 price falls beneath 
    (threshold_buy) percentile in (ref_days) days.
    Release when ratio goes above (threshold_sell) percentile. Vice versa for 
    long stock 2 and short stock 1.
    """

    assert(len(stock1_arr) == len(stock2_arr))
    assert(start < len(stock1_arr))
    assert(start >= 0)

    ratios = np.divide(stock1_arr, stock2_arr)
    
    #In the first ref_days days, just hold half in both stocks.
    stock1_hold = 0.5 / stock1_arr[start]
    stock2_hold = 0.5 / stock2_arr[start]
    long_stock = 0
    capital_arr = []
    for i in range(start, ref_days):
        capital_arr.append(stock1_hold * stock1_arr[i] + stock2_hold * stock2_arr[i])

    #Start trading.
    for i in range(ref_days, len(stock1_arr)):
        current_value = stock1_hold * stock1_arr[i] + stock2_hold * stock2_arr[i]
        bins = np.sort(ratios[i-ref_days:i]) #past ref_days data
        position = np.digitize(ratios[i], bins) #position of current ratio among past ratios
        if long_stock == 0:
            if position <= ref_days * threshold_buy:
                #Account for transaction costs
                stock1_hold *= (1 - transaction_cost * leverage)
                stock2_hold *= (1 - transaction_cost * leverage)
                current_value *= (1 - transaction_cost * leverage)
                #Long stock 1, short stock 2
                stock1_hold += leverage * current_value / stock1_arr[i]
                stock2_hold -= leverage * current_value / stock2_arr[i]
                long_stock = 1
                #print('Day', i, 'Long stock 1')
                
            elif position >= ref_days * (1 - threshold_buy):
                #Account for transaction costs
                stock1_hold *= (1 - transaction_cost * leverage)
                stock2_hold *= (1 - transaction_cost * leverage)
                current_value *= (1 - transaction_cost * leverage)
                #Short stock 1, long stock 2
                stock1_hold -= leverage * current_value / stock1_arr[i]
                stock2_hold += leverage * current_value / stock2_arr[i]
                long_stock = 2
                #print('Day', i, 'Long stock 2')
                
        elif long_stock == 1:
            if position >= ref_days * threshold_sell:
                #Account for transaction costs
                stock1_hold *= (1 - transaction_cost * leverage)
                stock2_hold *= (1 - transaction_cost * leverage)
                current_value *= (1 - transaction_cost * leverage)
                #Sell stock 1, buy stock 2
                stock1_hold -= leverage * current_value / stock1_arr[i]
                stock2_hold += leverage * current_value / stock2_arr[i]
                long_stock = 0
                #print('Day', i, 'sell stock 1')
        
        elif long_stock == 2:
            if position <= ref_days * (1 - threshold_sell):
                #Account for transaction costs
                stock1_hold *= (1 - transaction_cost * leverage)
                stock2_hold *= (1 - transaction_cost * leverage)
                current_value *= (1 - transaction_cost * leverage)
                #Buy stock 1, sell stock 2
                stock1_hold += leverage * current_value / stock1_arr[i]
                stock2_hold -= leverage * current_value / stock2_arr[i]
                long_stock = 0
                #print('Day', i, 'sell stock 2')
                
        capital_arr.append(current_value)
    
    return pd.Series(capital_arr)

def buy_and_hold(stock1_arr, stock2_arr, start=0):
    assert(len(stock1_arr) == len(stock2_arr))
    assert(start < len(stock1_arr))
    assert(start >= 0)
    
    stock1_hold = 0.5 / stock1_arr[start]
    stock2_hold = 0.5 / stock2_arr[start]
    capital_arr = []
    for i in range(start, len(stock1_arr)):
        capital_arr.append(stock1_hold * stock1_arr[i] + stock2_hold * stock2_arr[i])
            
    return pd.Series(capital_arr)
