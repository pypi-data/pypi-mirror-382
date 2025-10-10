import math
import numpy as np

def relu(x):
    if x >= 0:
        return x
    else:
        return 0


def relu_derivative(x):
    if x >= 0:
        return 1
    else:
        return 0


def tanh(x):
    return math.tanh(x)


def tanh_derivative(x):
    t = math.tanh(x)
    return 1 - t * t


def leaky_relu(x, alpha=0.01):
    if x >= 0:
        return x
    else:
        return alpha * x


def leaky_relu_derivative(x, alpha=0.01):
    if x >= 0:
        return 1
    else:
        return alpha

def sigmoid(x):
    return 1 / (1 + math.e ** (-x))

def sigmoid_derivative(x):
    s = sigmoid(x)
    return s * (1 - s)

def softplus(x):
    return math.log(1 + math.exp(x))


def softplus_derivative(x):
    # Softplus 的导数正好等于 Sigmoid 函数
    return sigmoid(x)


def selu(x, alpha=1.6732632423543772, lambda_=1.0507009873554805):
    if x > 0:
        return lambda_ * x
    else:
        return lambda_ * (alpha * (math.exp(x) - 1))


def selu_derivative(x, alpha=1.6732632423543772, lambda_=1.0507009873554805):
    if x > 0:
        return lambda_
    else:
        return lambda_ * alpha * math.exp(x)

def linear(x):
    return x

def linear_derivative(x):
    return 1

def softmax(i, x):
    sum = 0
    for index in range(len(x)):
        sum += np.exp(x[index])
    return np.exp(x[i]) / sum

__all__ = ['relu', 'relu_derivative', 'tanh', 'tanh_derivative', 'leaky_relu', 'leaky_relu_derivative'
    , 'sigmoid', 'softplus', 'softplus_derivative', 'selu', 'selu_derivative', 'linear', 'linear_derivative',
           'softmax']
