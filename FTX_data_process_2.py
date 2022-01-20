import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from utils import my_KalmanFilter
import numpy as np
import pandas as pd
import pickle
import statsmodels.tsa.stattools as ts
from sklearn.linear_model import LinearRegression
def seperate_data():
    data = pd.read_pickle("FTX_PERP.pkl")
    f_3 = open("selected_pair_90day.pkl", 'rb')
    selected_pair = pickle.load(f_3)
    f_3.close()
    training_stop_pair = selected_pair[int(len(selected_pair)*3/4) + 1]
    training_stop_time = training_stop_pair[0]
    training_data = data.loc[:training_stop_time,:]
    testing_data = data.loc[training_stop_time:,:]
    training_data.to_pickle('FTX_PERP_training.pkl')
    testing_data.to_pickle('FTX_PERP_testing.pkl')
    training_pair = selected_pair[:int(len(selected_pair)*3/4) + 1]
    testing_pair = selected_pair[int(len(selected_pair)*3/4) + 1:]
    f_1 = open('selected_pair_90day_training.pkl', 'wb')
    pickle.dump(training_pair, f_1)
    f_1.close()
    f_2 = open('selected_pair_90day_testing.pkl', 'wb')
    pickle.dump(testing_pair, f_2)
    f_2.close()

# pick out the pairs from the selected pairs we get from FTX_data_process-1.py with larger variance spread
def selected_pair_process(tick):  
    data = pd.read_pickle("data/FTX_PERP_training.pkl")
    data = data.loc[[x for x in data.index if x%(60000*tick) == 0],:]
    selected_pair = pd.read_pickle('data/selected_pair_90day_training.pkl')
    M = len(selected_pair)
    coint_day_period = 90
    timeperiod = 86400000 * coint_day_period
    selected_pair_new = []
    for i in range(M):
        
        pair_temp = selected_pair[i]
        if len(pair_temp) == 1:
            selected_pair_new.append(pair_temp)
            continue

        #calculate spread of each selected pair using Kalman Filter then calculate the variance of spread
        temp_selected_pair = pair_temp[1:]
        temp_start = pair_temp[0] - timeperiod
        temp_end = pair_temp[0]
        temp_data = data.loc[[x for x in data.index if x <= temp_end and x >= temp_start],:]
        temp_variance = np.zeros(len(temp_selected_pair))
        temp_beta = []
        temp_previous_spread = []

        for j in range(len(temp_selected_pair)):
            temp_data_1 = temp_data.loc[:,[temp_selected_pair[j][0], temp_selected_pair[j][1]]].dropna() #Since some data have nan value, we have to drop that and combine it after the calculation
            temp_data1 = temp_data_1.iloc[:,0]
            temp_data2 = temp_data_1.iloc[:,1]
            temp_beta_ = LinearRegression().fit(np.array(temp_data2).reshape(-1,1),np.array(temp_data1)).coef_[0]
            temp_data_1['spread'] = temp_data1 - temp_data2*temp_beta_
            previous_temp_spread_ = temp_data.merge(temp_data_1['spread'], how = 'outer', left_index = True, right_index = True)['spread'] #combine the nan timestamp
            temp_variance[j] = previous_temp_spread_.var()
            temp_beta.append(temp_beta_)
            temp_previous_spread.append(previous_temp_spread_)
        # sort selected pair using variance calculated obove
        temp_df = pd.DataFrame({'variance':temp_variance, 'beta': temp_beta, 'data':temp_previous_spread, 'pair':temp_selected_pair}).sort_values(by = 'variance', ascending = False).reset_index()
        
        # if two selected pairs have intersection like {'SHIT', 'EXH'} and {'SHIT', 'MID'}, then remove the one with smaller variance
        if len(temp_df.index) > 1:
            skip_list = []
            for l in temp_df.index:
                if l in skip_list:
                    continue
                for m in temp_df.index:
                    if m <= l or m in skip_list:
                        continue
                
                    temp_intersect = set(temp_selected_pair[temp_df.at[l,'index']]).intersection(set(temp_selected_pair[temp_df.at[m,'index']]))
                    if len(temp_intersect) > 0:
                        skip_list.append(m)
            temp_df_index = sorted(list(set(temp_df.index).difference(set(skip_list))))
            temp_df = temp_df.loc[temp_df_index,:]
            temp_df.reset_index(drop = True, inplace = True)
        # if we have more than 3 selected pairs then we keep the first 3 seleced pair according to rank by spread variance
        if len(temp_df.index) > 3:
            temp_df = temp_df.iloc[:3,:]
        selected_pair_new.append([pair_temp[0], temp_df['beta'], temp_df['pair'], temp_df['data']])
    
    f = open(f'temp_data/selected_pair_new_{tick}.pkl', 'wb')
    pickle.dump(selected_pair_new, f)
    f.close()
    
# Calculate the spread using Kalman Filter of the selected pairs we get from the function above
def get_spread(rolling_period, tick): 
    coint_day_period = 90
    timeperiod = 86400000 * coint_day_period
    selected_pair_info = pd.read_pickle(f'temp_data/selected_pair_new_{tick}.pkl')
    data = pd.read_pickle('data/FTX_PERP_training.pkl')
    data = data.loc[[x for x in data.index if x%(60000*tick) == 0],:]
    M = len(selected_pair_info)
    spread = []
    for i in range(M):
        temp_pair_info = selected_pair_info[i]
        temp_start = temp_pair_info[0] + 60000*tick
        if temp_start >= data.index[-1]:
            continue
        if len(temp_pair_info) == 1:
            spread.append([temp_start])
            continue
        temp_end = temp_start + int(coint_day_period/3)*86400000
        temp_previous_start = temp_start - timeperiod
        temp_previous_spread = temp_pair_info[3]
        temp_previous_beta = temp_pair_info[1]
        temp_selected_pair = temp_pair_info[2]
        temp_normalize_spread = []
        temp_M = len(temp_selected_pair)
        
        for j in range(temp_M):
            temp_data = data.loc[[x for x in data.index if x >= temp_start and x <= temp_end],:]
            temp_data_1 = temp_data.loc[:,[temp_selected_pair[j][0], temp_selected_pair[j][1]]]
            temp_data1 = temp_data_1.iloc[:,0]
            temp_data2 = temp_data_1.iloc[:,1]
            temp_spread = temp_data1 - temp_previous_beta[j]*temp_data2
            temp_combine_spread = pd.concat([temp_previous_spread[j],temp_spread])
            temp_normalize_spread_ = (temp_combine_spread - temp_previous_spread[j].mean())/temp_previous_spread[j].std()
            temp_normalize_spread_ = temp_normalize_spread_.loc[[x for x in temp_normalize_spread_.index if x >= temp_start]]
            temp_normalize_spread.append(temp_normalize_spread_)
        spread.append([temp_start,temp_selected_pair,temp_normalize_spread, temp_previous_beta])
    f_2 = open(f'temp_data/FTX_spread_{rolling_period}_{tick}.pkl','wb')
    pickle.dump(spread, f_2)
    f_2.close()

def selected_pair_spread_check_stationary(tick):  
    selected_pair_info = pd.read_pickle(f'temp_data/selected_pair_new_{tick}.pkl')
    M = len(selected_pair_info)
    for i in range(M):
        temp_pair_info = selected_pair_info[i]
        temp_start = temp_pair_info[0] + 60000*tick
        if temp_start >= data.index[-1]:
            continue
        if len(temp_pair_info) == 1:
            spread.append([temp_start])
            continue
        temp_previous_spread = temp_pair_info[3]
        temp_selected_pair = temp_pair_info[2]
        temp_M = len(temp_selected_pair)
        temp_p_value = []
        for j in range(temp_M):
            temp_p_value_ = ts.adfuller(temp_previous_spread[j])
            temp_p_value.append(temp_p_value_)
        print(temp_pair_info[0])
        print(temp_selected_pair)
        print(temp_p_value)
    
def spread_modify(rolling_period, tick):
    data = pd.read_pickle('data/FTX_PERP_training.pkl')
    selected_pair_info = pd.read_pickle('temp_data/FTX_spread_{rolling_period}_{tick}.pkl')
    M = len(selected_pair_info)
    for i in range(M):
        temp_pair_info = selected_pair_info[i]
        temp_start = temp_pair_info[0]
        if temp_start >= data.index[-1]:
            continue
        if len(temp_pair_info) == 1:
            spread.append([temp_start])
            continue
        temp_parameter = []
        temp_selected_pair = temp_pair_info[1]
        temp_spread = temp_pair_info[2]
        temp_previous_beta = temp_pair_info[3]
        temp_M = len(temp_selected_pair)
        for j in range(temp_M):
            temp_N = len(temp_spread[j])
            delta = 0.0001
            V_e = 0.1
            mkf = my_KalmanFilter(delta, V_e)
            for k in range(temp_N - 1):
                mkf.update(temp_spread[j].iloc[k], temp_spread[j].iloc[k+1])
                

# selected_pair_info = pd.read_pickle('selected_pair_new_1.pkl')
# get_spread(100, 1)

