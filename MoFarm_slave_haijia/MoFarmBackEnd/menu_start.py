'''
Author: your name
Date: 2022-03-17 14:01:16
LastEditTime: 2022-03-24 20:03:01
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /MoFarm/MoFarmBackEnd/menu_start.py
'''
import threading
from .views_dataset import  import_dataset_offline
from .manager_module import ModuleManager
from .manager_project import ProjectManager
from .manager_model import ModelManager
from .manager_dataset import DatasetManager
import json

def menu(args):
    module_manager = ModuleManager ()
    project_manager = ProjectManager()
    dataset_manager = DatasetManager()
    model_manager = ModelManager()


    #   导入本地的数据
    #   modified by lgm
    #   add 10. import dataset offline
    #   2022-3-17
    while True:
        print ('1. add module')
        print ('2. list modules')
        print ('3. add project')
        print ('4. list projects')
        print ('5. run project')
        print ('6. add dataset')
        print ('7. list datasets')
        print ('8. add model')
        print ('9. list model')
        print('10. import dataset offline')
         
        select = input('your choise:')
        if select == '1':
            print ('------------add module---------------')
            name = input('name:')
            desc = input('desc:')
            module_path = input('module path:')
            type = input('type:')
            module_manager.add_module(name, desc, module_path, type)
        elif select == '2':
            module_manager.get_modules()
        elif select == '3':
            print ('------------add project---------------')

            name = input('name:')
            desc = input('desc:')
            config_path = input('config path:')
            status = {}
            status["train_loss1"] = 0.01
            status["train_loss2"] = 0.02
            status["test_loss1"] = 0.03
            status["test_loss2"] = 0.04
            status["epoch"] = 3        
            status_json = json.dumps(status, ensure_ascii=False)
            
            project_manager.add_project(name, desc, config_path, status_json)
        elif select == '4':
            project_manager.get_projects()
        elif select == '5':
            id = int(input('id:'))           

            project_manager.run_project(id)
        elif select == '6':
            print ('------------add dataset---------------')

            name = input('name:')
            desc = input('desc:')
            dataset_path = input('dataset path:')
            type = input('type:')  
             
            dataset_manager.add_dataset(name, desc, dataset_path, type)
        elif select == '7':
            dataset_manager.get_datasets()
        elif select == '8':
            print ('------------add model---------------')

            name = input('name:')
            moduleid = int(input('moduleid'))
            desc = input('desc:')
            model_path = input('model_path:')
             
            model_manager.add_model(name, moduleid, desc, model_path)
        elif select == '9':
            model_manager.get_all_models()
       
        # motified by lgm
        elif select=='10':
            print('--------------import dataset offline------------------')
            print('----------image must be follow the VOC2007------------')
            print('-----------dataset file must be *.zip file------------')
            print('--------------------os must be linux------------------')

            target_path = input('dataset path:')
            dataset_name = input('dataset name:')            
            desc = input('desc:')
            type = input('type:') 
            import_dataset_offline(dataset_name,target_path,desc,type)# 解压缩
   


def start_menu():
    print ("starting...")
    t1 = threading.Thread(target=menu,args=('t1',))      
    t1.start()    
