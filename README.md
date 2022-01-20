# Statistical-Arbitrage on FTX Index Perpetual

It is observed that two index perpetual futures in FTX exchange show strong correlation relationship in the recent two years. There might be opportunities for statistical arbitrage for these index perpetual futures.

In this study, I use ALT-perp, DEFI-perp, DRG-perp, EXCH-perp, MID-perp, PRIV-perp, SHIT-perp and together with BTC future as my trading targets. Since the cointegration relationship
might change from time to time, I decide to use 3-month data to do cointegration tests, trade the pairs picked out from the test within 1 month and roll over the process again.

During the pair selection process, I first check if the price values of the two index perps in one pair are stationary using adfuller test. If the p-values for both indexes are greater than 0.1, I will reject the null hypothesis and accept the pairs.  

There are several problems we need to consider: 1. If we select two pairs like BTC-SHIT and BTC-ALT, then we cannot simply add these two pair in it because if we long BTC-SHIT and short BTC-ALT, we will just long the SHIT and ALT and this circumstance happens always. We need to find the pair that fits our demand most in this case. 

One thought is to calculate the spread Y<sub>t</sub> - &beta;X<sub>t</sub> and pick the one with the most largest variance of the spread. Why? Because if the spread is stationary and spread has a larger variance, then we might have more profits to make than the smaller one. I then use OLS to get the &beta; we want and there is one subtle problem: we need to decide the exogenerous variable and the endogerous variable (I have tried the basic OLS combining adfuller test to compare with conitgeration python package and they show different answers). (Just ignore this for simplicity)

If we can finished the selection step, then we can go to the signal construction part. One thought is to use the OU process to modify the spread we get. According to Elliott et al. (2005), they provide a solid method called Shumway and Stoffer smoother approach to get the parameter A, B, C, D for model X<sub>t+1</sub> = A + BX<sub>t</sub> + C&epsilon;<sub>t+1</sub> and Y<sub>t</sub> = X<sub>t</sub> + Dw<sub>t</sub>. Then we can use the first passing time for the OU process to calculate the average profits per time unit and get the optimal threshold for each pair each 3-month period. Then we can use this threhsold to trade in the next month for these pairs. (Undergoing)

New problems arose: According to the paper, the first passage time for OU process with the largest probability is 
<img width="965" alt="formular" src="https://user-images.githubusercontent.com/63221622/150321575-2d20c407-ef8f-4299-bca5-f72da0284832.png">
However, the graph pf this function is like:
<img width="171" alt="average_time" src="https://user-images.githubusercontent.com/63221622/150321590-93ba2ab3-b086-4023-9e1e-7430c9727eb0.png">
where I cannot find the maximal value. Need to go through the theory behind the first passage time.

(To be continued)
