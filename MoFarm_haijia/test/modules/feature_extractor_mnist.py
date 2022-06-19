'''
Author: your name
Date: 2022-04-15 17:04:39
LastEditTime: 2022-04-28 16:44:56
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /MoFarm_lvjm/MoFarmBackEnd/src/module/feature_extractor_mnist.py
'''
import sys
sys.path.append('../')
from  api.module_api import *
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose


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
        super(feature_extractor_mnist, self).__init__(project_name, module_name,config)  
        
        # Get cpu or gpu device for training.
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Using {} device".format(self.device))

        self.set_model(Model_Extractor().to(self.device))
        
 


