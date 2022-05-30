from torch.utils.data import DataLoader,Dataset
import torch
import pandas 

class EnergyData(Dataset):
    def __init__(self, root_dir, history_len=10, forecast_len=1, interval=5, train=True):
      
        self.history_len = history_len
        self.forecast_len = forecast_len
        self.interval = interval
        train_df = pandas.read_csv(root_dir+'train.csv')
        self.raw_data = train_df[train_df['building_id'].apply(lambda x:x==1)&
                     train_df['meter_re ading'].apply(lambda x:x>0)&
                     train_df['meter'].apply(lambda x:x==0)]
       
        split_index = int(len(self.raw_data)*0.7)
#         print('split_index is ',split_index)
        if(train==True):
            self.raw_data = self.raw_data.values[200:split_index][:,3].astype('float32')
#             print('trainset raw_data size: ', len(self.raw_data))
        else:
            self.raw_data = self.raw_data.values[split_index:][:,3].astype('float32')
#             print('testset raw_data size: ', len(self.raw_data))
        self.len = int((self.raw_data.shape[0]-self.history_len-self.forecast_len)/self.interval)+1
    
    def __getitem__(self, index):
        if(index<self.len):
            x_start = self.interval*index
            y_start = x_start+self.history_len
            x_data = torch.from_numpy(self.raw_data[x_start:x_start+self.history_len])
            y_reg = torch.from_numpy(self.raw_data[y_start:y_start+self.forecast_len]) 
            
            y_future = self.raw_data[y_start:y_start+5]
            if(y_future[0]>x_data[-1] and y_future[1]>y_future[0] and y_future[2]>y_future[1]):
            #if(y_future[0]>x_data[-1] and y_future[1]>x_data[-1] and y_future[2]>x_data[-1]):
                y_cla = torch.tensor(1)
            else:
                y_cla = torch.tensor(0)
            return x_data, (y_reg, y_cla)
        else:
            return None
    
    def __len__(self):
        return self.len
    


class RTTData(Dataset):
    def __init__(self, data_path, history_len=10, forecast_len=1, interval=5, train=True):
    
        self.history_len = history_len
        self.forecast_len = forecast_len
        self.interval = interval
        train_df = pandas.read_csv(data_path)
        self.raw_data = train_df['rtt'].values
       
        split_index = int(len(self.raw_data)*0.7)
#         print('split_index is ',split_index)
        if(train==True):
            self.raw_data = self.raw_data[200:split_index].astype('float32')
#             print('trainset raw_data size: ', len(self.raw_data))
        else:
            self.raw_data = self.raw_data[split_index:].astype('float32')
#             print('testset raw_data size: ', len(self.raw_data))
        self.len = int((self.raw_data.shape[0]-self.history_len-self.forecast_len)/self.interval)
    
    def __getitem__(self, index):
        if(index<self.len):
            x_start = self.interval*index
            y_start = x_start+self.history_len
            x_data = torch.from_numpy(self.raw_data[x_start:x_start+self.history_len])
            y_reg = torch.from_numpy(self.raw_data[y_start:y_start+self.forecast_len]) 
            
            for i in range(len(x_data)):
                if(x_data[i]>1500):
                    x_data_i = 1500
                    
#             print(y_start)
            y_future = self.raw_data[y_start:y_start+5]
#             if(y_future[0]>x_data[-1] and y_future[1]>y_future[0]):
            #if(y_future[0]>x_data[-1] and y_future[1]>x_data[-1] and y_future[2]>x_data[-1]):
            if((y_future[0]+y_future[1])/2 - x_data[-1] >=0.2):
                y_cla = torch.tensor(1)
            else:
                y_cla = torch.tensor(0) 
                
            # x_data size: (batch_size, history_len)
            return x_data, (y_reg, y_cla)
        else:
            return None
    def __len__(self):
        return self.len
    
    
    
class MotorData(Dataset):
    def __init__(self, data_path, history_len=10, forecast_len=1, interval=3, train=True):
    
        self.history_len = history_len
        self.forecast_len = forecast_len
        self.interval = interval
        train_df = pandas.read_csv(data_path)
        self.raw_data = train_df['speed'].values/1000
        split_index = int(len(self.raw_data)*0.7)
        print('split_index is ',split_index)
        if(train==True):
            self.raw_data = self.raw_data[10:split_index].astype('float32')
        else:
            self.raw_data = self.raw_data[split_index:].astype('float32')
        self.len = int((self.raw_data.shape[0]-self.history_len-self.forecast_len)/self.interval)
    
    def __getitem__(self, index):
        if(index<self.len):
            x_start = self.interval*index
            y_start = x_start+self.history_len
            x_data = torch.from_numpy(self.raw_data[x_start:x_start+self.history_len])
            y_reg = torch.from_numpy(self.raw_data[y_start:y_start+self.forecast_len]) 

            y_future = self.raw_data[y_start:y_start+5]
            if((y_future[0]+y_future[1])/2 - x_data[-1] >=0.2):
                y_cla = torch.tensor(1)
            else:
                y_cla = torch.tensor(0) 
                
            # x_data size: (batch_size, history_len)
            return x_data, (y_reg, y_cla)
        else:
            return None

    def __len__(self):
        return self.len