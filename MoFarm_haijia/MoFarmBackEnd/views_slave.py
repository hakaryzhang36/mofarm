from multiprocessing import Manager
from urllib import response
from django.shortcuts import render, HttpResponse
import os
import json
from django.conf import settings 
from .manager_slave import SlaveManager

def add_slave(request):
    response = {}
    manager = SlaveManager()
    slave_config = json.loads(request.body)
        
    id = manager.add_slave(slave_config)
    
    response['code'] = 0
    response['id'] = id
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
   
def delete_slave(request):
    '''
    训练节点主动注销
    '''
    response = {}
    manager = SlaveManager()
    id = json.loads(request.body)['id']
    if manager.delete_slave(id):
        response['code'] = 0
    else:
        response['code'] = -1
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

def keep_alive(request):
    response = {}
    manager = SlaveManager()
    
    data_json = json.loads(request.body)
    id = data_json['id']
    alive_timestamp = data_json['alive_timestamp']
    
    if manager.keep_alive(id, alive_timestamp):
        response['code'] = 0
    else:
        response['code'] = -1
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

def update_slave_state_all(request):
    response = {}
    manager = SlaveManager()
    config = json.loads(request.body)
    # print('收到更新的slave_config:\n', config)
    id = config['id']
    
    success = manager.update_slave_state_all(id, config)
    
    if success:
        response['code'] = 0
    else:
        response['code'] = -1
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

