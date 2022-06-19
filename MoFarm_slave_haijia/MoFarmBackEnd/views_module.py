'''
Author: your name
Date: 2022-03-21 15:29:00
LastEditTime: 2022-03-25 18:04:42
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /MoFarm/MoFarmBackEnd/views_module.py
'''
from .models import MoFarmModule
from .manager_module import ModuleManager
from django.shortcuts import render, HttpResponse
import os
import json
from django.conf import settings

# Create your views here.


def test_module(request):
    response = {}
    manager = ModuleManager()

    name = 'feature_extrator_image'
    desc = '图像特征提取模块'
    module_path = 'feature_extrator_image.json'
    type = 'Feature_extrator'
    manager.add_module(name, desc, module_path, type)

    manager.get_modules()

    response['code'] = 200
    response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def clear_module(request):
    response = {}
    manager = ModuleManager()
    manager.remove_all()
    response['code'] = 200
    response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def get_modules(request):
    response = {}
    
    if request.method == 'GET':
        module_type = request.GET.get("moduleType", None)
        
        manager = ModuleManager()
        # if module_type:            
        #     query_result = manager.get_modules_by_type(module_type)
        # else:
        query_result = manager.get_modules()

        if len(query_result) == 0:
            response['code'] = 401
            response['message'] = 'Fail!'
            response['mapMsg'] = []
        else:
            # 返回状态信息
            response['code'] = 200
            response['message'] = 'Success!'
            response['mapMsg'] = query_result

        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def get_module(request):
    response = {}
    id = int(request.GET.get("moduleID"))  # 数据集id

    manager = ModuleManager()
    query_result = manager.get_module_by_id(id)

    if query_result == None:
        response['code'] = 401
        response['message'] = 'Fail!'
        response['mapMsg'] = []
    else:
        # 返回状态信息
        response['code'] = 200
        response['message'] = 'Success!'
        response['mapMsg'] = json.loads(query_result)

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def get_modules_v2(request):
    response = {}
    
    if request.method == 'GET':
        manager = ModuleManager()
    
        
        Modules = MoFarmModule.objects.all()
        if not Modules:
            response['code'] = 401
            response['message'] = 'Fail!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

  
        mapMsg={}
        for var in Modules:
            query_result = manager.get_module_by_id(var.id)
            
            sys_path = os.path.join(settings.BASE_DIR,'MoFarmBackEnd/config/modules',var.type,var.module_path).replace('\\', '/')
            # print(sys_path)            
            # if os.path.exists(sys_path):
            #     print("exist")
            # print("*****************************")
            try:
                module_config = json.loads(query_result)
            except:
                module_config = []
            if var.type not in mapMsg.keys():
                mapMsg[var.type]=[]
            mapMsg[var.type].append({
                'id':var.id,
                'name':var.name,
                "desc":var.desc,
                "module_config":module_config,
            })

        
        # 返回状态信息
        response['code'] = 200
        response['message'] = 'Success!'
        response['mapMsg'] = mapMsg

        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
