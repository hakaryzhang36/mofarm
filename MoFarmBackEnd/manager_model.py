'''
Author: jmlv
Date: 2022-03-14 15:15:22
LastEditTime: 2022-04-26 17:50:31
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /SoFuse/MoFarmBackEnd/manager_model.py
'''
from .models import MoFarmModel
import csv
import os
from django.conf import settings

'''
4.模型仓库
模型是指各个模块训练之后保存下来的模型。
模型表的设置：
   模型名称
   对应模块ID
   说明
   pth文件的路径


4.模型仓库
4.1 获取特定模块的模型列表
处理方法：根据模块ID，在模型表中查找对应的模型并返回列表。
'''


class ModelManager(object):
    def __init__(self): 
        return
    
    '''
    功能:添加模型
    参数:
        name - 模块名称
        moduleid - 对应模块ID
        model_path - 模型pth文件的路径
    '''  
    def add_model(self, name, module_id,  model_path):
        model = MoFarmModel (name = name, module_id = module_id, model_path = model_path)
        model.save()
        return True
    
    '''
    功能:获取所有的模型的列表
    '''
    def get_all_models(self):
        list = MoFarmModel.objects.all()
        for i in range (len(list)):
            print ('%d %s %s %s' %(list[i].id, list[i].name, list[i].moduleid, list[i].desc))
        return list
    
    '''
    功能:根据模型的名称，获取模型的编号。
    参数:
        model_name - 模型的名称
    返回:
        模型的id
    '''
    def get_model_id_by_name(self, model_name):          
        try:            
            model = MoFarmModel.objects.get(name = model_name)

            if model != None:
                return model.id
            else:
                return -1
        except:
            print ('there is no such model!')
            return -1


    '''
    功能:根据模块ID，在模型表中查找对应的模型并返回列表。
    参数:
        moduleid - 模块的ID        
    返回:
        模型列表
    '''
    def get_models_of_module(self, module_id):        
        result = []               
         
        try:            
            models = MoFarmModel.objects.filter(module_id = module_id)
            for model in models:                
                result.append({"id": model.id, "name": model.name})
                       
            return result
        except:
            print ('error in get_models_of_module:there is no such module!')
            return result

        
    '''
    功能：删除所有模块配置
    '''
    def remove_all(self):
        MoFarmModel.objects.all().delete()

     
