# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 14:26:00 2021

@author: AY
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import yfinance as yf
pd.options.display.max_columns = 10
#hsi_arr = ["1109.HK", "0002.HK", "1398.HK", "1038.HK", "0101.HK", "0003.HK", "0386.HK", "0016.HK", "0012.HK", "2628.HK",
#           "1928.HK", "0267.HK", "0017.HK", "1299.HK", "0669.HK", "0883.HK", "1044.HK", "0960.HK", "1093.HK", "1997.HK",
#           "2018.HK", "2269.HK", "0027.HK", "2319.HK", "1810.HK", "2020.HK", "9988.HK", "0241.HK", "6098.HK", "3690.HK"]
#property_arr = ["0960.HK", "1109.HK", "1113.HK", "0688.HK", "2007.HK", "0012.HK", "0333.HK", "1918.HK", "0017.HK", "0083.HK",
#                "0754.HK", "0813.HK", "3380.HK", "0884.HK", "2202.HK", "1030.HK", "3383.HK", "0683.HK", "1813.HK", "2777.HK"]
#property_arr_hk = ["1113.HK", "0012.HK", "0017.HK", "0083.HK"] #factor = 1.00 -- historical, 1.05 -- 250, 1.03 -- 100, 1.06 -- 500, 1.05 -- 1000 
#property_arr_chn = ["2007.HK", "2202.HK", "3383.HK", "1638.HK"] #factor = 1.02 -- historical, 1.09 -- 500, 1.13 -- 250, 1.03 -- 100, 1.07 -- 1000
#But if do -1000 to -500, get <1.
#bank_arr_chn = ["0939.HK", "1398.HK", "3988.HK", "1288.HK", "0998.HK"] #factor = 1.02 -- 500, 1.01 -- historical, 
#data_arr = []
result_arr = []

#One pair. Take in data
df1 = pd.read_csv('1211.HK.csv')
df2 = pd.read_csv('2333.HK.csv')

#Calibrate start date
start_date = max(min(df1['Date']), min(df2['Date']))
data1 = df1[df1['Date'] > start_date]
data2 = df2[df2['Date'] > start_date]

#Drop unknown data
merged = data1.merge(data2, on = 'Date')
processed = merged.dropna().reset_index()

#Get price and ratio data
stock1 = processed.loc[:, 'Adj Close_x']
stock2 = processed.loc[:, 'Adj Close_y']
ratio12 = np.divide(stock1,stock2)

#Function to return proportion of capital held in a stock, based on rank order.
def get_factor(ratio, ratios, hedge):
    n = 0
    while ratio < ratios[n]:
        n += 1
        if n == len(ratios):
            return 1/2 + hedge/2
    return 1/2 + hedge * (n / len(ratios) - 1/2)

#Setup
balance_arr = [1] #Total return
stock_1_hold = 0
stock_2_hold = 0
balance = 1

#Time frame is 750 trading days after start date
time_frame = 750
end = stock1.size
factor, factor_prev = 0, 0 # This is to calculate transaction cost

#Option 1: use the same ratio array throughout
arr_1 = ratio12[:time_frame]

for i in range(time_frame, end, 5):
    #Option 2: use a rolling ratio array
    arr_2 = sorted(ratio12[i-time_frame:i], reverse = True)
    factor = get_factor(ratio12[i], arr_1, 2)
    if not i == time_frame:
        #Calculate present value of portfolio
        balance = stock1[i] * stock_1_hold + stock2[i] * stock_2_hold
        balance_arr.append(balance)
        #transaction fee -- assume 0.7%
        balance *= (1 - abs(factor_prev - factor) * 0.007)
    
    #Reallocate balance among two stocks
    stock_1_hold = (balance * factor) / stock1[i]
    stock_2_hold = (balance * (1 - factor)) / stock2[i]
    factor_prev = factor
   
balances = pd.Series(balance_arr)

#Plot some graphs
fig, axs = plt.subplots(2, 2)
#Top two graphs are the two stocks
axs[0, 0].plot(stock1[time_frame:stock1.size])
axs[0, 1].plot(stock2[time_frame:stock1.size])
#Bottom graph shows balance over time
axs[1, 0].plot(balances)

#Printing out some information
print('Stock 1 total return:', stock1[stock1.size - 1] / stock1[time_frame])
print('Stock 2 total return:', stock2[stock2.size - 1] / stock2[time_frame])
print('Strategy total return:', balances[balances.size - 1])

#Calculate sharpe ratio
#Use all 250-day (1 year) intervals as data
returns = []
for i in range(balances.size - 50):
    returns.append(balances[i + 50] / balances[i])
avg_return = np.mean(returns)
std_return = np.std(returns)
risk_free_rate = 1.015 #This is taken by eye of HK 10Y government bond returns
sharpe = (avg_return - risk_free_rate) / std_return

#Calculate avg rate of return for single stocks
returns1 = []
for i in range(time_frame, stock1.size - 250):
    returns1.append(stock1[i + 250] / stock1[i])
avg_return1 = np.mean(returns1)
returns2 = []
for i in range(time_frame, stock2.size - 250):
    returns2.append(stock2[i + 250] / stock2[i])
avg_return2 = np.mean(returns2)
#Print sharpe-related information
print("Stock 1 average return:", avg_return1)
print("Stock 2 average return:", avg_return2)
print("Average rate of return:", avg_return)
print("Standard deviation of return:", std_return)
print("Sharpe ratio:", sharpe)
axs[1, 1].plot(returns)
plt.show()

'''
for k in range(len(data_arr)-1):
    for j in range(k+1,len(data_arr)):
        print(k, j)
        df = pd.merge(data_arr[k], data_arr[j], left_index = True, right_index = True)
        df.dropna(inplace=True)
        df.reset_index(inplace=True)
        data1 = df['Adj Close_x']
        data2 = df['Adj Close_y']
        #print(data1.head())
        #print(data2.head())
        ratio = np.divide(data1, data2)
        #print(ratio[3102:3116])
#Proportion of assets
        for _ in range(1):
            #What if we use the previous year?
            #r = sorted(ratio[:ratio.size-500], reverse = True)
            #print(r[:10])
            balance_arr = [1]
            stock_1 = 0
            stock_2 = 0
            balance = 1
            reference = 500
            start = data1.size - 1000
            end = data1.size - 1
            
            for i in range(0, data1.size - 500, 7):
                factor = round(r.index(ratio[i]) / len(r), 1)
                if (i % 100 == 0): print(factor)
                if not i == 0:
                    #Recalculate balance
                    balance = data1[i] * stock_1 + data2[i] * stock_2
                    balance_arr.append(balance)
                #Reallocate balaance
                stock_1 = (balance * factor) / data1[i]
                stock_2 = (balance * (1 - factor)) / data2[i]
            balances = pd.Series(balance_arr)
            #print(balances[balances.size-1])
            #print(data1[data1.size-501]/data1[0], data2[data2.size-501]/data2[0])
            #Test
            balance_arr = [1]
            stock_1 = 0
            stock_2 = 0
            balance = 1
            
            total = 0
            factor, factor_prev = 0, 0
            for i in range(start, end, 30):
                #print(i)
                r = sorted(ratio[i-reference:i], reverse = True)
                factor = round(get_factor(ratio[i], r), 1)
                total += factor
                if not i == start:
                    #Recalculate balance
                    balance = data1[i] * stock_1 + data2[i] * stock_2
                    balance_arr.append(balance)
                #transaction fee
                balance *= (1 - abs(factor_prev - factor) * 0.01)
                #Reallocate balance
                stock_1 = (balance * factor) / data1[i]
                stock_2 = (balance * (1 - factor)) / data2[i]
                factor_prev = factor
            balances = pd.Series(balance_arr)
            x = balances[balances.size-1]
            y = max(data1[end]/data1[start] , data2[end]/data2[start])
            print(x, y)
            print(total/int((end - start)/7))
            print(data1[data1.size-1]/data1[data1.size-500], data2[data2.size-1]/data2[data2.size-500])
            result_arr.append(x/y)
            
            fig, axs = plt.subplots(2,2)
            axs[0,0].plot(data1[data1.size-500:])
            axs[0,1].plot(data2[data2.size-500:])
            axs[1,0].plot(ratio[ratio.size-500:])
            axs[1,1].plot(balances)
            axs[0,0].set_xlabel(str(i)+" "+str(j))
            
print(np.median(result_arr))

df1 = df1[df1['Date'] > '2010-12-17'].reset_index()
df1.dropna(inplace=True)
df2.dropna(inplace=True)
df1.reset_index(inplace=True)
df2.reset_index(inplace=True)

#parameters?
time_frame = 1000
diff_buy = 0.15
diff_sell = 0.05
balance = 1
stock1_hold = False
stock1_hand = 0
stock2_hold = False
stock2_hand = 0
for i in range(time_frame, data1.size):
    #Set exchange rate
    exchange_rate = np.nanmedian(np.divide(data1[i-time_frame:i], data2[i-time_frame:i]))
    curr_rate = ratio[i] / exchange_rate
    if stock1_hold == True:
        if curr_rate >= (1 - diff_sell):
            #Sell stock 1
            balance += stock1_hand * data1[i]
            stock1_hand = 0
            print('Sell stock 1 on day ' + str(i) + ' with price ' + str(data1[i]))
            print('Balance is ' + str(balance))
            stock1_hold = False
    elif stock2_hold == True:
        if curr_rate <= (1 - diff_sell):
            #Sell stock 2
            balance += stock2_hand * data2[i]
            stock2_hand = 0
            print('Sell stock 2 on day ' + str(i) + ' with price ' + str(data2[i]))
            print('Balance is ' + str(balance))
            stock2_hold = False
    else:
        if curr_rate <= (1 - diff_buy):
            #Buy stock 1
            stock1_hand = float(balance * 0.995)/data1[i]
            balance = 0
            print('Buy stock 1 on day ' + str(i) + ' with price ' + str(data1[i]))
            print('Balance is ' + str(balance))
            stock1_hold = True
        elif curr_rate >= (1 + diff_buy):
            #Buy stock 2
            stock2_hand = float(balance * 0.995)/data2[i]
            balance = 0
            print('Buy stock 2 on day ' + str(i) + ' with price ' + str(data2[i]))
            print('Balance is ' + str(balance))
            stock2_hold = True
print(balance + stock1_hand * data1[data1.size-1] + stock2_hand * data2[data2.size-1])

def get_factor(ratio, ratios):
    i = 0
    while ratio < ratios[i]:
        i += 1
        if i == len(ratios):
            return 1
    return i / len(ratios)

#Proportion of assets
for _ in range(1):
    r = sorted(ratio[:ratio.size-500], reverse = True)
    balance_arr = [1]
    stock_1 = 0
    stock_2 = 0
    balance = 1
    for i in range(0, data1.size - 500, 7):
        factor = round(r.index(ratio[i]) / len(r), 1)
        if (i % 100 == 0): print(factor)
        if not i == 0:
            #Recalculate balance
            balance = data1[i] * stock_1 + data2[i] * stock_2
            balance_arr.append(balance)
        #Reallocate balaance
        stock_1 = (balance * factor) / data1[i]
        stock_2 = (balance * (1 - factor)) / data2[i]
    balances = pd.Series(balance_arr)
    print(balances[balances.size-1])
    print(data1[data1.size-501]/data1[0], data2[data2.size-501]/data2[0])
    #Test
    balance_arr = [1]
    stock_1 = 0
    stock_2 = 0
    balance = 1
    for i in range(data1.size - 500, data1.size, 7):
        factor = round(get_factor(ratio[i], r), 1)
        if not i == data1.size - 500:
            #Recalculate balance
            balance = data1[i] * stock_1 + data2[i] * stock_2
            balance_arr.append(balance)
        #Reallocate balaance
        stock_1 = (balance * factor) / data1[i]
        stock_2 = (balance * (1 - factor)) / data2[i]
    balances = pd.Series(balance_arr)
    print(balances[balances.size-1])
    print(data1[data1.size-1]/data1[data1.size-500], data2[data2.size-1]/data2[data2.size-500])
    fig, axs = plt.subplots(2,2)
    axs[0,0].plot(data1)
    axs[0,1].plot(data2)
    axs[1,0].plot(ratio)
    axs[1,1].plot(balances)
'''