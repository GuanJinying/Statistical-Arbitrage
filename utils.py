import numpy as np
import pandas as pd
from scipy.special import gamma
from math import sqrt, factorial, exp, log10
from decimal import *
getcontext().prec = 20
from scipy.optimize import minimize 

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

def ou_process_likelihood(params, X):
    n = len(X) - 1
    mu, theta, delta = params
    result = -n/2
    for i in range(n):
        result -= 1/2*np.log(1-exp(-2*theta))
        result -= theta/(delta**2)*(X[i+1] - mu - (X[i] - mu)*exp(-theta))/(1-exp(-2*theta))
    return -result

def OU_process_parameter_estimatior(X, x_0):
    tol = 1e-6
    res = minimize(fun = ou_process_likelihood, x0 = x_0, args = (X), tol = tol, method = 'Nelder-Mead')
    return res

def zeng_formula(n, c, a):
    a = Decimal(a)
    c = Decimal(c)
    temp_result = Decimal(0)
    for i in range(n):
        temp_result += (Decimal(2).sqrt()*a)**Decimal(2*i+1)/Decimal(factorial(2*i+1))*Decimal(gamma((2*i+1)/2))/Decimal(2)
        temp_result -= (a-c/Decimal(2))/Decimal(2).sqrt()*(Decimal(2).sqrt()*a)**Decimal(2*i)/Decimal(factorial(2*i))*Decimal(gamma((2*i+1)/2))
        
    return temp_result

def calculate_optimzal_spread(transaction_cost_perc, accuracy, n):
    left = transaction_cost_perc
    right = 10
    temp = (left + right)/2
    left_result = zeng_formula(n, transaction_cost_perc, left)
    right_result = zeng_formula(n, transaction_cost_perc, right)
    temp_result = zeng_formula(n, transaction_cost_perc, temp)
    temp_accuracy = right - left
    while temp_accuracy >= accuracy:
        temp_check_1 = temp_result * left_result
        temp_check_2 = temp_result * right_result
        if temp_result.compare(0) == 0:
            return temp
        elif temp_check_1.compare(0) == -1:
            right = temp
            temp = (left + right)/2
            temp_accuracy = right - left
            right_result = temp_result
            temp_result = zeng_formula(n, transaction_cost_perc, temp)
        elif temp_check_2.compare(0) == -1:
            left = temp
            temp = (left + right)/2
            temp_accuracy = right - left
            left_result = temp_result
            temp_result = zeng_formula(n, transaction_cost_perc, temp)
        print(f'temp_check_1:{temp_check_1}')
        print(f'temp_check_2:{temp_check_2}')
        print(f'accuracy:{temp_accuracy}')
        print('\n')
    return temp

def get_optimal(transaction_cost_perc, accuracy):
    N_length = [20, 40, 60, 80, 100, 120, 140, 160]
    for i in range(len(N_length)):
        a = calculate_optimzal_spread(transaction_cost_perc, accuracy, N_length[i])
        print(a)

#get_optimal(0.00065, 0.0000001)
