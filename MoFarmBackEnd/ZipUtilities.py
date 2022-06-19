'''
Author: your name
Date: 2022-03-18 14:37:41
LastEditTime: 2022-03-18 14:37:41
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /MoFarm/MoFarmBackEnd/ZipUtilities.py
'''
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
import filetype, hashlib
import json
# Create your views here.
import os
import zipstream

# 打包下载
class ZipUtilities(object):
    """
    将文件或者文件夹打包成ZIP格式的文件，然后下载，在后台可以通过response完成下载
    """
    zip_file = None

    def __init__(self):
        self.zip_file = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)

    def to_zip(self, file, name):
        if os.path.isfile(file):
            self.zip_file.write(file, arcname=os.path.basename(file))
        else:
            self.add_folder_to_zip(file, name)

    def add_folder_to_zip(self, folder, name):
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                self.zip_file.write(
                    full_path,
                    arcname=os.path.join(name, os.path.basename(full_path))
                )
            elif os.path.isdir(full_path):
                self.add_folder_to_zip(
                    full_path,
                    os.path.join(name, os.path.basename(full_path))
                )

    def close(self):
        if self.zip_file:
            self.zip_file.close()

