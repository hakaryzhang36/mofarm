import socket
import os
import threading

FM_IP = '0.0.0.0'
FM_PORT = 12307

CONTROLLOR_FM_IP = '0.0.0.0'
CONTROLLOR_FM_PORT = 12308


class SlaveFileManager:
    def __init__(self) -> None:
        self.local_FM_ip = FM_IP
        self.loacl_FM_port = FM_PORT
        self.controllor_FM_ip = CONTROLLOR_FM_IP
        self.controllor_FM_port = CONTROLLOR_FM_PORT
        
        
    def send_pth(self, file_name, file_dir):
        '''
        发送pth文件
        '''
        file_path = file_dir + file_name
        
        # 建立连接
        sock_send = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock_send.connect((self.controllor_FM_ip, self.controllor_FM_port))

        # 发送文件基本信息
        file_stats = os.stat(file_path)
        sock_send.send('{}|{}|{}'.format(file_stats.st_size, 'test.pth', file_dir + 'test.pth').encode())
        
        # 发送文件
        print('Sending ', file_name)
        if 'ok' == sock_send.recv(1024).decode():
            file = open(file_path, 'rb')
            while True:
                file_data = file.read(1024)
                if not file_data:
                    break
                sock_send.send(file_data)
        
        if 'copy' == sock_send.recv(1024).decode():
            print('{} send finish !'.format(file_name))
            file.close()
            return True
        else:
            return False 
            
    def wait_pth(self, t, project_json):
        print('等待pth生成')
        while t.is_alive():
            continue
        for module in project_json['modules']:
            if 'model' in module['config']:
                pth_name = module['config']['model']
                import os
                if os.path.exists("./MoFarmBackEnd/config/models/" + pth_name):
                    r = self.send_pth(pth_name, "./MoFarmBackEnd/config/models/")
                    if r:
                        print('pth文件传输成功')
                    else:
                        print('pth文件传输出错')