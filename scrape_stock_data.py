import pandas_datareader as pdr
import pandas as pd
import numpy as np
df = pd.DataFrame(pdr.get_data_yahoo('0001.HK', start='2010-12-01'))['Adj Close']

for i in range(2, 3000):
    print(i)
    print(df.shape)
    name = '0'*(4 - len(str(i)))+str(i)+".HK"
    try:
        data = pdr.get_data_yahoo(name, start='2010-12-01')
        #print(data.index[0])
        if data.index[0] < pd.Timestamp('2011-01-01') and np.min(data['Volume'].values[0:5]) > 50000:
            curr = data['Adj Close']
            #print(curr.head())
            df = pd.merge(df, curr, left_index = True, right_index = True, suffixes = ("", "_"+str(i)))
            print('Stock '+str(i)+' added')
    except:
        continue
df.to_csv('HK_stocks_from_2011.csv')

