from asyncio import start_unix_server
from genericpath import exists
import imp
from uuid import RESERVED_FUTURE

from MoFarmBackEnd.manager_task import TaskManager
from .models import MoFarmProject, MoFarmProjectStatus
from .manager_project import ProjectManager
from django.shortcuts import render, HttpResponse
import json
from django.conf import settings

def updata_task_status(request):
    response = {}
    manager = ProjectManager()
    
    request_json = json.loads(request.body)
    task_id = request_json['task_id']
    status = request_json['status']

    TaskManager().update_task_status(task_id=task_id, status=status)

    response['code'] = 200
    response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

