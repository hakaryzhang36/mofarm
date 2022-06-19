from django.test import TestCase

# Create your tests here.
import socket,time,struct,os
import threading
LOCAL_IP = '0.0.0.0'
PORT = 12307

 
  
def conn_thread(connection,address): 
  while True:
    try:
      connection.settimeout(600)
      fileinfo_size=struct.calcsize('128sl') 
      buf = connection.recv(fileinfo_size)
      if buf: #如果不加这个if，第一个文件传输完成后会自动走到下一句
        filename,filesize =struct.unpack('128sl',buf) 
        filename_f = filename.strip('\00')
        filenewname = os.path.join('e:\\',('new_'+ filename_f))
        print('file new name is %s, filesize is %s' %(filenewname,filesize))
        recvd_size = 0 #定义接收了的文件大小
        file = open(filenewname,'wb')
        print('stat receiving...')
        while not recvd_size == filesize:
          if filesize - recvd_size > 1024:
            rdata = connection.recv(1024)
            recvd_size += len(rdata)
          else:
            rdata = connection.recv(filesize - recvd_size) 
            recvd_size = filesize
          file.write(rdata)
        file.close()
        print('receive done')
        #connection.close()
    except socket.timeout:
      connection.close()
 
def recive_pth(sock):
    '''
    接收线程
        - path: pth file path
    '''
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
            print('Recived {} bytes...'.format(get))
        file.close()
        sock.send(b'copy')
        print(file_name, ' is recived.')
    return


def listen():
    '''
    监听主线程
    '''
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #定义socket类型
    s.bind((LOCAL_IP, PORT)) #绑定需要监听的Ip和端口号，tuple格式
    s.listen(1)
    while True:
        print('Thread "LISTEN" start !')
        sock, address = s.accept()
        print('Connected by ', address)
        thread = threading.Thread(target=recive_pth, args=(sock,)) #使用threading也可以
        thread.start()

def send_pth(file_name, file_dir):
    '''
    发送pth文件
    '''
    file_path = file_dir + file_name
    
    # 建立连接
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((LOCAL_IP, PORT))
    
    # 发送文件基本信息
    file_stats = os.stat(file_path)
    sock.send('{}|{}|{}'.format(file_stats.st_size, 'test.pth', file_dir + 'test.pth').encode())
    
    # 发送文件
    print('Sending ', file_name)
    if 'ok' == sock.recv(1024).decode():
        file = open(file_path, 'rb')
        while True:
            file_data = file.read(1024)
            if not file_data:
                break
            sock.send(file_data)
    
    if 'copy' == sock.recv(1024).decode():
        print('{} send finish !'.format(file_name))
    file.close()
    sock.close()

if __name__ == '__main__':
    # t1 = threading.Thread(target=listen)
    # t1.daemon = True
    # t1.start()
    # time.sleep(1)
    # send_pth('classifier_1.pth', './MoFarmBackEnd/config/models/')
    # while True:
    #     print('main is running.')
    #     time.sleep(1)
    l = [1,2,3]
    for k in l:
      k=1
    print(l)