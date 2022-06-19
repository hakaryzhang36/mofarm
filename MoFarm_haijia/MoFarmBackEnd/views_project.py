from asyncio import start_unix_server
from genericpath import exists
import imp
from multiprocessing import managers
from urllib import response
from uuid import RESERVED_FUTURE
from .models import MoFarmProject, MoFarmProjectStatus
from .manager_project import ProjectManager
from django.shortcuts import render, HttpResponse
import os
import json
from django.conf import settings
import datetime
import math
import pandas as pd
# Create your views here.

# Create your views here.


def test_project(request):
    response = {}
    manager = ProjectManager()

    name = 'first_project'
    desc = '第一个项目',
    config_path = 'first_project.json'

    status = {}
    status["train_loss1"] = 0.01
    status["train_loss2"] = 0.02
    status["test_loss1"] = 0.03
    status["test_loss2"] = 0.04
    status["epoch"] = 3
    status_json = json.dumps(status, ensure_ascii=False)

    manager.add_project(name=name, desc=desc,
                        config_path=config_path, status=status_json)

    manager.get_projects()

    response['code'] = 200
    response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

# modidfed by csj, 2022-3-22


def add_project(request):
    '''
    web method: POST
    params:
        projectName
        desc
        projectType
    '''
    response = {}
    if request.method != 'POST':
        response['code'] = 400
        response['message'] = 'wrong method'
        response['id'] = -1
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type='application/json')

    manager = ProjectManager()
    request_msg = request.body
    project_msg = json.loads(request_msg)

    project_name = project_msg['projectName']
    project_desc = project_msg['desc']
    project_type = project_msg['projectType']
    project_inherit = project_msg['inherit']

    status = ""
    create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")

    if project_inherit:
        # 检查是否存在要继承的项目
        try:
            old_project = MoFarmProject.objects.get(name=project_inherit)
        except Exception as e:
            print(e)
            response['code'] = 202
            response['message'] = '不存在被继承的项目!'
            response['id'] = -1
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
    #   motifed by lgm 22/04/21
    default_status = {"total_progress": 0,'run_status':'stop'}
    default_status = json.dumps(default_status)
    project_id = manager.add_project_online(
        project_name, project_desc, default_status, create_time, project_type)
    # project_id = manager.add_project_online(
    #     project_name, project_desc, status, create_time, project_type)

    if project_id >= 0:
        if project_inherit != '':
            manager.inherit_project(project_name, project_inherit)
        response['code'] = 200
        response['message'] = 'Success!'
        response['id'] = project_id
    else:
        response['code'] = 401
        response['message'] = '已存在相同名称的项目, 项目创建失败!'
        response['id'] = -1
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


# modified by csj, 2022-3-23
def update_project(request):
    response = {}
    if request.method != 'POST':
        response['code'] = 400
        response['message'] = 'wrong method'
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type='application/json')

    request_msg = request.body
    project_config = json.loads(request_msg)

    manager = ProjectManager()

    project_basic_info = project_config['project_basic_info']
    id = int(project_basic_info['project_id'])
    name = project_basic_info['project_name']
    desc = project_basic_info['project_desc']

    project_original_config = project_config['project_structure']

    try:
        msg = manager.update_project(id, name, desc, project_original_config)
    except Exception as e:
        msg = str(type(e)) + ':' + str(e)

    # msg = manager.update_project(id, name, desc, project_original_config)

    if msg == 'success!':
        response['code'] = 200
    else:
        response['code'] = 400
    response['message'] = msg
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def update_project_status(request):
    response = {}
    manager = ProjectManager()

    name = request.GET.get("name")
    status = request.GET.get("status")

    if manager.update_project_status(name, status):
        response['code'] = 200
        response['message'] = 'Success!'
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
    else:
        response['code'] = 401
        response['message'] = 'Fail!'
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def clear_project(request):
    response = {}
    manager = ProjectManager()
    manager.remove_all()
    response['code'] = 200
    response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def run_project(request):
    '''
    web method: POST
    params:
        id        
    '''
    response = {}
    manager = ProjectManager()
    if request.method != 'POST':
        response['code'] = 400
        response['message'] = 'wrong method'
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type='application/json')

    request_msg = request.body
    project_msg = json.loads(request_msg)

    id = int(project_msg['id'])

    project = MoFarmProject.objects.get(id=id)
    try:
        status = json.loads(project.status)
        real_time_status = status['run_real_time_msg']
        real_time_status = dict.fromkeys(real_time_status, 0)
        print('实时运行状态信息************************************************')
        print(real_time_status)
        status['total_progress'] = 0
        status['run_real_time_msg'] = real_time_status
        project.status = json.dumps(status)
        project.save()
    except:
        print('项目还没有启动，还没有状态信息')

    manager = ProjectManager()
    success = manager.run_project_controller(id)

    if success:
        response['code'] = 200
        response['message'] = 'Success!'
    else:
        response['code'] = 401
        response['message'] = 'Fail!'

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def reset_status(id):
    try:
        project = MoFarmProject.objects.get(id=id)
        status = project.status

        # history_file_path = status['run_history_path']
        # print('**********************************')
        # print(history_file_path)
        # history_status = pd.read_csv(history_file_path)
        # print(history_status)
        # column_len = len(history_status.shape[1])
        # history_status.drop(history_status.index, inplace=True)
        # history_status.loc[0]=[0 for i in range(column_len)]
        # print(history_status)
        # history_status.to_csv(history_file_path, index=False, mode='w')
        # print('*****************************************')

        real_time_status = status['run_real_time_msg']
        real_time_status = dict.fromkeys(real_time_status, 0)
        status = {'total_progress': 0, 'run_real_time_msg': real_time_status,
                  'run_history_path': history_file_path}
        project.status = status
        project.save()

        return True
    except Exception as e:
        print(e)
        return False


def get_projects(request):
    response = {}

    manager = ProjectManager()
    query_result = manager.get_projects()

    if query_result == None:
        response['code'] = 401
        response['message'] = 'Fail!'
        response['mapMsg'] = []
    else:
        # 返回状态信息
        response['code'] = 200
        response['message'] = 'Success!'
        response['mapMsg'] = query_result

    # return HttpResponse("你 XX")

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


'''
功能：根据项目的ID查询某个项目的配置
'''


def get_project_config(request):
    response = {}
    id = int(request.GET.get("id"))

    # print('i am going to ============')
    manager = ProjectManager()
    flag, query_result = manager.get_project_config(id)

    if flag == 0:
        response['code'] = 401
        response['message'] = 'No such project'
    elif flag == 2:
        response['code'] = 204
        response['message'] = 'No configuration'
    else:
        # 返回状态信息
        response['code'] = 200
        response['message'] = 'Success!'
    response['mapMsg'] = query_result
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


'''
功能：根据项目的ID查询某个项目的状态
'''

'''modified by lgm, 2022-3-22  未完成'''
# modified bys csj, 2022-4-11


def get_project_status_all(request):
    id = int(request.GET.get("id"))

    response = ProjectManager().get_status(id=id, flag=1)

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

# added bys csj, 2022-4-11


def get_project_status_realtime(request):
    id = int(request.GET.get('id'))
    response = ProjectManager().get_status(id=id, flag=0)
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type='application/json')

# modidfed by lgm, 2022-3-22


def get_projects_by_page(request):
    response = {}
    project_type = request.GET.get("algriType")
    try:
        page_number = int(request.GET.get('pageNum'))
    except Exception as e:
        page_number = 1
    try:
        page_size = int(request.GET.get('pageSize'))
    except Exception as e:
        page_size = 12

    #   按更新时间降序排序，即最新更新的在前面
    projects_all = MoFarmProject.objects.filter(
        project_type=project_type).order_by('-updated_time')
    total_project_count = MoFarmProject.objects.filter(
        project_type=project_type).count()
    if total_project_count == 0:
        response['code'] = 401
        response['message'] = 'Fail,the classifier of project is not exist!'
        response['project_msg'] = []
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

    total_pages = math.ceil(total_project_count / page_size)
    if page_number > total_pages:
        page_number = total_pages
    cursor = (page_number - 1) * page_size

    if page_number == total_project_count:

        if total_project_count == 1:    # 当只有一张时不切片
            results = [projects_all[cursor]]
        else:
            results = projects_all[cursor:total_project_count - 1]
    else:
        results = projects_all[cursor:cursor + page_size]

    if page_number >= total_pages:
        isNext = False
    else:
        isNext = True
    # 保存分页数据
    projects_query = []
    for var in results:
        try:
            status = json.loads(var.status)['run_status']
        except:
            status = 'stop'
        projects_query.append(
            {'id': var.id, 'name': var.name,'run_status':status,
                'desc': var.desc, 'type': var.project_type}
        )

    if page_number >= total_pages:
        isNext = False
    else:
        isNext = True
    response['code'] = 200
    response['message'] = 'Success!'
    response['totalPages'] = total_pages
    response['currentPage'] = page_number
    response['isNext'] = isNext
    response['mapMsg'] = projects_query

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

# modidfed by lgm, 2022-3-22


def get_projects_by_keyword(request):
    response = {}
    keyword = request.GET.get('keyword', None)
    try:
        page_number = int(request.GET.get('pageNum'))
    except Exception as e:
        page_number = 1
    try:
        page_size = int(request.GET.get('pageSize'))
    except Exception as e:
        page_size = 20

    keyword_projects = MoFarmProject.objects.filter(name__icontains=keyword)
    if not keyword_projects:
        response['code'] = 401
        response['message'] = 'Fail!not exist'

        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

    manager = ProjectManager()
    # 展示所有图片
    total_projects = MoFarmProject.objects.filter(
        name__icontains=keyword).count()
    total_pages = math.ceil(total_projects / page_size)

    if page_number > total_pages:
        page_number = total_pages

     # 当前游标位置
    cursor = (page_number - 1) * page_size

    if page_number == total_projects:

        if total_projects == 1:    # 当只有一张时不切片
            results = [keyword_projects[cursor]]
        else:
            results = keyword_projects[cursor:total_projects - 1]
    else:
        results = keyword_projects[cursor:cursor + page_size]

    if page_number >= total_pages:
        isNext = False
    else:
        isNext = True
    project_names = []
    for var in results:
        project_names.append(
            {"id": var.id, "name": var.name, "desc": var.desc})

    if len(project_names) == 0:
        response['code'] = 401
        response['message'] = 'Fail!'
        response['mapMsg'] = []
    else:
        # 返回状态信息
        response['code'] = 200
        response['message'] = 'Success!'
        response['totalPages'] = total_projects
        response['totalPages'] = page_number
        response['pageSize'] = page_size
        response['isNext'] = isNext

        response['mapMsg'] = project_names

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def get_project_type(request):
    response = {}
    if request.method == 'GET':

        Projects_type = set(
            list(MoFarmProject.objects.all().values_list('project_type')))
        # print(Projects_type)
        if len(Projects_type) == 0:
            response['code'] = 401
            response['message'] = 'Fail!'
            response['project_type'] = []

        type_list = []
        for type in Projects_type:
            type_list.append(type[0])
        type_list = sorted(type_list)
        print(type_list)

        response['code'] = 200
        response['message'] = 'Success!'
        response['project_type'] = type_list

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def delete_project(request):
    response = {}
    # projectName = request.GET.get('projectName', None)
    if request.method == "POST":
        paramslist = request.body
        json_data = json.loads(paramslist, strict=False)
        projectName = json_data['projectName']

        exists = MoFarmProject.objects.filter(name=projectName)
        if not exists:
            response['code'] = 404
            response['message'] = 'Fail!project is not found,place create'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        delete_project = MoFarmProject.objects.filter(name=projectName).first()
        config_path = delete_project.config_path
        origin_config_path = delete_project.origin_config_path
        project_type = delete_project.project_type
        # 删库
        MoFarmProject.objects.filter(name=projectName).delete()
        MoFarmProjectStatus.objects.filter(projectname=projectName).delete()

        # 删除json配置文件
        config_file_path = os.path.join(
            settings.BASE_DIR, 'MoFarmBackEnd/config/projects', project_type, config_path)
        origin_config_file_path = os.path.join(
            settings.BASE_DIR, 'MoFarmBackEnd/config/projects', project_type, origin_config_path)

        if os.path.exists(config_file_path):
            os.remove(config_file_path)
            os.remove(origin_config_file_path)
        
        #   modified by lgm 2022/04/22
        #   删除方案生成的py文件
        src_file_name = projectName+'.py'
        project_src_file_path = os.path.join(
            settings.BASE_DIR, 'MoFarmBackEnd/src/', src_file_name)
        if os.path.exists(project_src_file_path):
            os.remove(project_src_file_path)
        
        #   删除项目的日志文件
        project_logs_file_path = os.path.join(
        settings.BASE_DIR, 'MoFarmBackEnd/log/')
        print(project_logs_file_path)
        rm_comand = 'rm -rf {:}{:}*'.format(project_logs_file_path,projectName)
        print(rm_comand)
        os.system(rm_comand)
        
        response['code'] = 200
        response['message'] = 'Success!'
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
    else:
        response['code'] = 500
        response['message'] = 'place use post method!'
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
