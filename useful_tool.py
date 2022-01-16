import numpy as np
import pandas as pd

class my_KalmanFilter():
    def __init__(self, delta, r):
        self.beta = np.zeros(2)
        self.P = np.zeros((2,2)) #variance of beta
        self.Q = delta/(1-delta) * np.eye(2) # prediction uncertainty
        self.R = r # measurement uncertainty

    def update(self,x_new,y_new):
        #calculate the prediction
        beta_hat = self.beta
        P_hat = self.P + self.Q
        #modify the prediction from the measurement
        H = np.array([x_new,1])
        K = P_hat.dot(H.T) /(H.dot(P_hat.dot(H.T)) + self.R)
        z = y_new
        z_hat = H.dot(beta_hat)
        beta = beta_hat + K.dot(z-z_hat)
        self.beta = beta
        self.P = (np.eye(2) - K.dot(H)).dot(P_hat)
        return z-z_hat


def hurst(ts):
    lags = range(2,100)
    tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]
    poly = polyfit(log(lags), log(tau), 1)
    return poly[0]*2.0

# def halflife(df, col_name):
    
