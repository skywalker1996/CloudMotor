import torch
from torch import nn
import numpy as np
import os
import torch.nn.functional as F

class Model_A(nn.Module):
    def __init__(self, name):
        super(Model_A,self).__init__()
        
        self.layer_1=nn.Sequential(
                nn.Linear(in_features=2,out_features=8,bias=True),
                # nn.BatchNorm1d(8),
                nn.ReLU())
        self.layer_2=nn.Sequential(
                nn.Linear(in_features=8,out_features=4,bias=True),
                # nn.BatchNorm1d(4),
                nn.ReLU())
        self.layer_3=nn.Sequential(
                nn.Linear(in_features=4,out_features=1,bias=True)
                )
        
    def forward(self,x):
        fc1=self.layer_1(x)
        fc2=self.layer_2(fc1)
        output=self.layer_3(fc2)
        return output

# class Model_A(nn.Module):
#     def __init__(self, name):
#         super(Model_A,self).__init__()
#         self.name = name
#         self.bn = nn.BatchNorm1d(2)
#         self.layer_1 = nn.Linear(in_features=2,out_features=1,bias=True)
        
#     def forward(self,x):
#         output=self.layer_1(self.bn(x))
#         return output
