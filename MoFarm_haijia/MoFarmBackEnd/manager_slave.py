'''
主服务器，训练节点管理模块
'''

from django.conf import settings
import random
import string
import requests
from .time_format import time_format

'''
modified by zhj, 2022-4-29
训练节点状态信息
    - id：节点id（唯一索引）
    - ip：节点ip
    - port：节点后台端口
    - CPU_s：CPU状态（暂定记录占有率，整型）
    - GPU_s：GPU状态
    - MEM_s：内存状态
    - runtime_s：运行状态
    - alive_timestamp：生存时间戳，节点定期与主服务器打招呼
'''
SLAVE_DICT = {} # 训练节点状况信息，暂定本地缓存，减少数据库访问
free_slaves = [] # 空闲节点

class Slave():
    '''
    desc: 训练节点类
    '''
    def __init__(self, ip, port, CPU_s, GPU_s, MEM_s, runtime_s, alive_timestamp, controller_ip, controller_port):
        self.id = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        self.ip = ip
        self.port = port
        self.CPU_s = CPU_s
        self.GPU_s = GPU_s
        self.MEM_s = MEM_s
        self.runtime_s = runtime_s
        self.alive_timestamp = alive_timestamp
        self.controller_ip = controller_ip
        self.controller_port = controller_port
        self.weight = -float(self.GPU_s['GPU_rate'])   # 初始化权重
        return
    
    def reset_weight(self,):
        self.weight = -float(self.GPU_s['GPU_rate'])
        return
    
    def update_state_all(self, config):
            if config['alive_timestamp'] > self.alive_timestamp:
                self.alive_timestamp = config['alive_timestamp']
                self.runtime_s = config['runtime_s']
                self.CPU_s = config['CPU_s']
                self.MEM_s = config['MEM_s']
                self.GPU_s = config['GPU_s']
                self.weight = -float(self.GPU_s['GPU_rate'])

class SlaveManager(object):
    def __init__(self):
        self.overload = False
        return

    def add_slave(self, config):
        '''
        说明：新增一个节点
        参数：
            - config：节点配置
        返回：节点id
        '''
        slave = Slave(config['ip'], config['port'], config['CPU_s'], config['GPU_s'], config['MEM_s'], config['runtime_s'], config['alive_timestamp'], config['controller_ip'], config['controller_port'])
        print(time_format(), '生成新节点：({}, {}:{})'.format(slave.id, slave.ip, slave.port))
        SLAVE_DICT[str(slave.id)] = slave
        return slave.id

    def get_highest_weight_slave(self,):
        '''
        实现节点负载均衡
        '''
        if len(SLAVE_DICT) == 0:
            return None
        
        # 超载等待
        while self.overload == True:
            for id in SLAVE_DICT.keys():
                id = str(id)
                slave = SLAVE_DICT[id]
                if slave.GPU_s['GPU_rate'] < 99:
                    SLAVE_DICT[id].reset_weight()
                    self.overload = False

        # 加权轮询
        selected_id = ''
        for id in SLAVE_DICT.keys():
            id = str(id)
            if selected_id == '' and float(SLAVE_DICT[id].GPU_s['GPU_rate']) < 99:
                selected_id = id
            elif SLAVE_DICT[id].weight > SLAVE_DICT[selected_id].weight:
                selected_id = id


        shotcut = []
        for id, slave in SLAVE_DICT.items():
            shotcut.append((slave.weight, slave.GPU_s))
        print(time_format(), '选出节点：', selected_id, ', 全部节点：', shotcut)
        return SLAVE_DICT[selected_id]

            
    
    def delete_slave(self, id):
        '''
        说明：删除节点
        参数：
            - id：节点id
        返回：操作生效/无效
        '''
        if SLAVE_DICT.pop(id, default = False):
            return True
        else:
            print('节点尚未注册')
            return False

    def keep_alive(self, id, alive_timestamp):
        '''
        说明：更新节点生存时间戳
        参数：
            - id：节点id
            - alive_timestamp：生存时间戳
        返回：操作生效/无效
        '''
        id = str(id)
        if id in SLAVE_DICT.keys():
            if alive_timestamp > SLAVE_DICT[id].alive_timestamp:
                SLAVE_DICT[id].alive_timestamp = alive_timestamp
                print(time_format(), '节点{}更新时间戳{}'.format(id, alive_timestamp))
            return True
        else:
            print('节点尚未注册')
            return False
    
    def update_slave_state_all(self, id:str, config):
        '''
        说明：更新节点全部状态信息
        参数：
            - id：节点id
            - config：节点配置
        返回：操作生效/无效
        '''
        id = str(id)
        if id in SLAVE_DICT.keys():
            SLAVE_DICT[id].update_state_all(config)
            print(time_format(), '更新节点{}状态成功'.format(id))
            return True
        else:
            print('节点尚未注册')
            return False
    
    
    def get_slave(self, id):
        '''
        Get a slave config.
        '''
        print('获取节点{}配置'.format(id))
        return SLAVE_DICT[str(id)]

    