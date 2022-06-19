import socket
import os
import threading
from .time_format import time_format


CONTROLLOR_FM_IP = '0.0.0.0'
CONTROLLOR_FM_PORT = 12308

# CONTROLLOR_FM_IP = '0.0.0.0'
# CONTROLLOR_FM_PORT = 12308


def init_contorllor_file_listener(django_thread:threading.Thread):
    '''
    文件传输监听线程
    '''
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    #定义socket类型
    s.bind((CONTROLLOR_FM_IP, CONTROLLOR_FM_PORT))          #绑定需要监听的Ip和端口号，tuple格式
    s.listen(1)
    while django_thread.is_alive():
        print(time_format(), 'Thread "File Manager Service" start, running on ({}:{})'.format(CONTROLLOR_FM_IP, CONTROLLOR_FM_PORT))
        sock, address = s.accept()
        print('Connected by ', address)
        thread = threading.Thread(target=ContorllorFileManager().recive_pth, args=(sock,)) #使用threading也可以
        thread.start()
    s.close()
    

    

class ContorllorFileManager:
    def __init__(self) -> None:
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

        # 发送文件信息头部
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

    def recive_pth(self, sock:socket.socket):
        print('Thread "RECIVE" start !')
        head = sock.recv(1024)
        length, file_name, path = head.decode().split('|')
        if length and file_name:
            file = open(path, 'wb')
            print('File Path: ', path)
            print('File Length: ', length,)
            print('File Name: ', file_name)
            sock.send(b'ok')
            total = int(length)
            get = 0
            # 接收pth
            print(file_name, ' is reciving...')
            while get < total:
                data = sock.recv(1024)
                get += len(data)
                file.write(data)
                # print('Recived {} bytes...'.format(get))
            file.close()
            sock.send(b'copy')
            sock.close()
            print(file_name, ' is recived.')
        return
            
