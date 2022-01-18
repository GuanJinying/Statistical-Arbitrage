# Statistical-Arbitrage on FTX Index Perpetual

It is observed that two index perpetual futures in FTX exchange show strong correlation relationship in the recent two years. Therefore there might be opportunities for 
statistical arbitrage for these index perpetual futures.

In this study, I use ALT-perp, DEFI-perp, DRG-perp, EXCH-perp, MID-perp, PRIV-perp, SHIT-perp and together with BTC future as my trading targets. Since the cointegration relationship
might change from time to time, I decide to use 3-month data to do cointegration tests, trade the pairs picked out from the test within 1 month and roll over the process again.

During the pair selection process, I first check if the price values of the two index perps in one pair are stationary using adfuller test. If the p-values for both indexes are greater than 0.1, I will reject the null hypothesis and accept the pairs. 

After that, I use kalman filter to predict &beta; for Y<sub>t</sub> = &beta;<sub>t</sub> X<sub>t</sub> + &epsilon;<sub>t</sub> and &beta;<sub>t</sub> = &beta;<sub>t-1</sub> + w<sub>t</sub> where Y<sub>t</sub> is the price of asset 1 at time t, X<sub>t</sub> is the price of asset 2, &epsilon;<sub>t</sub> is measurement uncertainty following independent identical normal distribution N(0,r) and w<sub>t</sub> is the prediction uncertainty folowing normal distribution N(0,&delta;/(1-&delta;)).   

There are several problems we need to consider: 1. If we select two pairs like BTC-SHIT and BTC-ALT, then we cannot simply add these two pair in it because if we long BTC-SHIT and short BTC-ALT, we will just long the SHIT and ALT and this circumstance happens always. We need to find the pair that fits our demand most in this case. (undergoing)

One thought is to calculate the spread Y<sub>t</sub> - &beta;X<sub>t</sub> and pick the one with the most largest variance of the spread. Why? Because if the spread is stationary and spread has a larger variance, then we might have more profits to make than the smaller one. However, since we are using kalman Filter and it takes time to converge to the eal spread we want. 

Another thought is to use OLS to get the &beta; we want and there is problem: First we need to dicide the exogenerous variable and the endogerous variable (I have tried the basic OLS combining adfuller test to compare with conitgeration pythn package and they shows different answers). Second, it will lead to omitted variable bias. We may use ECM model to strip out the error term. 

If we can finished the selection step, then we can go to the signal construction part. This part is not yet started. One thought is to use the OU process to modify the spread we get. According to Elliott et al. (2005), they provide a solid method called Shumway and Stoffer smoother approach to get the parameter A, B, C, D for model X<sub>t+1</sub> = A + BX<sub>t</sub> + C&epsilon;<sub>t+1</sub> and Y<sub>t</sub> = X<sub>t</sub> + Dw<sub>t</sub>. Then we can use the first passing time for the OU process to calculate the average profits per time unit and get the optimla threshold for each pair each 3-month period. Then we can use this threhsold to trade in the next month for these pairs.

(To be continued)
