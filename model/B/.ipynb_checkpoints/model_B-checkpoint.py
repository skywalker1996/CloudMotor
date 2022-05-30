import torch
from torch import nn
import numpy as np
from BasicModule import *
import os
import torch.nn.functional as F

class Model_B(BasicModule):
    def __init__(self, name, history_len=10, forecast_len=1):
        super(Model_B, self).__init__()
        self.name = name
        self.seq_len = history_len
        self.forecast_len = forecast_len
        self.LSTM_reg = nn.LSTM(input_size=1, hidden_size=16, num_layers=1, batch_first=True)
#         self.LSTM_cla = nn.LSTM(input_size=1, hidden_size=16, num_layers=1, batch_first=True)
        self.linear_reg_1 = nn.Linear(16*self.seq_len,10)
        self.linear_reg_2 = nn.Linear(10,self.forecast_len)
#         self.linear_cla_1 = nn.Linear(16*self.seq_len,10)
#         self.linear_cla_2 = nn.Linear(10,2)
    def forward(self, x):
        # out = (batch, seq_len, num_directions * hidden_size)
        # hidden = (hn, cn)，维度同上
        x, hidden = self.LSTM_reg(x)
        x = x.reshape(-1, 16*self.seq_len)
        x_reg = self.linear_reg_1(x)
        x_reg = self.linear_reg_2(x_reg)
#         x_cla = self.linear_cla_1(x)
#         x_cla = self.linear_cla_2(x_cla)
#         x_cla = F.softmax(x_cla, dim=1)
#         return (x_reg, x_cla)
        return x_reg

