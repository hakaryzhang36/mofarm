'''
Author: your name
Date: 2022-01-05 15:45:43
LastEditTime: 2022-04-11 23:47:30
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /SoFuse/SoFuseBackEnd/urls.py
'''

from django.urls import path, include
from .views_dataset import get_datasets,create_dataset,upload_data_record,upload_label_file,search_dataset_by_keyword
from .views_dataset import upload_label_online,get_data_by_page,delete_label_record,get_datasets_by_page_v2
from .views_dataset import delete_dataset,get_image_by_page,download_dataset,upload_voc_classes,get_voc_classes,update_label

from .views_module import test_module, get_module, get_modules, clear_module,get_modules_v2
from .views_model import test_model, get_model, clear_model,add_model
from .views_project import get_project_status_all, test_project,get_projects, get_project_config, get_project_status_all, get_project_status_realtime
from .views_project import update_project,clear_project,run_project,update_project_status,get_project_type
from .views_project import add_project,get_projects_by_page,get_projects_by_keyword,delete_project
from .menu_start import start_menu

from .views_slave import add_slave, delete_slave, update_slave_state_all, keep_alive
from .manager_file_controllor import init_contorllor_file_listener
from .view_task import updata_task_status
import threading
from .manager_task import TaskManager
from .manager_project import ProjectManager
from .controller import Controller
import time

django_thread = threading.current_thread()
listener = threading.Thread(target=init_contorllor_file_listener, args=(django_thread,))    # 文件传输监听线程
schedule_controller = threading.Thread(target=Controller().keep, args=(django_thread,))           # 调度控制器后台线程
listener.start()
schedule_controller.start()

# def test():
#     input('回车载入任务...')
#     for i in range(2):
#         ProjectManager().run_project_controller(i)
#         time.sleep(5)
# t = threading.Thread(target=test, args=())
# t.isDaemon = True
# t.start()

#   菜单
# start_menu()

urlpatterns = [
    # path('test_dataset/', test_dataset),    

    # motified by lgm
    # 2022/3/14
    path('Data/create_dataset/', create_dataset),
    path('Data/upload_data_record/', upload_data_record),
    path('Data/upload_label_file/', upload_label_file),
    path('Data/upload_label_online/',upload_label_online),    
    path('Data/get_data_by_page/',get_data_by_page),    
    path('Data/delete_dataset/',delete_dataset),
    path('Data/delete_label_record/',delete_label_record),
    path('Data/get_datasets_by_page/',get_datasets_by_page_v2),
    
    # motified by lgm
    # 2022/3/28
    # 上传数据集标签类别
    path('Data/upload_voc_classes/',upload_voc_classes),
    path('Data/get_voc_classes/',get_voc_classes),
    #   统计标签
    path('Data/update_label/',update_label),
    #   标注页面的分页查看
    path('Data/get_image_by_page/',get_image_by_page),
    
    
    path('Data/download_dataset/',download_dataset),
    
    path('Data/search_dataset_by_keyword/',search_dataset_by_keyword),    
    # path('clear_dataset/', clear_dataset),
    # path('get_dataset/', get_dataset),
    path('Data/get_datasets/', get_datasets),

    path('test_module/', test_module),
    path('Module/get_modules/', get_modules),
    path('Module/get_modules_v2/', get_modules_v2),
    # path('clear_module/', clear_module),# 清除所有模块 太危险！
    path('Module/get_module/', get_module),


    path('test_model/', test_model),
    path('clear_model/', clear_model),
    path('get_model/', get_model),
    path('add_model/', add_model),

    # modified by csj, 2022-3-22
    path('test_project/', test_project),   
    path('Project/add_project/', add_project),
    path('clear_project/', clear_project),    
    path('Project/get_project_config/', get_project_config),
    # path('get_project_status/', get_project_status),
    path('Project/update_project/', update_project),
    # path('run_project/', run_project),
    path('update_project_status/', update_project_status),
    
    # modified by lgm, 2022-3-22
    path('Project/get_projects/', get_projects),
    path('Project/get_projects_by_page/', get_projects_by_page),
    path('Project/get_projects_by_keyword/', get_projects_by_keyword),
    path('Project/delete_project/', delete_project),
    # modified by csj, 2022-4-11
    path('Project/get_project_status_all/', get_project_status_all),
    path('Project/get_project_status_realtime/', get_project_status_realtime),
    path('Project/run_project/', run_project),
    path('Project/get_project_types/', get_project_type),
    
    # 训练节点管理
    path('inter_connection/add_slave', add_slave),
    path('inter_connection/delete_slave', delete_slave),
    path('inter_connection/update_slave_state_all', update_slave_state_all),
    path('inter_connection/keep_alive', keep_alive),
    path('inter_connection/update_task_status', updata_task_status)
    
]
