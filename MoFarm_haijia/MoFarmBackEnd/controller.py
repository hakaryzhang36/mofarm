import datetime
import time
import json
import os
import requests
import threading
from django.conf import settings
from .manager_task import TaskManager
from .manager_slave import SlaveManager
from .models import MoFarmProject, MoFarmProjectStatus
from .time_format import time_format


class Controller():
    def __init__(self) -> None:
        return


    def handle_task(self, slave, task):
        '''
        交付任务
        '''
        if task != False:
            # 交付任务
            project = MoFarmProject.objects.get(id=task.project_id)

            json_path = project.config_path
            name = project.name
            print(json_path)

            project_type = project.project_type

            sys_path = os.path.join(
                settings.BASE_DIR, 'MoFarmBackEnd/config/projects', project_type, json_path).replace('\\', '/')
            print('opening the json:' + sys_path)

            config_json = ''
            with open(sys_path)as f:
                for line in f:
                    config_json = config_json + line
            project_json = json.loads(config_json)

            # 1 发送数据集[暂无]
            # project_json['name'] = project.name
            # for data_sourece in project_json['modules']:
            #     if data_sourece['name'] == 'data_source':
            #         dataset = open('', 'r')
            #         requests.post(socket + '/Dataset/', files=dataset)

            # 2 发送项目配置，启动项目
            print('正在交付... 任务', task.id, ' 节点', slave.id)
            data_json = {}
            data_json['project_json'] = project_json
            data_json['task_id'] = task.id
            data_json['project_id'] = task.project_id

            socket = 'http://' + slave.ip + ':' + slave.port
            res_data = requests.post(socket + '/MoFarmBackEnd/Project/run_project_slave', data = json.dumps(data_json))
            
            # 3 检查交付操作
            res_json = json.loads(res_data.content)
            if res_json['code'] == 200:
                print('任务交付成功')
                return True
            else:
                print('任务交付失败')
                return False

    def add_task_to_list(self, project_id):
        TaskManager().add_task(project_id)
        return

    
    def schedule(self):
        '''
        调度过程实现
        '''
        task_manager = TaskManager()
        if not task_manager.empty():
            
            slave = SlaveManager().get_highest_weight_slave()
        
            task = None
            if slave != None:
                task = task_manager.get_runable_task(GPU_rate=slave.GPU_s['GPU_rate'])
            
            if task != None:
                success = self.handle_task(slave, task)
                if success:
                    task_manager.update_task_status(task.id, 'RUNNING')
        
        return

    def keep(self, django_thread:threading.Thread):
        print(time_format(), 'Thread "Controller" start.')
        while django_thread.is_alive():
            self.schedule()
            time.sleep(5)