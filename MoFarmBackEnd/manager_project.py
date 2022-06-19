'''
2.1 项目仓库数据库
2.1.1 项目元信息表
项目元信息表（算法方案元信息表）
	项目id
	项目方案名称
	说明
	所属算法类型（目标识别/图片分类/数据预测/异常检测）
	配置json文件路径
	运行状态说明（未运行/训练/测试）
	创建时间
	更新时间

2.1.2 项目运行状态表
	方案名称
	运行状态说明（未运行/训练/测试）
	运行总进度
	运行状态实时信息（当前运行轮次的指标信息）
	运行状态历史信息json文件路径（各运行指标信息的历史快照记录在json文件中）

2.1.3 项目具体配置信息，保存成一个jason文件
   所使用的模块列表
   每个模块的具体属性配置
   模块之间的连接关系(a,b,relation)



2.2 项目仓库接口
2.2.1 新建算法方案
处理方法：写入项目元信息表
2.2.2 保存算法方案
处理方法： 更新项目元信息表及项目配置json文件
2.2.3 获取项目列表
处理方法：读取项目元信息表
2.2.4 批量获取项目列表
处理方法：读取项目元信息表
2.2.5 按关键字搜索项目
处理方法：读取项目元信息表
2.2.6 获取特定项目配置信息：
处理方法：读取特定项目的配置json文件。
2.2.7 获取特定项目的状态信息：
处理方法：读取读取项目元信息表中特定项目的运行状态。
2.2.8 运行项目：
处理方法：驱动特定项目对应的运行脚本。
2.2.9 删除项目
处理方法： 删除项目元信息表对应数据及对应配置json文件

'''
import datetime
import imp
import shutil
from tkinter.tix import Tree
from turtle import shape
from .models import MoFarmProject, MoFarmProjectStatus
import csv
import os
from django.conf import settings
from .factory_project import ProjectFactory
import json
import pandas as pd
import requests

# modified by zhj, 2022-5-4
from .manager_slave import SlaveManager
import requests
from time import sleep
import threading
from .manager_task import TaskManager
from .controller import Controller

class ProjectManager(object):
    def __init__(self):
        return

    '''
    添加项目
        name - 项目名称
        desc - 说明
        config_path - 项目配置json路径
        status -  运行状态,json字符串
    '''

    def add_project_by_file(self, name, desc, config_path, status):
        project = MoFarmProject(name=name, desc=desc,
                                config_path=config_path, status=status)
        project.save()
        return True

    '''
    添加项目
        name - 项目名称
        desc - 说明
        config_path - 项目配置json路径
        status -  运行状态,json字符串
    '''
    # modifie by csj, 2022-3-22

    def add_project_online(self, name, desc, status, create_time, project_type):
        config_json = '%s.json' % name
        original_config_json = '%s_original.json' % name
        print('Status json: {}'.format(status))

        try:
            project = MoFarmProject(name=name, desc=desc, origin_config_path=original_config_json, config_path=config_json, status=status,
                                    created_time=create_time, updated_time=create_time, project_type=project_type)
            project.save()

        except:
            return -1

        config_dir = os.path.join(
            settings.BASE_DIR, 'MoFarmBackEnd/config/projects', project_type).replace('\\', '/')
        os.makedirs(config_dir, exist_ok=True)

        config_sys_path = os.path.join(
            config_dir, config_json).replace('\\', '/')
        original_config_sys_path = os.path.join(
            config_dir, original_config_json).replace('\\', '/')

        # print('opening the json:' + sys_path)
        print('create a blank config file:'+config_sys_path)
        with open(config_sys_path, 'w') as f:
            pass

        print('create a blank config file:'+original_config_sys_path)
        with open(original_config_sys_path, 'w') as f:
            pass

        # with open(sys_path, "w")as f:
        #     f.write(config)
        #     f.close()

        return project.id


    '''
    继承项目
        name - 项目名称
        inherti - 被继承项目名字
    '''
    # create by csj 2022/4/8

    def inherit_project(self, name, inherit):
        new_project = MoFarmProject.objects.get(name=name)
        old_project = MoFarmProject.objects.get(name=inherit)
        
        old_config_path = old_project.config_path
        old_original_config_path = old_project.origin_config_path
        old_type = old_project.project_type
        
        old_config_path = os.path.join(
            settings.BASE_DIR, 'MoFarmBackEnd/config/projects', old_type, old_config_path).replace('\\', '/')
        old_original_config_path = os.path.join(
            settings.BASE_DIR, 'MoFarmBackEnd/config/projects', old_type, old_original_config_path).replace('\\', '/')
        
        new_config_path = new_project.config_path
        new_original_config_path = new_project.origin_config_path
        new_type = new_project.project_type
        
        new_config_path = os.path.join(
            settings.BASE_DIR, 'MoFarmBackEnd/config/projects', new_type, new_config_path).replace('\\', '/')
        new_original_config_path = os.path.join(
            settings.BASE_DIR, 'MoFarmBackEnd/config/projects', new_type, new_original_config_path).replace('\\', '/')
        
        print('*********************************************')
        print('going to inherit consice config')
        print('old project:')
        print(old_config_path)
        print('new project:')
        print(new_config_path)
        shutil.copyfile(old_config_path, new_config_path)

        print('=============================================')
        print('going to inherit original config')
        print('old project:')
        print(old_original_config_path)
        print('new project:')
        print(new_original_config_path)
        shutil.copyfile(old_original_config_path, new_original_config_path)



    '''
    更新项目
        id - 项目的id
        name - 项目名称
        desc - 说明
        original_config - 项目配置json字符串,前端返回的原始配置json
    需要分别存储原始配置和简洁配置，前者是为了前端页面展示，后者是为了后端代码运行设置        
    '''
    # modified by csj, 2022-3-23

    def update_project(self, id, name, desc, original_config):
        try:
            project = MoFarmProject.objects.get(id=id)

        except:
            print('there is no such project!')
            return 'there is no such project!'

        try:
            project.name = name
            project.desc = desc
            project.config_path = name + '.json'
            project.origin_config_path = name + '_original.json'
            project.save()
        except:
            print('new name of project %s is conflict with existed projects' % name)
            return 'new name of project %s is conflict with existed projects' % name

        project_type = project.project_type
        config_json = project.config_path
        original_config_json = project.origin_config_path
        # print(original_config_json)

        config_sys_path = os.path.join(
            settings.BASE_DIR, 'MoFarmBackEnd/config/projects', project_type, config_json).replace('\\', '/')
        original_config_sys_path = os.path.join(
            settings.BASE_DIR, 'MoFarmBackEnd/config/projects', project_type, original_config_json).replace('\\', '/')

        print("store original project config")
        print('opening the json:' + original_config_sys_path)
        with open(original_config_sys_path, "w") as f:
            json.dump(original_config, f)

        concise_config = self.tranform_project_config(original_config)
        print("store consice project config")
        print('opening the json:' + config_sys_path)
        with open(config_sys_path, "w")as f:
            json.dump(concise_config, f)

        return 'success!'

    '''
    将前端返回的原始项目配置转化简洁版本
        {
            "modules":[],
            "links":[],
            "running":{}
        }
    '''
    # added by csj, 2022-3-23

    def tranform_project_config(self, original_config):
        modules = []
        links = []
        running = {
            original_config["running_config"]["initial_module"]: original_config["running_config"]["initial_function"]
        }

        graph_config = original_config["graph_config"]

        # print("length of graph_config: "+str(len(graph_config)))
        for element in graph_config:
            if element['shape'] == 'edge':
                start_point_id = element['source']['cell']
                #start_point = [point['shape']
                start_point = [point['data']['local_name']
                            for point in graph_config if point['id'] == start_point_id][0]
                
                end_point_id = element['target']['cell']
                #end_point = [point['shape']
                end_point =  [point['data']['local_name']
                             for point in graph_config if point['id'] == end_point_id][0]

                links.append(
                    [start_point, end_point])
            else:
                module_info = element['data']
                # print("module_info-----------------------")
                # print(module_info)
                # print("length of module_info: "+str(len(module_info)))
                module_name = module_info['name']
                module_local_name = module_info['local_name']
                module_info.pop('name')
                module_info.pop('local_name')
                module_config = module_info
                modules.append(
                    {
                        "name": module_name,
                        "local_name": module_local_name,
                        "config": module_config
                    }
                )

        return {'modules': modules, 'links': links, 'running': running}

    '''
    更新项目状态
        name - 项目名称
        status - 项目状态        
    '''

    def update_project_status(self, name, status):
        try:
            project = MoFarmProject.objects.get(name=name)

            project.status = status
            project.save()

            return True
        except:
            print('更新项目状态是出错：there is no such project!')
            return False

    '''
    获取所有的项目的列表
    '''

    def get_projects(self):
        result = []
        list = MoFarmProject.objects.all()
        for i in range(len(list)):
            result.append(
                {"id": list[i].id, "name": list[i].name, "desc": list[i].desc})

            print('%d %s %s %s %s' % (
                list[i].id, list[i].name, list[i].desc, list[i].status, list[i].config_path))

        return result

    '''
    功能：查询某个项目的配置
    参数：
        id - 项目的ID        
    返回：
        配置的json字符串
    '''

    def get_project_config(self, id):
        try:
            project = MoFarmProject.objects.get(id=id)

        except:
            print('No such project')
            return 0, []

        project_type = project.project_type
        original_config_json = project.origin_config_path
        print(original_config_json)
        # print('=====================') 

        original_config_sys_path = os.path.join(
            settings.BASE_DIR, 'MoFarmBackEnd/config/projects', project_type, original_config_json).replace('\\', '/')
        print('opening the json:' + original_config_sys_path)

        try:
            with open(original_config_sys_path)as f:
                result = json.load(f)

            # print (result)
            return 1, result
        except Exception as e:
            print('the configuration is blank!')

            blank_config = {
                "counter": 1,
                "running_config": {
                    "initial_module": "",
                    "initial_function": ""},
                "graph_config": []
            }

            return 2, blank_config

    '''
    功能：查询某个项目的状态
    参数：
        id - 项目的ID        
    返回：
        状态的json字符串
    '''

    # def get_project_status(self, id):
    #     result = ''

    #     try:
    #         project = MoFarmProject.objects.get(id=id)
    #         print('geting the status of the project %d' % id)
    #         return project.status

    #     except:
    #         print('there is no such project!')
    #         return None

    '''
    功能：删除所有项目
    '''

    def remove_all(self):
        MoFarmProject.objects.all().delete()

    '''
    功能：启动项目
    参数：
        id - 项目的id
    '''

    def run_project(self, id):
        config_json = ''

        # try:
        if True:
            project = MoFarmProject.objects.get(id=id)
            json_path = project.config_path
            name = project.name

            print(json_path)

            project_type = project.project_type

            sys_path = os.path.join(
                settings.BASE_DIR, 'MoFarmBackEnd/config/projects', project_type, json_path).replace('\\', '/')
            print('opening the json:' + sys_path)

            with open(sys_path)as f:
                for line in f:
                    config_json = config_json + line

            project_factory = ProjectFactory(name)
            project_factory.parse_json(config_json)
            print ('building project...')
            project_factory.build_project()
            project_factory.draw_project()
            project_factory.run_project()

            return True
        # except:
        #     print ('run_project error!')
        #     return False

    # modified by zhj, 2022-5-4
    def run_project_controller(self, project_id):
        '''
        功能：主服务器启动项目，分配到节点执行
        '''
        config_json = ''

        # try:
        if True:
            controller = Controller()
            controller.add_task_to_list(project_id)
            # project = MoFarmProject.objects.get(id=project_id)

            # json_path = project.config_path
            # name = project.name
            # print(json_path)

            # project_type = project.project_type

            # sys_path = os.path.join(
            #     settings.BASE_DIR, 'MoFarmBackEnd/config/projects', project_type, json_path).replace('\\', '/')
            # print('opening the json:' + sys_path)

            # with open(sys_path)as f:
            #     for line in f:
            #         config_json = config_json + line
            # project_json = json.loads(config_json)

            # project_json = {} # test
            # 获取训练节点
            # slave_id = SlaveManager().get_free_slave()
            # slave = SlaveManager().get_slave_config(slave_id)
            # socket = 'http://' + slave['ip'] + ':' + slave['port']
            # print('获取训练节点成功, id: {}'.format(slave_id))
            # 1 发送数据集[暂无]
            # project_json['name'] = project.name
            # for data_sourece in project_json['modules']:
            #     if data_sourece['name'] == 'data_source':
            #         dataset = open('', 'r')
            #         requests.post(socket + '/Dataset/', files=dataset)

            # 2 发送项目配置，启动项目
            # print('启动项目...')
            # data_json = {}
            # data_json['project_json'] = project_json
            # data_json['project_id'] = project_id
            # res_data = requests.post(socket + '/MoFarmBackEnd/Project/run_project_slave', data = json.dumps(data_json))
            # 3 检查启动操作
            # res_json = json.loads(res_data.content)
            # if res_json['code'] == 200:
            #     print('训练节点已启动')
            #     return True
            # else:
            #     print('训练节点启动失败')
            #     return False
            return True

    # modified by zhj, 2022-5-4
    def run_project_slave(self, project_json):
        '''
        功能：训练节点启动项目
        '''
        project_factory = ProjectFactory(project_json['name'])
        project_factory.parse_json(project_json)
        print ('building project...')
        project_factory.build_project()
        project_factory.draw_project()
        t = project_factory.run_project() # t为训练进程
        print('启动训练')
        # 定期发送节点状态信息到主服务器
        from slave_config import slave as loacl_slave
        t2 = threading.Thread(target=loacl_slave.update_slave_running_config, args=(t,))
        t2.start()
        # 等待，发送pth文件
        from .manager_file_slave import SlaveFileManager
        t3 = threading.Thread(target=SlaveFileManager().wait_pth(t,project_json))
        t3.start()
        return 

    

    # added by csj, 2022-4-12
    def get_status(self, id, flag=0):
        response = {}
        
        try:
            project = MoFarmProject.objects.get(id=id)
        except:
            response['code'] = 204
            response['message'] = 'No such project!'
            response['result'] = {}
            return response
        
        try:
            status =json.loads(project.status)
        except:
            response['code'] = 200
            response['message'] = 'Project has not even run yet.'
            response['result'] = {}
            return response
        
        
        if flag == 1:
            # try:
            history_status_path = status['run_history_path']
            history_status_path = os.path.join(settings.BASE_DIR, history_status_path).replace('\\', '/')
            #print('================================')
            #print('open history status:')
            #print(history_status_path)
            his_data = pd.read_csv(history_status_path)
            history_status = his_data.to_dict('list')
            history_status['epoch'] = list(range(len(history_status['epoch'])))
            status['run_history_path'] = history_status
            # except:
            #     pass
                # status['run_history_path'] = {}
        else:
            status['run_history_path'] = {}
        
        # 返回状态信息
        response['code'] = 200
        response['message'] = 'Success!'
        response['result'] =status
        
        # print(result)
        # print(response)

        return response