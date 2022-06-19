'''
Author: jmlv
Date: 2022-03-14 15:14:28
LastEditTime: 2022-04-26 17:50:34
LastEditors: Please set LastEditors
Description:  
FilePath: /SoFuse/MoFarmBackEnd/manager_dataset.py
'''
from .models import MoFarmDataset
import csv
import os
from django.conf import settings
import threading

dataset_buf = {} #数据集的内存缓存，减少反复的读取硬盘
buf_lock = threading.RLock()  #和dataset_buf相配套的锁
class DatasetManager(object):
    def __init__(self): 
        return 
    
    def get_dataset(self,name):
        try:
            return MoFarmDataset.objects.filter(name=name).first()
        except Exception as e:
            return None
    '''
    添加数据集
        name - 数据集名称
        desc - 说明
        dataset_path - csv路径
        type - 数据集类型(table|text|image|video|timeseq|audio|graph)
    '''  
    def add_dataset(self, name, desc, type):
        dataset = MoFarmDataset (name = name, desc = desc , type = type)
        dataset.save()
        return True
    
    '''
    获取所有的数据集的列表
    '''
    def get_datasets(self):
        list = MoFarmDataset.objects.all()
        result = []
        for i in range (len(list)):
            print ('%d %s %s %s' %(list[i].id, list[i].name, list[i].desc, list[i].dataset_path))
            result.append({"id":list[i].id,"name":list[i].name, "desc":list[i].desc, "dataset_path":list[i].dataset_path})
        

        return result
    

    '''
    功能：查询某个数据集，获取某一页的数据
    参数：
        id - 数据集的ID
        page - 查询的数据页
        page_size - 每一页的数据的条数
    返回：
        数据列表
    '''
    def query_dataset(self, id, page, page_size):
        global dataset_buf
        databuf = [] 
        query_result = []
        
        if id in dataset_buf:
            buf_lock.acquire()
            databuf = dataset_buf[id]
            buf_lock.release()
        else:            
            dataset = MoFarmDataset.objects.get(id = id)
            dataset_path = None
            if dataset != None:
                dataset_path = dataset.dataset_path
                print (dataset_path)
            else:
                print ('there is no such record!')
                return None

            sys_path = os.path.join(settings.BASE_DIR,'SoFuseBackEnd/config/datasets/csv',dataset_path).replace('\\', '/') 
            print ('opening the csv:' + sys_path)

            with open(sys_path)as f:
                f_csv = csv.reader(f)
                for row in f_csv:
                    databuf.append(row)
            
            buf_lock.acquire()
            dataset_buf[id] = databuf
            buf_lock.release()

        query_result = databuf[page*page_size:(page+1)*page_size]

        return query_result
        
    '''
    功能：删除所有数据
    '''
    def remove_all(self):
        MoFarmDataset.objects.all().delete()

     