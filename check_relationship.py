import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.stattools import adfuller
def adf_test(timeseries):
    #print ('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    #print (dfoutput)
    return dfoutput['p-value']

prices = pd.read_csv('HK_stocks_from_2011.csv')
prices.rename(columns={'Adj Close': 'Adj Close_1'}, inplace = True)
possibilities = pd.read_csv('possibilities.csv').values[:, 1:] #Column 0 is index
#Restrict attention to train set
n = int(prices.shape[0] * 7 / 10)
prices = prices.head(n)

#Plot graph
'''
for i in range(len(possibilities)):
    stock1 = prices.loc[:, possibilities[i][0]]
    stock2 = prices.loc[:, possibilities[i][1]]
    plt.scatter(stock1, stock2)
    plt.title(possibilities[i][0] + ' ' + possibilities[i][1])
    plt.show()
'''
#After looking at graph
#remove: 2828 and 388, 2828 and 806
possibilities = np.delete(possibilities, [30, 31], axis = 0)
#print(possibilities)

#Stationarity test (Augmented Dickey-Fuller)
filtered_poss = []
for i in range(len(possibilities)):
    stock1 = prices.loc[:, possibilities[i][0]]
    stock2 = prices.loc[:, possibilities[i][1]]
    ratio = np.divide(stock1, stock2)
    if adf_test(ratio) < 0.05:
        filtered_poss.append(possibilities[i])
final_choices = pd.DataFrame(filtered_poss)
final_choices.to_csv('final_choices.csv')
