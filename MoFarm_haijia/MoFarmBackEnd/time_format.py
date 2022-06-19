'''
Author: zhj
Description: 一个命令行输出格式化时间戳的函数
'''

import datetime

def time_format():
    return '【' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f") + '】'