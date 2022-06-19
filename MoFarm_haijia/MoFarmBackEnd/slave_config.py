'''
当前训练节点配置
'''

import json
import time
from urllib import response
import requests
import psutil
import pynvml
import threading


CONTROLLER_IP = '127.0.0.1'
CONTROLLER_PORT = '8080' 

SLAVE_IP = '127.0.0.1'                     
SLAVE_PROT = '1234' 

FM_IP = '0.0.0.0'
FM_PORT = 12307

is_slave = True     # 设置当前节点是否为训练节点

class Slave:
    def __init__(self) -> None:
        self.id = ''                                    # 节点id，主服务器分配
        self.ip = SLAVE_IP                              # 节点ip
        self.port = SLAVE_PROT                          # 节点port
        self.CPU_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]     # CPU状态，暂定为记录10条按时间顺序的CPU占用率
        self.GPU_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]     # GPU状态
        self.MEM_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]     # 内存状态
        self.runtime_s = 'FREE'                         # 运行状态（FREE空闲，RUNNING运行中）
        self.alive_timestamp = str(time.time())         # 生存时间戳
        self.controller_ip = CONTROLLER_IP              # 主服务器ip
        self.controller_port = CONTROLLER_PORT          # 主服务器port
        return

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

    def login(self):
        print('这是训练节点')
        slave_config = self.get_config()
        url = self.get_controller_url() + '/MoFarmBackEnd/inter_connection/add_slave/'
        print('URL: ', url)
        res = requests.post(url, data=json.dumps(slave_config))
        res_json = json.loads(res.content)
        slave.id = res_json['id']
        print('节点已注册，分配id：', slave.id)
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
    
    def update_alive(self):
        data_json = {}
        self.alive_timestamp = str(time.time())
        data_json['id'] = self.id
        data_json['alive_timestamp'] = self.alive_timestamp

        url = self.get_controller_url() + '/MoFarmBackEnd/inter_connection/keep_alive/'
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
        handle = len(pynvml.nvmlDeviceGetHandleByIndex(0))  # 这里的0是GPU id
        memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        self.GPU_s.pop(0)
        self.GPU_s.append(format(memory_info.used / memory_info.total * 100, '.2f'))
        # update MEM_s
        mem = psutil.virtual_memory()
        mem_used = mem.used
        mem_total = mem.total
        self.MEM_s.pop(0)
        self.MEM_s.append(format(mem_used / mem_total * 100, '.2f'))
        # update alive_timestamp
        self.alive_timestamp = str(time.time())
        
        data_json['config'] = self.get_config()

        url = self.get_controller_url() + '/MoFarmBackEnd/inter_connection/update_slave_state_all/'
        print('URL: ', url)
        res = requests.post(url, data=json.dumps(data_json))
        res_json = json.loads(res.content)
        print('更新状态操作：', res_json['code'])
        return

    def update_slave_running_config(self, t):
        while t.is_alive():
            print('运行中，正在发送状态信息')
            self.update_state_all()
            time.sleep(3)

    def send_pth(self):
        return
    

# 节点初始化操作
slave = Slave()
# slave.login()




