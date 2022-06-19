# -*- coding:UTF-8 -*-
from module_api import *
from yolov4.YoloDataset import *
from torch.utils.data import DataLoader
from yolov4.voc2yolo4 import voc_to_yolo4
from yolov4.voc_annotation import *
from django.conf import settings

# data load
class datasource_yolo(DataSource):
    def __init__(self):
        self.mosaic = True
        self.data_path = None
        self.data_annotation_path = None
        self.train_dataset = None
        self.test_dataset = None
        # load datasets.
        self.batch_size = 2  # batch size

        data_path = "v1/VOC2007/ImageSets/Main/2007_train.txt"
        with open(data_path,encoding='utf-8') as f:
            data_nums = f.readlines()
        
        # load train datasets.
        self.train_dataset = YoloDataset(data_nums, (608, 608), mosaic=self.mosaic, is_train=True)
        
        # Create training data loaders.
        self.train_dataloader  = DataLoader(self.train_dataset, shuffle=True, batch_size=self.batch_size, num_workers=0, pin_memory=True, drop_last=True, collate_fn=yolo_dataset_collate)
        
        # Create testing data loaders.
        self.test_dataset = YoloDataset(data_nums, (608, 608), mosaic=False, is_train=False)
        # Create data loaders.
        self.test_dataloader  = DataLoader(self.test_dataset, shuffle=False, batch_size=self.batch_size, num_workers=0, pin_memory=True, drop_last=True,collate_fn=yolo_dataset_collate)
    
  

    def set_url(self, folder_path, action):
        print('YOLODataSource.set_url')


    def set_test_url(self, train_folder_path, folder_path, action):
        print('YOLODataSource.set_test_url')

 
    
    def get_url(self):
        return self.data_path

    def get_train_data_labeled(self):
        return self.train_dataloader

    def get_validation_data(self):
        print('YOLODataSource.get_validation_data')
    
    def get_test_data(self):
        return self.test_dataloader
        
    def get_source_data_labeled(self):
        print('YOLODataSource.get_source_data_labeled')
    
    def get_target_data_unlabeled(self):
        print('YOLODataSource.get_target_data_unlabeled')

if __name__ == '__main__':
    test  = YOLO_DataSource()
    test.set_url('DetectionModel/V1/test')
    print(test.get_url())
    test_data = test.get_test_data()

    for data in test_data:
        src_data, src_data_len = data
        image_shape = np.array(np.shape(src_data)[2:4])
        print('image_shape', image_shape)
        print('----\n', src_data)
        print('len', src_data_len)

