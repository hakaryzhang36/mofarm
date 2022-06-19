from concurrent.futures import thread
from .manager_slave import SLAVE_DICT, SlaveManager
from .time_format import time_format
import time
import json
import requests
import threading
import random, string

TASK_LIST = []

class Task():
    def __init__(self, project_id):
        self.id = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        self.created_time = time.time()
        self.start_time = -1
        self.end_time = -1
        self.project_id = project_id
        self.max_gpu_need = 0
        self.status = 'READY'

class TaskManager():
    def empty(self):
        if len(TASK_LIST) == 0:
            return True
        else: 
            return False

    def add_task(self, project_id):
        '''
        添加任务
        '''
        task = Task(project_id)
        TASK_LIST.append(task)
    
    def get_runable_task(self, GPU_rate):
        '''
        调度任务，返回一个可启动任务
        '''
        if len(TASK_LIST) :
            # 选出任务
            for i in range(len(TASK_LIST)):
                if TASK_LIST[i].status != 'RUNNING' and TASK_LIST[i].status != 'FINISH' and TASK_LIST[i].max_gpu_need < 100 - GPU_rate:
                    print(time_format(), '选出任务', TASK_LIST[i].id, ' 序号：', i, ' 项目', TASK_LIST[i].project_id)
                    return TASK_LIST[i]
        else:
            # 任务队列为空
            return None
        # 无合适任务
        return None
            
    def update_task_status(self, task_id:str, status:str):
        '''
        修改任务状态
        '''
        for i in range(len(TASK_LIST)):
            if TASK_LIST[i].id == task_id:
                TASK_LIST[i].status == status
                if TASK_LIST[i].status == 'FINISH':
                    print(time_format(), '任务 ', TASK_LIST[i].id, ' 完成')
                    TASK_LIST.pop(i)
                break
    






