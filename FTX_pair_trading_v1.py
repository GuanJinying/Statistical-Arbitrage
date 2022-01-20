import pandas as pd
import numpy as np
import pickle
import logging
from datetime import datetime
import math
import matplotlib.pyplot as plt

file1 = open("FTX_pair_trading_V1.log", "w")
file1.close()
logging.basicConfig(level = logging.INFO, filename = 'FTX_pair_trading_V1.log', filemode = 'a', format = '%(message)s')

class pair_trading_strategy():
    def __init__(self, data_file_name, spread_data_file_name, initial_amount, trading_fee_percent, maximum_leverage_ratio, normal_leverage_ratio, coint_day_period, enter_spread, close_spread, tick):
        self.initial_amount = initial_amount
        self.account = initial_amount
        self.account_history = []
        self.trading_fee_percent = trading_fee_percent
        self.maximum_leverage_ratio = maximum_leverage_ratio
        self.normal_leverage_ratio = normal_leverage_ratio
        self.coint_day_period = coint_day_period
        self.position_value = 0
        self.position_value_history = []
        self.leverage_ratio = 0
        self.leverage_ratio_history = []
        self.sub_account = []
        self.sub_position_value = []
        self.peak_value = initial_amount
        self.maximum_drawdown = 0
        self.enter_spread = enter_spread
        self.close_spread = close_spread
        self.beta = []
        
        timeperiod = 86400000 * coint_day_period 
        self.tick = tick
        self.data = pd.read_pickle(data_file_name)
        self.data = self.data.loc[[x for x in self.data.index if x%(60000*tick) == 0],:]
        self.data = self.data.loc[[x for x in self.data.index if x >= (self.data.index[0] + timeperiod + 60000*tick)],:]
        self.spread = pd.read_pickle(spread_data_file_name)
        self.position = np.zeros(len(self.data.columns))
        self.current_price = np.zeros(len(self.data.columns))
        self.previous_price = np.zeros(len(self.data.columns))
        self.current_pair_spread = []
        self.coin_list = []
        self.current_spread = []
        self.spread_index = 0
        self.M = 0
        
    def sub_account_cash(self):
        number_of_pairs = len(self.coin_list)
        sub_account_cash = self.account/number_of_pairs
        self.sub_account = np.array([sub_account_cash]*number_of_pairs)
    
    def transaction_cost(self, previous_position, next_position):
        amount = np.sum(np.multiply(np.absolute(previous_position - next_position), self.current_price))*self.trading_fee_percent
        return amount

    def update_sub_account(self):
        if len(self.current_pair_spread) != 1:
            self.coin_list = self.current_pair_spread[1]
            self.sub_position_value = np.zeros(len(self.coin_list))
            self.sub_account_cash()
            self.current_spread = self.current_pair_spread[2]
            self.M = len(self.coin_list)
            self.beta = self.current_pair_spread[3]
        if len(self.current_pair_spread) == 1:
            self.coin_list = []
            self.sub_position_value = []
            self.sub_account = []
            self.current_spread = []
            self.M = 0
            self.beta = []

    def marking_to_market(self):
        for j in range(self.M):
            coin_1 = self.coin_list[j][0]
            coin_2 = self.coin_list[j][1]
            coin_1_index = list(self.data.columns).index(coin_1)
            coin_2_index = list(self.data.columns).index(coin_2)
            self.sub_account[j] += (self.current_price[coin_1_index] - self.previous_price[coin_1_index])*self.position[coin_1_index] + (self.current_price[coin_2_index] - self.previous_price[coin_2_index])*self.position[coin_2_index]
            self.sub_position_value[j] = self.current_price[coin_1_index]*abs(self.position[coin_1_index]) + self.current_price[coin_2_index]*abs(self.position[coin_2_index])
        self.account += np.sum(np.multiply(self.current_price - self.previous_price, self.position))
        self.position_value = np.sum(np.multiply(self.current_price, np.absolute(self.position)))
        self.leverage_ratio = self.position_value/self.account
        if self.account > self.peak_value:
            self.peak_value = self.account
        drawdown = (self.peak_value - self.account)/self.peak_value*100
        if drawdown > self.maximum_drawdown:
            self.maximum_drawdown = drawdown

    def log(self, i, text):
        pass
        #logging.info(f"{self.data.index[i]} {text}")

    # change coin_list every month and close all positions 
    def change_coin_list(self, i):
        if self.spread[self.spread_index][0] + int(self.coint_day_period/3)*86400000 < self.data.index[i]:
            self.spread_index += 1
            self.current_pair_spread = self.spread[self.spread_index]
            next_position = np.zeros(len(self.data.columns))
            self.account -= self.transaction_cost(self.position, next_position)
            self.position = np.copy(next_position)
            self.position_value = 0
            self.leverage_ratio = 0
            self.log(i, f'Change coin list.')
            if len(self.current_pair_spread) == 1:
                self.update_sub_account()
            else:
                self.log(i, f'coin list:{[x for x in self.current_pair_spread[1]]}')
                self.update_sub_account()

    def enter_market(self, coin_1_index, coin_2_index, signal_1, signal_2, i, j):
        temp_position = np.copy(self.position)
        coin_1_price = self.current_price[coin_1_index]
        coin_2_price = self.current_price[coin_2_index]
        temp_position_1 = min(self.sub_account[j]/coin_1_price, abs(self.sub_account[j]/(self.beta[j]*coin_2_price)))
        position_1 = math.floor(temp_position_1*100*self.normal_leverage_ratio/2)/100.0*signal_1
        position_2 = math.floor(abs(position_1)*self.beta[j]*100)/100.0*signal_2
        if self.beta[j] < 0:
            position_2 = position_2*(-1)
        temp_position[coin_1_index] = position_1
        temp_position[coin_2_index] = position_2
        self.sub_position_value[j] = abs(position_1)*coin_1_price + abs(position_2)*coin_2_price
        self.sub_account[j] -= self.transaction_cost(self.position, temp_position)
        self.account -= self.transaction_cost(self.position, temp_position)
        self.position = np.copy(temp_position)
        coin_1 = self.data.columns[coin_1_index]
        coin_2 = self.data.columns[coin_2_index]
        self.log(i, f"Enter market, spread:{self.current_spread[j].loc[self.data.index[i]]}, {coin_1}_position: {position_1}, {coin_2}_position: {position_2}")

    def close_position(self, coin_1_index, coin_2_index, i, j):
        temp_position = np.copy(self.position)
        temp_position[coin_1_index] = 0
        temp_position[coin_2_index] = 0
        self.sub_position_value[j] = 0
        self.sub_account[j] -= self.transaction_cost(self.position, temp_position)
        self.account -= self.transaction_cost(self.position, temp_position)
        self.position = np.copy(temp_position)
        coin_1 = self.data.columns[coin_1_index]
        coin_2 = self.data.columns[coin_2_index]
        self.log(i, f"Close position for {coin_1} and {coin_2}, spread:{self.current_spread[j].loc[self.data.index[i]]}, {coin_1}_position: {self.position[coin_1_index]}, {coin_2}_position: {self.position[coin_2_index]}")

    def account_summary(self, i):
        self.previous_price = np.copy(self.current_price)
        self.position_value = np.sum(np.multiply(self.current_price, np.absolute(self.position)))
        self.leverage_ratio = self.position_value/self.account
        self.account_history.append(self.account)
        self.position_value_history.append(self.position_value)
        self.leverage_ratio_history.append(self.leverage_ratio)
        self.log(i, f'Account Summary, account_value:{self.account}, Sub_account:{self.sub_account}, coin_list:{list(self.data.columns)}, position:{self.position}, price:{self.current_price}, leverage_ratio:{self.leverage_ratio}')

    def backtest_result(self):
        logging.info('\n---------------------------------------Backtest Summary---------------------------------------\n')
        logging.info(f'Initial Portfolio Value: {self.initial_amount}')
        logging.info(f'Final Portfolio Value: {self.account}')
        percentage_pnl_return = (self.account - self.initial_amount)/self.initial_amount*100
        number_of_days = (datetime.fromtimestamp(int(self.data.index[-1]/1000)).date() - datetime.fromtimestamp(int(self.data.index[0]/1000)).date()).days
        percentage_annualized_pnl_return = percentage_pnl_return/(number_of_days/365)
        logging.info('Annualised Pnl return: {:.2f}%'.format(percentage_annualized_pnl_return))
        #calculate daily sharpe ratio
        portfolio = pd.DataFrame({'time':self.data.index, 'portfolio':self.account})
        portfolio1 = portfolio.copy()
        portfolio1['time'] = pd.to_datetime(portfolio['time'].apply(lambda x: int(x/1000)), unit = 's')
        portfolio1.set_index('time', inplace = True)
        plt.figure(figsize=(16, 9), dpi=80)
        portfolio1.plot(title = 'Portfolio value from 2020 to 2022')
        plt.show()
        plt.savefig('Portfolio_value.png')
        portfolio.set_index('time', inplace = True)
        start_ = portfolio.index[0]%86400000
        portfolio2 = portfolio.loc[[x for x in portfolio.index if x%86400000 == start_],:]/portfolio['portfolio'][0]
        pnl_1 = portfolio2.shift() - portfolio2
        sharpe_ratio = pnl_1.mean()/pnl_1.std()
        logging.info('Daily Sharpe ratio: {:.2f}'.format(sharpe_ratio))
        logging.info('Maximum Drawdown: {:.2f}%'.format(self.maximum_drawdown))

    def fit(self):
        N = len(self.data.index)
        self.current_pair_spread = self.spread[self.spread_index]
        self.update_sub_account()
        for i in range(N):
            self.current_price = np.nan_to_num(list(self.data.iloc[i,:]))
            self.marking_to_market()
            self.change_coin_list(i)
            for j in range(self.M):
                coin_1 = self.coin_list[j][0]
                coin_2 = self.coin_list[j][1]
                coin_1_index = list(self.data.columns).index(coin_1)
                coin_2_index = list(self.data.columns).index(coin_2)
                if pd.isnull(self.current_spread[j].loc[self.data.index[i]]):
                    continue
                if self.current_spread[j].loc[self.data.index[i]] >= self.enter_spread and self.position[coin_1_index] == 0 and self.position[coin_2_index] == 0:
                    self.enter_market(coin_1_index, coin_2_index, -1, 1, i, j)
                elif self.current_spread[j].loc[self.data.index[i]] <= self.enter_spread*(-1) and self.position[coin_1_index] == 0 and self.position[coin_2_index] == 0:
                    self.enter_market(coin_1_index, coin_2_index, 1, -1, i, j)
                elif abs(self.current_spread[j].loc[self.data.index[i]]) <= self.close_spread and self.position[coin_1_index] != 0 and self.position[coin_2_index] != 0:
                    self.close_position(coin_1_index, coin_2_index, i, j)
            self.account_summary(i)
        #self.backtest_result()

# if __name__ == "__main__":
#     enter_spread = 3
#     close_spread = 0.1
#     strategy1 = pair_trading_strategy('FTX_PERP.pkl', 'FTX_spread_500.pkl', 100000, 0.00065, 4, 1, 90, enter_spread, close_spread)
#     strategy1.fit()

    