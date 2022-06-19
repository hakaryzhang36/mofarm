# -*- coding:UTF-8 -*-
from django.conf import settings
import torch
import numpy as np
import time
from torch.autograd import Variable
from torch import nn
import torch.backends.cudnn as cudnn
from module_api import *
from DataSource_YOLO import DataSource_YOLO
from FeatureExtractor_YOLO import FeatureExtractor_YOLO
from yolov4.yolo_training import YOLOLoss,LossHistory,weights_init
from yolov4.DecodeBox import *
import os,sys,json
import django
import xml.etree.ElementTree as ET
from channels.layers import get_channel_layer
 

class classifier_yolo(Classifier):
    def __init__(self):  
        # Get cpu or gpu device for training.
        self.device = "cuda" if torch.cuda.is_available() else "cpu"                
        self.data_source = None
        self.feature_extractor = None
        self.model = None #Model_Classifier().to(device)
        self.Cosine_lr = False
        self.anchors = self.get_anchors('v1/yolo_anchors.txt')
       
        # test args
        self.confidence = 0.2
        self.iou = 0.5
        self.letterbox_image = False
        self.yolo_decodes = []

    def get_anchors(self, anchors_path):
        '''loads the anchors from a file'''
        with open(anchors_path) as f:
            anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]
        return np.array(anchors).reshape([-1,3,2])[::-1,:,:]
        
    def set_feature_extractor(self, feature_extractor):       
        self.feature_extractor = feature_extractor
        self.data_source = feature_extractor.get_data_source()
        self.model = feature_extractor.get_model().to(self.device)             
     
    def get_model(self): 
        return self.model
   
    def train(self):
        weights_init(self.model)
      
        # 输入参数读取
        class_names = self.feature_extractor.get_class_names()        
        num_classes = len(class_names)
        
        yolo_loss = YOLOLoss(np.reshape(self.anchors,[-1,2]), num_classes, (608, 608), 0, True, False)
        
        optimizer = torch.optim.Adam(self.model.parameters(),lr=1e-3)#, weight_decay = 5e-4)

        if self.Cosine_lr:
            lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=5, eta_min=1e-5)
        else:
            lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.92)

        dataloader = self.data_source.get_train_data_labeled()

        num_batch = len(dataloader.dataset)
        epoch_size = num_batch // 2  # self.batch_size=2
        Init_Epoch, Epoch = 0, 10 

        for epoch in range(Init_Epoch,Epoch):
            total_loss = 0
            print('\n' + '-' * 10 + 'Train one epoch.' + '-' * 10)
            print('Epoch:'+ str(epoch+1) + '/' + str(Epoch))
            print('Start Training.')
            self.model.train()             
                
            if self.device == "cuda":
                self.model = torch.nn.DataParallel(self.model)
                cudnn.benchmark = True
                self.model = self.model.cuda()

            start_epoch_time = time.time()
            for iteration, batch in enumerate(dataloader):
                if iteration >= epoch_size:
                    break
                images, targets = batch[0], batch[1]
                start_time = time.time()
                with torch.no_grad():
                    if self.device == "cuda":
                        images = Variable(torch.from_numpy(images).type(torch.FloatTensor)).cuda()
                        targets = [Variable(torch.from_numpy(ann).type(torch.FloatTensor)) for ann in targets]
                    else:
                        images = Variable(torch.from_numpy(images).type(torch.FloatTensor))
                        targets = [Variable(torch.from_numpy(ann).type(torch.FloatTensor)) for ann in targets]
                
                #   清零梯度
                optimizer.zero_grad()
                #   前向传播
                outputs = self.model(images)
                losses = []
                num_pos_all = 0

                #   计算损失
                for i in range(3):
                    loss_item, num_pos = yolo_loss(outputs[i], targets)
                    losses.append(loss_item)
                    num_pos_all += num_pos

                loss = sum(losses) / num_pos_all
                total_loss += loss.item()

                #   反向传播
                loss.requires_grad_(True)
                loss.backward()
                optimizer.step()
                lr_scheduler.step()

                total_loss += loss
                waste_time = time.time() - start_time
                if iteration == 0 or (iteration+1) % 10 == 0:
                    print('step:' + str(iteration+1) + '/' + str(epoch_size) + ' || Total Loss: %.4f || %.4fs/step' % (total_loss/(iteration+1), waste_time))
           

            waste_epoch_time = time.time() - start_epoch_time
            print('Epoch:'+ str(epoch+1) + '/' + str(Epoch) +' || Train Loss: %.4f || %.4fs/epoch' % (total_loss/(epoch_size+1), waste_epoch_time))
       
        print('Finish All Training.')  

    
    def test(self):       
        #anchors = get_anchors('%s/model_data/yolo_anchors.txt' % data_path)
        class_names = self.feature_extractor.get_class_names()        
        num_classes = len(class_names)

        # load testdataset list
        image_ids = open('v1/VOC2007/ImageSets/Main/train.txt').read().strip().split()
   
        self.model.eval()  # 将模型转换为测试模式,固定住dropout层和Batch Normalization层
        if self.device == "cuda":
            self.model = nn.DataParallel(self.model)
            self.model = self.model.cuda()

        #  建立三个特征层解码用的工具
        for i in range(3):
            self.yolo_decodes.append(DecodeBox(self.anchors[i], num_classes,  (608, 608)))

        for image_id in image_ids:
            print ('---------------')
            image_path = "v1/VOC2007/JPEGImages/" + image_id + ".jpg"
            image = Image.open(image_path)
            
            image_shape = np.array(np.shape(image)[0:2])
            
            # 给图像增加灰条，实现不失真的resize or 直接resize进行识别
            if self.letterbox_image:
                crop_img = np.array(letterbox_image(image, (608, 608)))
            else:
                crop_img = image.convert('RGB')
                crop_img = crop_img.resize((608, 608), Image.BICUBIC)
            photo = np.array(crop_img,dtype = np.float32) / 255.0
            photo = np.transpose(photo, (2, 0, 1))

            #   添加上batch_size维度
            images = [photo]
            with torch.no_grad():
                images = torch.from_numpy(np.asarray(images))
                if self.device == "cuda":
                    images = images.cuda()

                outputs = self.model(images)
                output_list = []
                for i in range(3):
                    output_list.append(self.yolo_decodes[i](outputs[i]))

                #   将预测框进行堆叠，然后进行非极大抑制
                output = torch.cat(output_list, 1)
                batch_detections = non_max_suppression(output, len(class_names), conf_thres=self.confidence, nms_thres=self.iou)

                if (batch_detections[0] == None):
                    print ("no object of %s" %image_id)
                    continue
                batch_detections = batch_detections[0].cpu().numpy()                
                #   对预测框进行得分筛选
                top_index = batch_detections[:,4] * batch_detections[:,5] > self.confidence
                top_conf = batch_detections[top_index,4]*batch_detections[top_index,5]
                top_label = np.array(batch_detections[top_index,-1],np.int32)
                top_bboxes = np.array(batch_detections[top_index,:4])
                top_xmin, top_ymin, top_xmax, top_ymax = np.expand_dims(top_bboxes[:,0],-1),np.expand_dims(top_bboxes[:,1],-1),np.expand_dims(top_bboxes[:,2],-1),np.expand_dims(top_bboxes[:,3],-1)

                #  去除灰条
                if self.letterbox_image:
                    boxes = yolo_correct_boxes(top_ymin,top_xmin,top_ymax,top_xmax,np.array([608, 608]),image_shape)
                else:
                    top_xmin = top_xmin / 608 * image_shape[1]
                    top_ymin = top_ymin / 608 * image_shape[0]
                    top_xmax = top_xmax / 608 * image_shape[1]
                    top_ymax = top_ymax / 608 * image_shape[0]
                    boxes = np.concatenate([top_ymin,top_xmin,top_ymax,top_xmax], axis=-1)

            for i, c in enumerate(top_label):
                predicted_class = class_names[c]
                score = str(top_conf[i])

                top, left, bottom, right = boxes[i]
                print("%s %s %s %s %s %s\n" % (predicted_class, score[:6], str(int(left)), str(int(top)), str(int(right)),str(int(bottom))))
            
        return 
  

    def save_model(self): 
        return
        
    def load_model(self ):
        return         

    def get_model(self):
        return self.model
    
    def freeze_model(self):
        print('Freeze model ...')
        for param in self.model.parameters():
            param.requires_grad = False
    
    def unfreeze_model(self):
        print('Unfreeze model ...')
        for param in self.model.parameters():
            param.requires_grad = True


if __name__ == '__main__':
    data_source  = DataSource_YOLO ()
    extractor = FeatureExtractor_YOLO()
    classifier = Classifier_YOLO()

    extractor.set_data_source(data_source)
    classifier.set_feature_extractor(extractor)

    classifier.train()
    classifier.test()


