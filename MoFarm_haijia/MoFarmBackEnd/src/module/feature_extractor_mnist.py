'''
Author: your name
Date: 2022-04-15 17:04:39
LastEditTime: 2022-04-15 17:04:39
LastEditors: your name
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /MoFarm_lvjm/MoFarmBackEnd/src/module/feature_extractor_mnist.py
'''
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose
from .module_api import *


class Model_Extractor(nn.Module):
    def __init__(self):
        super(Model_Extractor, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU()
            #nn.Linear(512, 10)
        )

        #for param in self.parameters():
        #    param.requires_grad = False

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits


class feature_extractor_mnist(FeatureExtractor):   
    def __init__(self, project_name, module_name,config):
        self.data_source = None
        # Get cpu or gpu device for training.
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Using {} device".format(device))
        self.model = Model_Extractor().to(device)
        self.project_name = project_name
        self.config = config
        #print(self.model)

    def link(self, module):
        if (module.__class__.__bases__[0].__name__=="DataSource"):
            print ('------->link from datasource to feature extractor')
            self.data_source = module 

    def get_data_source (self):
        return self.data_source

    def get_feature(self):
        print('Not implemented ：FeatureExtractor.get_feature')
    def get_model(self):
        return self.model
    def save_model(self):
        if self.config.__contains__("model"):
            model_path = self.config["model"]
            print ("saving model SoFuseBackEnd/config/models/%s " %model_path)
            torch.save(self.model.state_dict(), ('SoFuseBackEnd/config/models/%s' %model_path))

        else:
            print("no matching model !")        
    def load_model(self):
        if self.config.__contains__("model"):
            model_path = self.config["model"]
            print ("saving model SoFuseBackEnd/config/models/%s " %model_path)
            self.model.load_state_dict(torch.load('SoFuseBackEnd/config/models/%s' %model_path))
        else:
            print("no matching model !") 
       
    def freeze_model(self):
        for param in self.model.parameters():
            param.requires_grad = False
    def unfreeze_model(self):
        for param in self.model.parameters():
            param.requires_grad = True