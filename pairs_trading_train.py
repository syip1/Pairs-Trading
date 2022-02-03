import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from backtest_functions import compute_mean_std, pairs_trade_continuous, pairs_trade_discrete, buy_and_hold

choices = pd.read_csv('final_choices.csv').values
stock_data = pd.read_csv('HK_stocks_from_2011.csv')
#Only use train set
n = int(stock_data.shape[0] * 7 / 10)
print(n)



result = []
for i in range(choices.shape[0]):
    stock1_arr = stock_data[choices[i, 1]].values[:n]
    stock2_arr = stock_data[choices[i, 2]].values[:n]
    print("Stock 1:", choices[i, 1])
    print("Stock 2:", choices[i, 2])
    #Baseline strategy
    buy_and_hold_arr = buy_and_hold(stock1_arr, stock2_arr)
    mean, std, sharpe = compute_mean_std(buy_and_hold_arr)
    print('Baseline:', mean, std, sharpe)
    arr = [choices[i, 1], choices[i, 2], mean, std, sharpe]
    #Optimise sharpe ratio subject to volatility < 1.5 * original volatility
    days_arr = [80, 90, 100, 110, 120]
    leverage_arr = [1, 2, 3, 4, 5, 6, 7, 8]
    rebalancing_arr = [2, 3, 4, 5, 10, 20]
    max_sharpe = 0
    max_mean = 0
    max_std = 0
    days = 0
    lev = 0
    reb = 0
    for ref_days in days_arr:
        for rebalancing in rebalancing_arr:
            for leverage in leverage_arr:
                ret = pairs_trade_continuous(stock1_arr, stock2_arr, ref_days=ref_days, leverage=leverage, transaction_cost=0.005, rebalancing=rebalancing)
                stats = compute_mean_std(ret)
                if stats[1] < 1.5 * std:
                    if stats[2] > max_sharpe:
                        max_sharpe = stats[2]
                        max_mean = stats[0]
                        max_std = stats[1]
                        days = ref_days
                        lev = leverage
                        reb = rebalancing
    print('Params:', days, lev, reb)
    print('Continuous Return:', max_mean, max_std, max_sharpe)
    arr.extend([max_mean, max_std, max_sharpe, days, lev, reb])
    
    days_arr = [100, 125, 150, 175, 200]
    leverage_arr = [1, 1.5, 2, 2.5, 3, 3.5, 4]
    threshold_buy_arr = [0.02, 0.05, 0.1, 0.2, 0.3]
    threshold_sell_arr = [0.5, 0.6, 0.7]
    max_sharpe = 0
    max_mean = 0
    max_std = 0
    days = 0
    lev = 0
    buy = 0
    sell = 0
    for ref_days in days_arr:
        for thresh_buy in threshold_buy_arr:
            for thresh_sell in threshold_sell_arr:
                for leverage in leverage_arr:
                    ret = pairs_trade_discrete(stock1_arr, stock2_arr, ref_days=ref_days, leverage=leverage, threshold_buy=thresh_buy, threshold_sell=thresh_sell)
                    stats = compute_mean_std(ret)
                    if stats[1] < 2 * std:
                        if stats[2] > max_sharpe:
                            max_sharpe = stats[2]
                            max_mean = stats[0]
                            max_std = stats[1]
                            days = ref_days
                            lev = leverage
                            buy = thresh_buy
                            sell = thresh_sell
    print('Params:', days, lev, buy, sell)
    print('Discrete Return:', max_mean, max_std, max_sharpe)
    arr.extend([max_mean, max_std, max_sharpe, days, lev, buy, sell])
    
    result.append(arr)    
    
export = pd.DataFrame(result, columns = ['Stock 1', 'Stock 2', 'Base return', 'Base vol', 'Base sharpe', 
                                         'Max return C', 'Max vol C', 'Max sharpe C', 'Ref days C', 'Leverage C', 'Reb days C',
                                         'Max return D', 'Max vol D', 'Max sharpe D', 'Ref days D', 'Leverage D', 'Thresh buy D', 'Thresh sell D'])
export.to_csv('train_results.csv')

#Notes
#Increasing volatility increases sharpe
#Increasing leverage increases sharpe
#Increasing reference days seems to increase sharpe
#Maybe look at return distribution?
