import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
df = pd.read_csv('HK_stocks_from_2011.csv')
df.rename(columns = {'Adj Close': 'Adj Close_1'}, inplace = True)
df_no_date = df.drop('Date', axis = 1)
n = df.shape[0]
#print(df.shape)
#print(df.isna().sum().sum())
sig = []
for i in df_no_date.columns:
    for j in df_no_date.columns:
        if (i < j):
            #Brake it down into 10 periods, say.
            correlated = True
            for k in range(7):
                #The 8th period is a validation set
                #We save the final 2 periods for a test set
                begin = int(k*n/10)
                end = int((k+1)*n/10)
                first = df_no_date[i].values[begin:end]
                second = df_no_date[j].values[begin:end]
                #Account for an array being constant
                if np.all(second == second[0]) or np.all(first == first[0]):
                    correlated = False
                    break
                pmcc, p = stats.pearsonr(df_no_date[i].values[begin:end], \
                                         df_no_date[j].values[begin:end])
                if (abs(pmcc) < 0.8):
                    correlated = False
                    break
            if correlated:
                #print(i, j)
                sig.append([i, j])

df = pd.DataFrame(sig)
df.columns = ['Stock 1', 'Stock 2']
df.to_csv('possibilities.csv')
