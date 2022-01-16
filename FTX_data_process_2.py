from useful_tool import my_KalmanFilter
import numpy as np
import pandas as pd
import pickle

# pick out the pairs from the selected pairs we get from FTX_data_process-1.py with larger variance spread
def selected_pair_process():  
    data = pd.read_pickle("FTX_PERP.pkl")
    f_3 = open("selected_pair_90day.pkl", 'rb')
    selected_pair = pickle.load(f_3)
    f_3.close()
    M = len(selected_pair)
    coint_day_period = 90
    timeperiod = 86400000 * coint_day_period
    delta = 0.0001
    V_e = 0.1
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
        temp_P = []
        temp_previous_spread = []

        for j in range(len(temp_selected_pair)):
            mkf = my_KalmanFilter(delta = delta, r = V_e)
            temp_data_1 = temp_data.loc[:,[temp_selected_pair[j][0], temp_selected_pair[j][1]]].dropna() #Since some data have nan value, we have to drop that and combine it after the calculation
            temp_data1 = temp_data_1.iloc[:,0]
            temp_data2 = temp_data_1.iloc[:,1]

            # if price of coin_1 is smaller than price of coin_2, then switch coin_1 and coin_2 to make sure coin_1 price is larger than coin_2 price  
            # so to have beta_0 larger than 1
            if temp_data1.iloc[0] < temp_data2.iloc[0]:
                temp_selected_pair_ = temp_selected_pair[j][0]
                temp_selected_pair[j][0] = temp_selected_pair[j][1]
                temp_selected_pair[j][1] = temp_selected_pair_
                temp_data_ = temp_data1
                temp_data1 = temp_data2
                temp_data2 = temp_data1

            temp_spread = []
            for k in range(len(temp_data_1.index)):
                temp_spread_ = mkf.update(temp_data2.iloc[k], temp_data1.iloc[k])
                temp_spread.append(temp_spread_)

            previous_temp_spread_ = pd.DataFrame({'spread':temp_spread,'Timestamp':temp_data_1.index}).set_index('Timestamp')
            previous_temp_spread_.iloc[0] = 0 #Since for the first day we set beta = 0 in KalmanFilter, hence spread will be the price of coin_1 if we don't modify it
            previous_temp_spread_ = temp_data.merge(previous_temp_spread_, how = 'outer', left_index = True, right_index = True)['spread'] #combine the nan timestamp
            temp_variance[j] = previous_temp_spread_.var()
            temp_beta.append(mkf.beta)
            temp_P.append(mkf.P)
            temp_previous_spread.append(previous_temp_spread_)
        
        # sort selected pair using variance calculated obove
        temp_df = pd.DataFrame({'variance':temp_variance, 'beta': temp_beta, 'P':temp_P, 'data':temp_previous_spread, 'pair':temp_selected_pair}).sort_values(by = 'variance', ascending = False).reset_index()
        
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
        selected_pair_new.append([pair_temp[0], temp_df['beta'], temp_df['P'], temp_df['pair'], temp_df['data']])
    
    f = open('selected_pair_new.pkl', 'wb')
    pickle.dump(selected_pair_new, f)
    f.close()

# Calculate the spread using Kalman Filter of the selected pairs we get from the function above
def get_spread(): 
    coint_day_period = 90
    timeperiod = 86400000 * coint_day_period
    delta = 0.0001
    V_e = 0.1
    f = open('selected_pair_new.pkl', 'rb')
    selected_pair_info = pickle.load(f)
    f.close()
    f_1 = open('FTX_PERP.pkl', 'rb')
    data = pickle.load(f_1)
    f_1.close()
    M = len(selected_pair_info)
    spread = []
    for i in range(M):
        print(f'M:{i}')
        temp_pair_info = selected_pair_info[i]
        temp_start = temp_pair_info[0] + 60000
        if(len(temp_pair_info)) == 1:
            spread.append([temp_start])
            continue
        temp_end = temp_start + int(coint_day_period/3)*86400000
        temp_previous_start = temp_start - timeperiod
        temp_previous_spread = temp_pair_info[4]
        temp_previous_beta = temp_pair_info[1]
        temp_previous_P = temp_pair_info[2]
        temp_selected_pair = temp_pair_info[3]
        temp_normalize_spread = []
        temp_M = len(temp_selected_pair)
        temp_beta = []
        
        for j in range(temp_M):
            print(f'temp_M:{j}')
            temp_data = data.loc[[x for x in data.index if x >= temp_start and x <= temp_end],:]
            print(list(temp_selected_pair[j]))
            temp_data = temp_data.loc[:,list(temp_selected_pair[j])]
            temp_N = len(temp_data.index)
            mkf = my_KalmanFilter(delta = delta, r = V_e)
            mkf.P = temp_previous_P[j]
            mkf.beta = temp_previous_beta[j]
            temp_spread = []
            temp_beta_ = []
            for k in range(temp_N):
                temp_spread_ = mkf.update(temp_data.iloc[k,1], temp_data.iloc[k,0])
                temp_spread.append(temp_spread_)
                temp_beta_.append(mkf.beta)
            temp_time = data.index[[x for x in range(len(data.index)) if data.index[x] >= temp_start and data.index[x] <= temp_end]]
            temp_combine_spread = pd.concat([pd.DataFrame({'Timestamp':temp_previous_spread[j].index, 'spread':temp_previous_spread[j].values}).set_index('Timestamp'),pd.DataFrame({'Timestamp': temp_time,'spread':temp_spread}).set_index('Timestamp')])
            rolling_period = 100
            temp_normalize_spread_ = (temp_combine_spread - temp_combine_spread.rolling(rolling_period).mean())/temp_combine_spread.rolling(rolling_period).std()
            temp_normalize_spread_ = temp_normalize_spread_.loc[[x for x in temp_normalize_spread_.index if x >= temp_start]]
            temp_normalize_spread.append(temp_normalize_spread_)
            
            temp_time_1 = data.index[[x for x in range(len(data.index)) if data.index[x] >= temp_start and data.index[x] <= temp_end]]
            temp_beta.append(pd.DataFrame({'Timestamp': temp_time_1, 'beta':temp_beta_}).set_index('Timestamp'))
        
        spread.append([temp_start,temp_selected_pair,temp_normalize_spread, temp_beta])
    f_2 = open('FTX_spread.pkl','wb')
    pickle.dump(spread, f_2)
    f_2.close()

selected_pair_process()
get_spread()


