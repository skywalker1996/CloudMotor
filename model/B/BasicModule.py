import torch as t
import os 

class BasicModule(t.nn.Module):
    """
    封装了nn.Module，主要提供save和load两个方法
    """

    def __init__(self):
        super(BasicModule,self).__init__()
#       self.model_name = str(type(self)) # 模型的默认名字

    def load(self, path):
        """
        可加载指定路径的模型
        """
        self.load_state_dict(t.load(path))

    def save(self, epoch=None):
        """
        保存模型，默认使用“模型名字+epoch”作为文件名，
        """
        folder = './checkpoints/' + self.name + '/'
        if(not os.path.exists(folder)):
            os.mkdir(folder)
        name = folder + self.name + '_epoch_'+str(epoch)
        t.save(self.state_dict(), name)
        return name