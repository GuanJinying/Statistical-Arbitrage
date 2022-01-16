import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy as np
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import pandas as pd
import statsmodels.tsa.stattools as ts
import pickle
from time import sleep

data = pd.read_pickle('FTX_PERP.pkl')
coint_day_period = 90
timeperiod = 86400000 * coint_day_period 
N = len(data.index)
n = len(data.columns)
temp_1 = data.index[0]
select_pair = []
while temp_1 < data.index[N-1]:

    temp_2 = temp_1 + timeperiod
    temp_data = data.loc[temp_1:temp_2,:]
    temp_1 = temp_1 + int(coint_day_period/3)*86400000 
    output_1 = [temp_2]
    for i in range(n):
        for j in range(i+1, n):
            array = temp_data.loc[:,[temp_data.columns[i],temp_data.columns[j]]]
            array.dropna(inplace = True)
            if array.empty == True:
                continue
            array1 = array[temp_data.columns[i]]
            array2 = array[temp_data.columns[j]]  
            adf_1 = ts.adfuller(array1)[1]    
            adf_2 = ts.adfuller(array2)[1]
            if adf_1 < 0.1 or adf_2 < 0.1:
                continue
            
            coint_1 = ts.coint(array1, array2)[1]
            if coint_1 < 0.05:
                output_1.append([temp_data.columns[i],temp_data.columns[j]])
            
    select_pair.append(output_1)
    print(select_pair)
    print('\n')

f_1 = open(f"selected_pair_{coint_day_period}day.pkl", 'wb')
pickle.dump(select_pair,f_1)
f_1.close()