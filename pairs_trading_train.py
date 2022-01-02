import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from backtest_functions import pairs_trade_continuous, buy_and_hold

choices = pd.read_csv('final_choices.csv').values
stock_data = pd.read_csv('HK_stocks_from_2011.csv')
#Only use train set
n = int(stock_data.shape[0] * 7 / 10)
print(n)

#Try the first one
stock1_arr = stock_data[choices[0, 1]].values[:n]
stock2_arr = stock_data[choices[0, 2]].values[:n]

print('Ref day Hedge Rebal day Mean ret Std ret Sharpe')

#Reference values
buy_and_hold_arr = buy_and_hold(stock1_arr, stock2_arr)
for ret in [buy_and_hold_arr, stock1_arr, stock2_arr]:
    #Generate sample 500-day returns
    ret500 = []
    for i in range(500, len(ret)):
        ret500.append(math.pow(ret[i]/ret[i-500], 0.504))
    meanret = np.mean(ret500) - 1
    stdret = np.std(ret500)
    sharperet = (meanret - 0.015) / stdret #Assume risk-free rate = 1.5%
    print(round(meanret, 2), '\t', round(stdret, 2), '\t', round(sharperet, 2))

#Tune some hyperparameters

for ref_days in [10, 50, 100, 250, 500, 1000]:
    for hedge in [0.2, 0.5, 1, 2, 5]:
        for rebalancing in [1, 5, 20, 100, 250]:
            ret = pairs_trade_continuous(stock1_arr, stock2_arr, ref_days, hedge, 0.005, rebalancing)
            #Generate sample 500-day returns
            ret500 = []
            for i in range(500, len(ret)):
                ret500.append(math.pow(ret[i]/ret[i-500], 0.504))
            meanret = np.mean(ret500) - 1
            stdret = np.std(ret500)
            sharperet = (meanret - 0.015) / stdret #Assume risk-free rate = 1.5%
            print(ref_days, '\t', hedge, '\t', rebalancing, '\t', \
                  round(meanret, 2), '\t', round(stdret, 2), '\t', round(sharperet, 2))

