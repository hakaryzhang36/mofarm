'''
当前训练节点配置
'''

import json
from os import stat
import time
from urllib import response
import requests
import psutil
import pynvml
import threading
from .time_format import time_format


CONTROLLER_IP = '0.0.0.0'
CONTROLLER_PORT = '9000' 

SLAVE_IP = '0.0.0.0'                     
SLAVE_PROT = '8000' 

FM_IP = '0.0.0.0'
FM_PORT = 12307

is_slave = True     # 设置当前节点是否为训练节点

class Slave:
    def __init__(self) -> None:
        self.id = ''                                    # 节点id，主服务器分配
        self.ip = SLAVE_IP                              # 节点ip
        self.port = SLAVE_PROT                          # 节点port
        self.CPU_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]     # CPU状态，暂定为记录10条按时间顺序的CPU占用率
        # self.GPU_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]     # GPU状态
        self.GPU_s = {}
        self.MEM_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]     # 内存状态
        self.runtime_s = 'FREE'                         # 运行状态（FREE空闲，RUNNING运行中）
        self.alive_timestamp = str(time.time())         # 生存时间戳
        self.controller_ip = CONTROLLER_IP              # 主服务器ip
        self.controller_port = CONTROLLER_PORT          # 主服务器port
        self.GPU_id = 0                                 # test
        self.task_list = []                             # 运行任务列表
        return

    def add_task(self, task, t:threading.Thread):
        self.task_list.append((task, t))
        return

    def state_cheak(self,):
        '''
        【弃用】监控节点状态，若超负荷则按策略中止任务
        '''
        self.update_state_all()
        print(self.GPU_s)
        if self.GPU_s[0]['GPU']['GPU_rate'] > 95:
            task, t = self.task_list.pop(-1)     # 最新的任务
            # 中止训练进程
            ident = t.ident
            import inspect
            import ctypes
            """raises the exception, performs cleanup if needed"""
            tid = ctypes.c_long(tid)
            if not inspect.isclass(SystemExit):
                exctype = type(SystemExit)
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
            if res == 0:
                raise ValueError("invalid thread id")
            elif res != 1:
                # """if it returns a number greater than one, you're in trouble,
                # and you should call it again with exc=NULL to revert the effect"""
                ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
                raise SystemError("PyThreadState_SetAsyncExc failed")
            
            # 更新任务状态至主服务器
            task['status'] = 'STOP'
            task['start_time'] = -1
            self.send_task_status(task=task, status='STOP')
        

    def get_config(self):
        config = {
            'id' : self.id,
            'ip' : self.ip,
            'port' : self.port,
            'CPU_s' : self.CPU_s,
            'GPU_s' : self.GPU_s,
            'MEM_s' : self.MEM_s,
            'runtime_s' : self.runtime_s,
            'alive_timestamp' : self.alive_timestamp,
            'controller_ip' : self.controller_ip,
            'controller_port' : self.controller_port
        }
        return config
    
    def get_controller_url(self):
        url = 'http://' + self.controller_ip + ':' + self.controller_port
        return url

    
    def update_alive(self):
        '''
        【弃用】更新时间戳
        '''
        data_json = {}
        self.alive_timestamp = str(time.time())
        data_json['id'] = self.id
        data_json['alive_timestamp'] = self.alive_timestamp

        url = self.get_controller_url() + '/MoFarmBackEnd/inter_connection/keep_alive'
        print('URL: ', url)
        res = requests.post(url, data=json.dumps(data_json))
        res_json = json.loads(res.content)
        print('更新时间戳操作：', res_json['code'])
        return
    
    def update_state_all(self):
        data_json = {}

        # update CPU_s
        self.CPU_s.pop(0)
        self.CPU_s.append(format(psutil.cpu_percent(), '.2f'))
        
        # update GPU_s
        pynvml.nvmlInit()
        GPUs = {}
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # 这里的0是GPU id
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        gpuUtilRate = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
        self.GPU_s['GPU_rate'] = gpuUtilRate
        
        # update MEM_s
        mem = psutil.virtual_memory()
        mem_used = mem.used
        mem_total = mem.total
        self.MEM_s.pop(0)
        self.MEM_s.append(format(mem_used / mem_total * 100, '.2f'))
        
        # update alive_timestamp
        self.alive_timestamp = str(time.time())

        return

    def send_config(self,):
        self.update_state_all()
        data = self.get_config()
        url = self.get_controller_url() + '/MoFarmBackEnd/inter_connection/update_slave_state_all'
        print(time_format(), '更新节点状态成功')
        requests.post(url, data=json.dumps(data))
        time.sleep(1)


    # def update_slave_running_config(self, t, project_id):
    #     while t.is_alive():
    #         print('运行中，正在发送状态信息')
    #         self.update_state_all()
    #         time.sleep(1)
    #     url = self.get_controller_url()
    #     data = {}
    #     for i in range(self.task_list.__len__):
    #         if self.task_list[i][0]
    #     data['id'] = self.id
    #     requests.post(url + '/MoFarmBackEnd/inter_connection/free_slave', data=json.dumps(data))
    #     print('训练完成，节点释放。')

    
    def login(self):
        print('这是训练节点')
        
        self.update_state_all()

        # 发送注册请求
        slave_config = self.get_config()
        url = self.get_controller_url() + '/MoFarmBackEnd/inter_connection/add_slave'
        print('发起请求 URL: ', url)
        res = requests.post(url, data=json.dumps(slave_config))
        res_json = json.loads(res.content)
        local_slave.id = res_json['id']
        print('节点已注册，分配id：', local_slave.id)
        return

    def logout(self):
        '''
        在主服务器上注销
        '''
        data_json = {}
        data_json['id'] = self.id
        url = self.get_controller_url() + '/MoFarmBackEnd/inter_connection/delete_slave/'
        print('URL: ', url)
        res = requests.post(url, data=json.dumps(data_json))
        res_json = json.loads(res.content)
        print('注销操作：', res_json['code'])
        return

        

    def keep(self,):
        while True:
            # 发送节点状态
            self.send_config()
            time.sleep(1)
            # # 检查负载
            # self.state_cheak()
            # # 检查任务列表情况
            # for i in range(len(self.task_list)):
            #     task = self.task_list[i][0]
            #     t = self.task_list[i][1]
            #     if not t.is_alive():
            #         self.task_list.pop(i)
            #         task['end_time'] = time.time()
            #         task['status'] = 'FINISH'
            #         self.send_task_status(task=task, status='FINISH')
    

# 节点初始化操作
local_slave = Slave()




