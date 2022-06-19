'''
Author: your name
Date: 2022-04-26 18:11:46
LastEditTime: 2022-04-28 16:45:11
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /MoFarm_jmlv/test/datasource_mnist.py
'''
import sys
sys.path.append('../')
from  api.module_api import *
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose

class datasource_mnist (DataSource):
    def __init__(self,project_name, module_name,config):
        super(datasource_mnist, self).__init__(project_name, module_name,config)      
        # Download training data from open datasets.
        self.training_data = datasets.FashionMNIST(
            root="data",
            train=True,
            download=True,
            transform=ToTensor(),
        )

        # Download test data from open datasets.
        self.test_data = datasets.FashionMNIST(
            root="data",
            train=False,
            download=True,
            transform=ToTensor(),
        )

        self.batch_size = 64

        # Create data loaders.
        self.train_dataloader = DataLoader(self.training_data, batch_size=self.batch_size)
        self.test_dataloader = DataLoader(self.test_data, batch_size=self.batch_size)
   

    def get_train_data_loader(self):
        return self.train_dataloader

    def get_validation_data_loader(self):
        pass
        
    def get_test_data_loader(self):
        return self.test_dataloader
         


    
