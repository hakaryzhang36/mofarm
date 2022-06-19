from  .module_api import *
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose

class datasource_mnist (DataSource):
    def __init__(self,project_name, module_name,config):
        
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


    def set_url(self,url):
        print ('MNISTDataSource.set_url')    

    def get_train_data_labeled(self):
        return self.train_dataloader

    def get_validation_data(self):
        print('MNISTDataSource.get_validation_data')
    def get_test_data(self):
        return self.test_dataloader
        
    def get_source_data_labeled(self):
        print('MNISTDataSource.get_source_data_labeled')
    def get_target_data_unlabeled(self):
        print('MNISTDataSource.get_target_data_unlabeled')



    
