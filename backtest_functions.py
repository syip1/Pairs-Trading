import numpy as np

def pairs_trade_continuous(stock1_arr, stock2_arr, ref_days=250, hedge=1, transaction_cost=0.005, rebalancing=1):
    """Implements the following version of pairs trading:
    We hold x proportion of assets in stock1, (1-x) proportion of assets in stock2.
    Where x = hedge * rank of price ratio in the previous ref_days days.
    Transaction cost modelling is very naive at the moment, just a fixed percentage with minimum of 0.001.
    """
    assert(len(stock1_arr) == len(stock2_arr))

    ratios = np.divide(stock1_arr, stock2_arr)
    
    #In the first ref_days days, just hold half in both stocks.
    capital = 1
    stock1_hold = 0.5 / stock1_arr[0]
    stock2_hold = 0.5 / stock2_arr[0]
    capital_arr = []
    for i in range(ref_days):
        capital_arr.append(stock1_hold * stock1_arr[i] + stock2_hold * stock2_arr[i])

    #Start trading.
    for i in range(ref_days, len(stock1_arr)):
        current_value = stock1_hold * stock1_arr[i] + stock2_hold * stock2_arr[i]

        #Rebalance if needed.
        if (i % rebalancing == 0):
            bins = np.sort(ratios[i-ref_days:i]) #past ref_days data
            position = np.digitize(ratios[i], bins) #position of current ratio among  past ratios
            #If position is large, stock1 is overvalued so hold quantity is less.
            proportion1 = 1.0/2 - hedge * (position / ref_days - 1.0/2)

            transaction_costs = min(transaction_cost * (abs(stock1_hold - current_value * proportion1 / stock1_arr[i]) \
                                + abs(stock2_hold - current_value * (1 - proportion1) / stock2_arr[i])), 0.001)
            current_value -= transaction_costs
            stock1_hold = current_value * proportion1 / stock1_arr[i]
            stock2_hold = current_value * (1 - proportion1) / stock2_arr[i]

        capital_arr.append(current_value)

    return capital_arr

def buy_and_hold(stock1_arr, stock2_arr):
    assert(len(stock1_arr) == len(stock2_arr))

    capital = 1
    stock1_hold = 0.5 / stock1_arr[0]
    stock2_hold = 0.5 / stock2_arr[0]
    capital_arr = []
    for i in range(len(stock1_arr)):
        capital_arr.append(stock1_hold * stock1_arr[i] + stock2_hold * stock2_arr[i])

    return capital_arr
