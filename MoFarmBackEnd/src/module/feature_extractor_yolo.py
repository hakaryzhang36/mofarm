# -*- coding:UTF-8 -*-
from module_api import *
from DataSource_YOLO import DataSource_YOLO
from collections import OrderedDict
import numpy as np
import torch
import os
import torch.nn as nn
from yolov4.CSPdarknet import darknet53
from yolov4.yolo_training import weights_init
from yolov4.yolo4 import *
from django.conf import settings

#---------------------------------------------------#
#   yolo_body
#---------------------------------------------------#
class Model_Extractor(nn.Module):
    def __init__(self, num_anchors, num_classes):
        super(Model_Extractor, self).__init__()
        #   生成CSPdarknet53的主干模型
        #   获得三个有效特征层，他们的shape分别是：
        #   52,52,256
        #   26,26,512
        #   13,13,1024
        self.backbone = darknet53(None)

        self.conv1 = make_three_conv([512,1024],1024)
        self.SPP = SpatialPyramidPooling()
        self.conv2 = make_three_conv([512,1024],2048)

        self.upsample1 = Upsample(512,256)
        self.conv_for_P4 = conv2d(512,256,1)
        self.make_five_conv1 = make_five_conv([256, 512],512)

        self.upsample2 = Upsample(256,128)
        self.conv_for_P3 = conv2d(256,128,1)
        self.make_five_conv2 = make_five_conv([128, 256],256)

        # 3*(5+num_classes) = 3*(5+20) = 3*(4+1+20)=75
        final_out_filter2 = num_anchors * (5 + num_classes)
        self.yolo_head3 = yolo_head([256, final_out_filter2],128)

        self.down_sample1 = conv2d(128,256,3,stride=2)
        self.make_five_conv3 = make_five_conv([256, 512],512)

        # 3*(5+num_classes) = 3*(5+20) = 3*(4+1+20)=75
        final_out_filter1 =  num_anchors * (5 + num_classes)
        self.yolo_head2 = yolo_head([512, final_out_filter1],256)

        self.down_sample2 = conv2d(256,512,3,stride=2)
        self.make_five_conv4 = make_five_conv([512, 1024],1024)

        # 3*(5+num_classes)=3*(5+20)=3*(4+1+20)=75
        final_out_filter0 =  num_anchors * (5 + num_classes)
        self.yolo_head1 = yolo_head([1024, final_out_filter0],512)


    def forward(self, x):
        #  backbone
        x2, x1, x0 = self.backbone(x)

        # 13,13,1024 -> 13,13,512 -> 13,13,1024 -> 13,13,512 -> 13,13,2048 
        P5 = self.conv1(x0)
        P5 = self.SPP(P5)
        # 13,13,2048 -> 13,13,512 -> 13,13,1024 -> 13,13,512
        P5 = self.conv2(P5)

        # 13,13,512 -> 13,13,256 -> 26,26,256
        P5_upsample = self.upsample1(P5)
        # 26,26,512 -> 26,26,256
        P4 = self.conv_for_P4(x1)
        # 26,26,256 + 26,26,256 -> 26,26,512
        P4 = torch.cat([P4,P5_upsample],dim=1)
        # 26,26,512 -> 26,26,256 -> 26,26,512 -> 26,26,256 -> 26,26,512 -> 26,26,256
        P4 = self.make_five_conv1(P4)

        # 26,26,256 -> 26,26,128 -> 52,52,128
        P4_upsample = self.upsample2(P4)
        # 52,52,256 -> 52,52,128
        P3 = self.conv_for_P3(x2)
        # 52,52,128 + 52,52,128 -> 52,52,256
        P3 = torch.cat([P3,P4_upsample],dim=1)
        # 52,52,256 -> 52,52,128 -> 52,52,256 -> 52,52,128 -> 52,52,256 -> 52,52,128
        P3 = self.make_five_conv2(P3)

        # 52,52,128 -> 26,26,256
        P3_downsample = self.down_sample1(P3)
        # 26,26,256 + 26,26,256 -> 26,26,512
        P4 = torch.cat([P3_downsample,P4],dim=1)
        # 26,26,512 -> 26,26,256 -> 26,26,512 -> 26,26,256 -> 26,26,512 -> 26,26,256
        P4 = self.make_five_conv3(P4)

        # 26,26,256 -> 13,13,512
        P4_downsample = self.down_sample2(P4)
        # 13,13,512 + 13,13,512 -> 13,13,1024
        P5 = torch.cat([P4_downsample,P5],dim=1)
        # 13,13,1024 -> 13,13,512 -> 13,13,1024 -> 13,13,512 -> 13,13,1024 -> 13,13,512
        P5 = self.make_five_conv4(P5)

        #   第三个特征层
        #   y3=(batch_size,75,52,52)
        out2 = self.yolo_head3(P3)
        #   第二个特征层
        #   y2=(batch_size,75,26,26)
        out1 = self.yolo_head2(P4)
        #   第一个特征层
        #   y1=(batch_size,75,13,13)
        out0 = self.yolo_head1(P5)

        return out0, out1, out2


class feature_extrator_yolo(FeatureExtractor):   
    def __init__(self):
        self.data_source = None
        
        #read the class
        classes_path = 'v1/model_data/voc_classes.txt'   
        data_path = 'v1/VOC2007/ImageSets/Main/train.txt'  
        class_names = []
        with open(classes_path.replace('\\', '/'), encoding='utf-8') as f:
            class_names = f.readlines()
        self.class_names = [c.strip() for c in class_names]   
        self.num_classes = len(class_names)

        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Using {} device".format(device))
        self.model = Model_Extractor(num_anchors=3, num_classes=self.num_classes).to(device)
        #weights_init(self.model)

    '''
    def set_classes_extractor(self, classes_extractor):      
        self.classes_names = classes_extractor.get_class_names() 
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Using {} device".format(device))
        self.model = Model_Extractor(num_anchors=3, num_classes=len(self.classes_names)).to(device)
    '''

    def get_class_names(self):
        return self.class_names

    def set_data_source(self,data_source):
        self.data_source = data_source

    def get_data_source (self):
        return self.data_source

    def get_feature(self):
        print('Not implemented ：FeatureExtractor.get_feature')
    
    def get_model(self):
        return self.model
    
    def save_model(self):  
        print('Saving weights...')      
         
    
    def load_model(self):
        '''
        print('Loading weights into state dict...')
        model_dict = self.model.state_dict()
        model_path = os.path.join(settings.MODEL_INIT_ROOT,"yolo4_voc_weights.pth").replace('\\', '/') 
        pretrained_dict = torch.load(model_path)
        pretrained_dict = {k: v for k, v in pretrained_dict.items() if np.shape(model_dict[k]) ==  np.shape(v)}
        model_dict.update(pretrained_dict)
        self.model.load_state_dict(model_dict)
        print('Finished!')
        '''
    
    def freeze_model(self):
        for param in self.model.parameters():
            param.requires_grad = False
    
    def unfreeze_model(self):
        for param in self.model.parameters():
            param.requires_grad = True
