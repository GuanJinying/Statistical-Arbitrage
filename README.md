# Statistical-Arbitrage on FTX Index Perpetual

It is observed that two index perpetual futures in FTX exchange show strong correlation relationship in the recent two years. There might be opportunities for statistical arbitrage for these index perpetual futures.

In this study, I use ALT-perp, DEFI-perp, DRG-perp, EXCH-perp, MID-perp, PRIV-perp, SHIT-perp and together with BTC future as my trading targets. Since the cointegration relationship
might change from time to time, I decide to use 3-month data to do cointegration tests, trade the pairs picked out from the test within 1 month and roll over the process again.

During the pair selection process, I first check if the price values of the two index perps in one pair are stationary using adfuller test. If the p-values for both indexes are greater than 0.1, I will reject the null hypothesis and accept the pairs.  

There are several problems we need to consider: 1. If we select two pairs like BTC-SHIT and BTC-ALT, then we cannot simply add these two pair in it because if we long BTC-SHIT and short BTC-ALT, we will just long the SHIT and ALT and this circumstance happens always. We need to find the pair that fits our demand most in this case. 

One thought is to calculate the spread Y<sub>t</sub> - &beta;X<sub>t</sub> and pick the one with the most largest variance of the spread. Why? Because if the spread is stationary and spread has a larger variance, then we might have more profits to make than the smaller one. I then use OLS to get the &beta; we want and there is one subtle problem: we need to decide the exogenerous variable and the endogerous variable (I have tried the basic OLS combining adfuller test to compare with conitgeration python package and they show different answers). (Just ignore this for simplicity) After the selection process, I use the maximum likelihood method to estimate the parameters using the loglikelihood function for OU process based on Hu and Long(2007). 

After we get the parameters, we can refer to Zhengqin Zeng & Chi-Guhn Lee's result(2014): Pairs trading: optimal thresholds and profitability. The paper calculated the expectation of the ratio of total profit over the total amount of time for we gain the profit and we get:
<p align="center">
<img width="365" alt="1" src="https://user-images.githubusercontent.com/63221622/150909793-a33fc9d8-1ed0-4698-be36-c684ec9f3378.png">
</p>
After several complex computations, the optimization problem transformed into a equation:
<p align="center">
<img width="298" alt="2" src="https://user-images.githubusercontent.com/63221622/150910109-7c66525d-a5dc-4778-869e-df1ecc5460f0.png">
</p>
where a is the threshold for a standard OU process for maximal profits and c is the transction fee. Then we just need to solve
<p align="center">
<img width="292" alt="3" src="https://user-images.githubusercontent.com/63221622/150910308-ae89a673-8570-4cbe-9bec-2c24224eafc8.png">
</p>
And the calculation is done in my utils file. Then we can set the entering threhsold to be a&delta;/sqrt(2)&theta; + &mu; and &mu; - a&delta;/sqrt(2)&theta; and we can get different thresholds for different pairs and avoid overfitting. (undergoing)

(To be continued)
