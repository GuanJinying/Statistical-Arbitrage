# Statistical-Arbitrage on FTX Index Perpetual

It is observed that two index perpetual futures in FTX exchange show strong correlation relationship in the recent two years. Therefore there might be opportunities for 
statistical arbitrage for these index perpetual futures.

In this study, I use ALT-perp, DEFI-perp, DRG-perp, EXCH-perp, MID-perp, PRIV-perp, SHIT-perp and together with BTC future as my trading targets. Since the cointegration relationship
might change from time to time, I decide to use 3-month data to do cointegration tests, trade the pairs picked out from the test within 1 month and roll over the process again.

During the pair selection process, I first check if the price values of the two index perps in one pair are stationary using adfuller test. If the p-values for both indexes are greater than 0.1, I will reject the
null hypothesis and accept the pairs. After that, I use kalman filter to predict beta for Y<sub>t</sub> = &beta;<sub>t</sub> X<sub>t</sub> + &epsilon;<sub>t</sub>
