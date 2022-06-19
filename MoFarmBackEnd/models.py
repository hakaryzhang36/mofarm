'''
Author: your name
Date: 2022-01-05 14:50:11
LastEditTime: 2022-03-24 11:14:54
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /SoFuse/SoFuseBackEnd/models.py
'''
from turtle import update
from django.db import models
import datetime
'''
数据集元信息
id
数据集名称
说明
csv路径
数据集类型（text|image|video|timeseq|audio|graph)
'''
class MoFarmDataset(models.Model):
    id = models.AutoField (primary_key = True,verbose_name="ID")
    name = models.CharField(max_length=100,unique=True,verbose_name="数据集名称")
    desc = models.CharField(max_length=200,default="",verbose_name="说明")
    dataset_path = models.CharField(max_length=200,default="",verbose_name="CSV路径")
    type = models.CharField(max_length=100,default="",verbose_name="数据集类型")
    created_time = models.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_time = models.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


'''
项目元信息表
id
项目名称
说明
配置jason文件路径
运行状态,以jason字符串的形式来说明状态。
#持续对比观测状态配置,以jason字符串的形式来说明状态。
'''
class MoFarmProject(models.Model):
    id = models.AutoField (primary_key = True,verbose_name="ID")
    name = models.CharField(max_length=100,unique=True,verbose_name="项目名称")
    desc = models.CharField(max_length=200,default="",verbose_name="说明")
    project_type = models.CharField(max_length=100,default="",verbose_name="所属算法类型（目标识别/图片分类/数据预测/异常检测）")
    config_path = models.CharField(max_length=200,default="",verbose_name="配置jason文件路径")
    origin_config_path = models.CharField(max_length=200,default="",verbose_name="前端源配置jason文件路径")
    status = models.CharField(max_length=1000,default="",verbose_name="运行状态:未运行/训练/测试")
    created_time = models.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_time = models.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),verbose_name="更新时间")
    
    #status_compare = models.CharField(max_length=1000,default="",verbose_name="持续对比观测状态配置")


'''
模块元信息表
id
模块名称
模块的类型
模块的jason文件路径
'''
class MoFarmModule(models.Model):
    id = models.AutoField (primary_key = True,verbose_name="ID")
    name = models.CharField(max_length=100,verbose_name="模块名称")
    desc = models.CharField(max_length=200,default="",verbose_name="说明")
    type = models.CharField(max_length=100,default="",verbose_name="模块的类型")
    module_path = models.CharField(max_length=200,default="",verbose_name="模块的jason文件路径")
    
'''
模型表的设置：
id
模型名称
对应模块ID
说明
pth文件的路径
'''
class MoFarmModel(models.Model):
    id = models.AutoField (primary_key = True,verbose_name="ID")
    module_id = models.IntegerField (verbose_name="模块ID", default=-1)
    name = models.CharField(max_length=100,default="",verbose_name="模型名称", unique=True)
    model_path = models.CharField(max_length=200,default="",verbose_name="pth文件的路径")


'''图片数据存放表'''
class MoFarmImagesDataset(models.Model):
    id = models.AutoField (primary_key = True,verbose_name="ID")
    datasetname = models.CharField(max_length=100,verbose_name="数据集名称")
    image_name = models.CharField(max_length=100,verbose_name="图片名称")
    image_md5 = models.CharField(max_length=256,verbose_name="图片的md5")
    tag_status = models.CharField(default='0',max_length=1,verbose_name="标注状态,0 未标注  1已标注")
    image_size = models.CharField(max_length=32,verbose_name="图片宽高 :(宽,高)")
    image_type = models.CharField(max_length=10,verbose_name="图片文件类型:jpg/png/tif")
    label_msg = models.TextField(verbose_name="图片标注信息")
    ratio = models.FloatField(max_length=20,verbose_name="图片缩放比例")

    @classmethod
    def get_image_by_md5_dataset(cls,md5,dataset):
        try:
            return MoFarmImagesDataset.objects.filter(datasetname=dataset,image_md5=md5).first()
        except Exception as e:
            return None
    
    @classmethod
    def getBoxes(cls, name, md5):
        try:
            return MoFarmImagesDataset.objects.values("label_msg").filter( datasetname=name, 
                                                     image_md5=md5).first()
        except Exception as e:
            return None


'''
项目运行状态
'''
class MoFarmProjectStatus(models.Model):
    id = models.AutoField (primary_key = True,verbose_name="ID")
    projectname = models.CharField(max_length=100,verbose_name="项目方案名称")
    status = models.CharField(max_length=100,verbose_name="运行状态说明(未运行/训练/测试)")
    total_progress = models.CharField(max_length=100,verbose_name="运行总进度")
    run_real_time_msg = models.CharField(max_length=100,verbose_name="当前运行轮次的指标信息")
    run_history_path = models.CharField(max_length=100,verbose_name="运行状态历史信息json文件路径")

'''模块模型对应关系表'''
class MoFarmModelModuleRelations(models.Model):
    module_id = models.IntegerField (verbose_name="模块ID")
    module_name = models.CharField(max_length=100,verbose_name="模块名称")
    model_id = models.IntegerField (verbose_name="模型ID")
    model_name = models.CharField(max_length=100,verbose_name="模型名称")  
