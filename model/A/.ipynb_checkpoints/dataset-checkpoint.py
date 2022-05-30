from torch.utils.data import DataLoader,Dataset
import torch
import pandas 
import numpy as np
  
class MotorData(Dataset):
    def __init__(self, data_path, train=True):
    
        train_df = pandas.read_csv(data_path)
        self.raw_data = train_df 
        split_index = int(len(self.raw_data)*0.7)
        if(train==True):
            self.raw_data = self.raw_data[0:split_index].astype('float32')
        else:
            self.raw_data = self.raw_data[split_index:].astype('float32')
        self.len = len(self.raw_data)
    
    def __getitem__(self, index):
        if(index<self.len):
            x = torch.from_numpy(np.array(self.raw_data.iloc[index][0:2]))
            label = torch.from_numpy(np.array(self.raw_data.iloc[index][2]/100)).unsqueeze(-1)
            
            return x, label
        else:
            return None
        
    def __len__(self):
        return self.len