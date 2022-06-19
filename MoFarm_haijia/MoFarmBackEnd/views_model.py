from .manager_model import ModelManager
from .manager_module import ModuleManager
from django.shortcuts import render, HttpResponse
import os
import json
from django.conf import settings 

# Create your views here.
 
# Create your views here.
def test_model(request):
    response = {}
    manager = ModelManager ()
        
    name = 'first_model'
    moduleid = 4       
    desc = '第一个模型'     
    model_path = 'first_model.pth' 
    
    manager.add_model(name, moduleid, desc, model_path)
    manager.get_all_models()

    response['code'] = 200
    response['message'] = 'Success!' 
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
    
def clear_model(request):
    response = {}
    manager = ModelManager ()
    manager.remove_all()
    response['code'] = 200
    response['message'] = 'Success!' 
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


'''
    功能:根据模块ID，在模型表中查找对应的模型并返回列表。    
'''
def get_model(request):
    response = {}
    id = int(request.GET.get("moduleid"))  #数据集id 
  
    manager = ModelManager ()
    query_result = manager.get_models_of_module(id)
 
    if query_result == None:
        response['code'] = 401
        response['message'] = 'Fail!'
        response['mapMsg'] =  []
    else:   
        # 返回状态信息
        response['code'] = 200
        response['message'] = 'Success!'
        response['mapMsg'] =  query_result
    
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

'''
    功能:添加模型。如果对应的模型已经存在，则不作变化
'''
def add_model(request):
    response = {}
    model_name = request.GET.get("model_name")  #数据集id 
    module_name = request.GET.get("module_name")  #数据集id 

  
    model_manager = ModelManager ()
    module_manager = ModuleManager()

    model_id = model_manager.get_model_id_by_name(model_name)
    module_id = module_manager.get_module_id_by_name(module_name)

    if model_id == -1 and module_id >= 0:
        model_manager.add_model(model_name, module_id, model_name)
    
    response['code'] = 200
    response['message'] = 'Success!'    
    
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")