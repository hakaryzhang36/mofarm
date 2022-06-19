from .models import MoFarmModule
from .manager_model import ModelManager
import csv
import os
import json
from django.conf import settings

  
class ModuleManager(object):
    def __init__(self): 
        return
    
    '''
    添加模块
        name - 模块名称
        desc - 说明
        module_path - 模块jason路径
        type - 模块类型（FeatureExtrator, Classifier, DataSource)
    '''  
    def add_module(self, name, desc, module_path, type):
        dataset = MoFarmModule (name = name, desc = desc, module_path = module_path, type = type)
        dataset.save()
        return True
    
    '''
    获取所有的模块的列表
    '''
    def get_modules(self):
        result = []               

        list = MoFarmModule.objects.all()
        for i in range (len(list)):
            result.append({"id":list[i].id,"name":list[i].name, "desc":list[i].desc, "type":list[i].type})

            print ('%d %s %s %s' %(list[i].id, list[i].name, list[i].desc, list[i].type))
            
        return result
    
    '''
    按模块类别获取模块的列表
    '''
    def get_modules_by_type(self,moduleType):
        result = []
        list = MoFarmModule.objects.filter(type=moduleType)
        for i in range (len(list)):
            result.append({"id":list[i].id,"name":list[i].name, "desc":list[i].desc, "type":list[i].type})

            print ('%d %s %s %s' %(list[i].id, list[i].name, list[i].desc, list[i].type))
            
        return result

    '''
    功能：查询某个模块的配置
    参数：
        id - 模块的ID        
    返回：
        配置的jason字符串
    '''
    def get_module_by_id(self, id):
        result = ''      
        model_manager = ModelManager ()
        
        try:        
            module = MoFarmModule.objects.get(id = id)
            json_path = module.module_path
            dataType = module.type

            #配置文件
            sys_path = os.path.join(settings.BASE_DIR,'MoFarmBackEnd/config/modules',dataType,json_path).replace('\\', '/')
            #print ('opening the json:' + sys_path)

            json_str = ''
            with open(sys_path ,'r') as f:
                for line in f:
                    json_str = json_str + line

            #读取相关的模型   
            models = model_manager.get_models_of_module(id)            
            model_name_list = []
            
            if models != None:
                for i in range(len(models)):
                    model_name_list.append(models[i]["name"])

                #解析json 配置
                config = json.loads(json_str)
                if len(model_name_list)!=0:
                    config["parameters"]["model"] =  model_name_list
                    
                
                try:                  
                    if isinstance(config["parameters"]['model'],str):
                        config["parameters"]['model'] = [config["parameters"]['model']]
                except:
                    pass
                
                    
                json_str = json.dumps(config, ensure_ascii=False)
                if (len(models) > 0):
                    print(json_str)

            
            return json_str
        
        except Exception as e:
            print ('error happended in get_module_by_id')
            return None
        
    '''
    功能：查询某个模块的配置
    参数：
        name - 模块的名称
    返回：
        配置的jason字符串 
    '''
    def get_module_by_name(self, name):
        result = ''        
        
        try:        
            module = MoFarmModule.objects.get(name = name)
            json_path = module.module_path
            type = module.type
            
            print (json_path)
            
            sys_path = os.path.join(settings.BASE_DIR,'MoFarmBackEnd/config/modules',json_path).replace('\\', '/') 
            print ('opening the json:' + sys_path)

            with open(sys_path)as f:
                for line in f:
                    result = result + line

            #print (result)
            return result
        except:
            print ('there is no such module!')
            return None

    '''
    功能：查询某个模块的id
    参数：
        name - 模块的名称
    返回：
        模块的id
    '''
    def get_module_id_by_name(self, name):
        result = ''        
        
        try:        
            module = MoFarmModule.objects.get(name = name)
            
            return module.id
        except:
            print ('there is no such module!')
            return -1
        
    '''
    功能：删除所有模块配置
    '''
    def remove_all(self):
        MoFarmModule.objects.all().delete()

     