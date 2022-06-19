import threading, json, os, requests
from .models import MoFarmProject
from .factory_project import ProjectFactory
from .manager_file_slave import SlaveFileManager
from .slave_config import local_slave as loacl_slave
from .time_format import time_format

TASK_LIST = []

class TaskInSlave():
    def __init__(self, task_id, project_id, project_json) -> None:
        self.task_id = str(task_id)
        self.project_id = str(project_id)
        self.project_json = project_json

    def start(self):
        # 启动任务
        project = MoFarmProject.objects.get(id=self.project_id)
        name = project.name
        project_factory = ProjectFactory(name)
        project_factory.parse_json(json.dumps(self.project_json))
        print ('building project...')
        project_factory.build_project()
        project_factory.draw_project()
        t = project_factory.run_project() # t为训练进程

        while t.is_alive():
            continue
        
        
        for module in self.project_json['modules']:
            if 'model' in module['config']:
                pth_name = module['config']['model']
                if os.path.exists("./MoFarmBackEnd/config/models/" + pth_name):
                    # 生成pth文件，训练进程正常结束时
                    print(time_format(), '任务', self.task_id, '训练完成，开始发送文件')
                    r = SlaveFileManager().send_pth(pth_name, "./MoFarmBackEnd/config/models/")
                    if r:
                        print(time_format(), 'pth文件传输成功')
                        data_json = {}
                        data_json['task_id'] = self.task_id
                        data_json['status'] = 'FINISH'
                        socket = loacl_slave.get_controller_url()
                        res_data = requests.post(socket + '/MoFarmBackEnd/inter_connection/update_task_status', data = json.dumps(data_json))
                    else:
                        print('pth文件传输出错')
                else:
                    # 没有生成pth文件，训练进程没有正常结束时
                    data_json = {}
                    data_json['task_id'] = self.task_id
                    data_json['status'] = 'READY'
                    socket = loacl_slave.get_controller_url()
                    res_data = requests.post(socket + '/MoFarmBackEnd/inter_connection/update_task_status', data = json.dumps(data_json))

