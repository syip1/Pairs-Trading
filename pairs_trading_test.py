import pandas as pd
from backtest_functions import compute_mean_std, pairs_trade_continuous, pairs_trade_discrete, buy_and_hold

train_data = pd.read_csv('train_results.csv')
stock_data = pd.read_csv('HK_stocks_from_2011.csv')
n = int(stock_data.shape[0] * 7 / 10)
cont_or_disc = train_data['Max sharpe C'] > train_data['Max sharpe D']

results = []
for i in range(train_data.shape[0]):
    stock1_arr = stock_data[train_data['Stock 1'][i]]
    stock2_arr = stock_data[train_data['Stock 2'][i]]
    print("Stock 1:", train_data['Stock 1'][i])
    print("Stock 2:", train_data['Stock 2'][i])
    
    #Baseline strategy
    base = buy_and_hold(stock1_arr, stock2_arr, n)
    mean, std, sharpe = compute_mean_std(base)
    print("Baseline:", mean, std, sharpe)
    arr = [train_data['Stock 1'][i], train_data['Stock 2'][i], mean, std, sharpe]
    
    #See whether continuous or discrete is better
    if (cont_or_disc[i]):
        result = pairs_trade_continuous(stock1_arr, stock2_arr, \
                                     ref_days=train_data['Ref days C'][i], \
                                     leverage=train_data['Leverage C'][i], \
                                     transaction_cost=0.005, rebalancing=train_data['Reb days C'][i], \
                                     start = n)
        method = 'C'
    else:
        result = pairs_trade_discrete(stock1_arr, stock2_arr, \
                                   ref_days=train_data['Ref days D'][i], \
                                   leverage=train_data['Leverage D'][i], \
                                   threshold_buy=train_data['Thresh buy D'][i], \
                                   threshold_sell=train_data['Thresh sell D'][i], \
                                   start = n)
        method = 'D'
    
    mean_pairs, std_pairs, sharpe_pairs = compute_mean_std(result)
    print("Pairs:", method, mean_pairs, std_pairs, sharpe_pairs)
    arr.extend([method, mean_pairs, std_pairs, sharpe_pairs])
    results.append(arr)

export = pd.DataFrame(results, columns = ['Stock 1', 'Stock 2', 'Base return', 'Base std', 'Base sharpe', \
                                          'Pairs method', 'Pairs return', 'Pairs std', 'Pairs sharpe'])
export.to_csv('test_results.csv')    
