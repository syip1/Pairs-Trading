# Pairs-Trading
This is a program that backtests the trading strategy of pairs trading. It takes two similar stocks and varies the proportion of assets put in each stock based on the relative price of the two stocks.  
Currently the following is done:  
<ol>
  <li> Scrape data (through Yahoo Finance) of most of the stocks on the Hong Kong Stock Exchange, with trading volume above a certain threshold. (<em>scrape_stock_data.py</em>) </li>
  <li> Filter the stocks and choose pairs with high correlation throughout the period. (<em>correlation.py</em>) </li>
  <li> Look at these pairs and select ones whose ratio are stationary. (<em>check_relationship.py</em>) </li>
</ol>
It remains to implement the pairs trading strategy on these selected stocks.
