'''
Author: lgm
Date: 2022-03-14 15:59:09
LastEditTime: 2022-04-21 16:51:29
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /MoFarm/MoFarmBackEnd/views_dataset.py
'''

from ast import literal_eval
from django.http import StreamingHttpResponse
from django.test import tag
from .manager_dataset import DatasetManager
from .models import MoFarmDataset, MoFarmImagesDataset
from django.shortcuts import render, HttpResponse
import os
import json
from django.conf import settings
import hashlib
import math
import xml.etree.ElementTree as ET
import filetype
import datetime
import pandas as pd
from PIL import Image
from django.utils.http import urlquote
import shutil
from .ZipUtilities import ZipUtilities
from .check import request_verify, response_failure
from .jpg2base64 import img_zip2base64
# Create your views here.

'''
数据型接口
modified by lgm
2022-3-14
'''


@request_verify('post', ['dataSetName', 'desc', 'dataType'])
def create_dataset(request):
    response = {}
    manager = DatasetManager()
    paramslist = request.body
    json_data = json.loads(paramslist, strict=False)
    dataset_name = json_data["dataSetName"]  # 数据集名称,ais,gis,...
    desc = json_data["desc"]  # 数据集描述
    # 数据集类型 （text|image|video|timeseq|audio|graph)
    dataType = json_data["dataType"]

    inheritDataSet = json_data["inheritDataSet"]  # 是否继承原有的数据集

    #   检测是否有存在的数据集
    src_dataset = manager.get_dataset(dataset_name)
    if src_dataset:
        response['code'] = 401
        response['message'] = 'the dataset is exist!'
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

    if dataType not in ('text', 'image', 'video', 'timeseq', 'audio', 'graph','remote_sensing'):
        response['code'] = 402
        response['message'] = 'the dataType is error!'
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

    # 写库
    manager.add_dataset(dataset_name, desc, dataType)
    if inheritDataSet != "":
        src_path = os.path.join(
            settings.WEB_DATA_SERVER_ROOT, dataType, inheritDataSet)
        if not os.path.exists(src_path):
            response['code'] = 200
            response['message'] = 'Fail!the dataset do not have data,only create new dataset!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        target_path = os.path.join(
            settings.WEB_DATA_SERVER_ROOT, dataType, dataset_name)
        copydir(src_path, target_path)   # 复制文件夹
        MoFarmDataset.objects.filter(
            name=dataset_name).update(dataset_path=os.path.join(dataType, dataset_name))
        if dataType == 'image':  # 如果继承的数据集是图像类需要遍历写入图片信息库
            update_img_database(dataset_name)
    else:
        MoFarmDataset.objects.filter(
            name=dataset_name).update(dataset_path=os.path.join(dataType, dataset_name))
    response['code'] = 200
    response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

# 上传一个数据样本文件


def upload_data_record(request):
    response = {}
    dataset_name = request.POST.get("dataSetName", None)  # 数据集名称,ais,gis,...
    file = request.FILES.get("file", None)  # 单文件,.getList():多文件

    manager = DatasetManager()
    src_dataset = manager.get_dataset(dataset_name)

    if not src_dataset:
        response['code'] = 404
        response['message'] = 'the dataset is not found!'
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

    # 获取文件扩展名
    ext = os.path.splitext(file.name)[-1]
    # 计算文件md5
    md5 = pCalculateMd5(file)
    dataType = MoFarmDataset.objects.filter(name=dataset_name).first().type
    dataset_path = os.path.join(
        settings.WEB_DATASET_SERVER_ROOT, dataType, dataset_name)
    # 创建数据文件夹
    if not os.path.exists(dataset_path):
        os.mkdir(dataset_path)
    if dataType == 'image':

        if not ext in ['.jpg', '.png']:
            response['code'] = 403
            response['message'] = 'the file type must be *.jpg/*.png!but upload file type is {:}'.format(
                ext)
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        jpeg_path = dataset_path+settings.UPLOAD_IMAGE_SERVER_PATH
        annotations_path = dataset_path+settings.ANNOTATION_SERVER_PATH
        if not os.path.exists(jpeg_path):
            os.makedirs(jpeg_path)
            os.makedirs(annotations_path)

        save_path = os.path.join(jpeg_path, md5+ext)
        importImage = MoFarmImagesDataset.get_image_by_md5_dataset(
            md5, dataset_name)
        if importImage:   # 文件已存在
            response['code'] = 404
            response['message'] = 'The file had already exist!'
            response['state'] = 'Fail'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        # 导入时获取图片尺寸放入
        img_pillow = Image.open(file)
        img_width = img_pillow.width  # 图片宽度
        img_height = img_pillow.height  # 图片高度
        imgsize = str(img_width)+','+str(img_height)
        # 检测通过 创建新的image对象
        importImg = MoFarmImagesDataset()
        importImg.image_name = file.name
        importImg.image_md5 = md5
        importImg.image_size = imgsize
        importImg.datasetname = dataset_name
        importImg.image_type = ext
        importImg.ratio = 1.0
        importImg.save()
    elif dataType == 'text':
        if ext in ['xls', 'xlsx']:
            response['code'] = 403
            response['message'] = 'the file type must be csv!but upload file type is {:}'.format(
                ext)
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
        save_path = os.path.join(dataset_path, dataset_name+ext)
    else:

        save_path = os.path.join(dataset_path, md5+ext)

    #   分块写入文件
    with open(save_path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)
        f.close()

    MoFarmDataset.objects.filter(name=dataset_name).update(
        dataset_path=os.path.join(dataType, dataset_name), updated_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    response['code'] = 200
    response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


#   上传一个数据样本的标注文件
def upload_label_file(request):
    response = {}
    if request.method == 'POST':

        # 数据集名称,梅州五华现场图片,...
        datasetname = request.POST.get("dataSetName", None)
        label_file = request.FILES.get("labelFile", None)  # 单文件,.getList():多文件
        flag = (datasetname, label_file)
        if not all(flag):
            response['code'] = 401
            response['message'] = "加载失败! 传递的参数存在缺失!"
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        filename, ext = os.path.splitext(label_file.name)
        if ext not in ['.xml']:  # 过滤非xml文件
            response['code'] = 401
            response['message'] = 'Wrong upload file type! It needs the *.xml!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
        annotation_save_dir = settings.WEB_DATASET_SERVER_ROOT + \
            'image/' + datasetname + settings.ANNOTATION_SERVER_PATH
        # 读取xml文件对应图片的md5
        imgfilename = filename+'.jpg'
        importImg = MoFarmImagesDataset.objects.filter(
            datasetname=datasetname, image_name=imgfilename).first()
        if not importImg:
            response['code'] = 4001
            response['message'] = 'image is not exist,place import image!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
        md5 = importImg.image_md5
        xml_file_name = md5+'.xml'

        xml_save_path = os.path.join(annotation_save_dir, xml_file_name)
        print(xml_save_path)
        with open(xml_save_path, 'wb+') as f:
            for chunk in label_file.chunks():
                f.write(chunk)
            f.close()
        # 读取保存的xml文件将标注信息写入数据库
        tree = ET.parse(xml_save_path)
        root = tree.getroot()
        # 存储图片的长宽 img_size
        # 异常处理
        try:
            width = root.find("size").find("width").text
            height = root.find("size").find("height").text
        except Exception as e:
            # width=2560
            # height=1440
            response['code'] = 4004
            response['message'] = 'xml file is not saved!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        img_size = width+','+height
        # 存储标注信息到字典列表

        # modified by lgm
        #  2022-3-15
        # 开始仅支持annotation,目前已兼容labelimg——doc
        bndboxes = []

        # annotation格式
        if root.tag == 'annotation':
            for item in root.findall('object'):
                dict = {}
                dict['label'] = item.find('name').text.replace(' ', '')
                dict['xmin'] = int(item.find('bndbox').find('xmin').text)
                dict['ymin'] = int(item.find('bndbox').find('ymin').text)
                dict['xmax'] = int(item.find('bndbox').find('xmax').text)
                dict['ymax'] = int(item.find('bndbox').find('ymax').text)
                bndboxes.append(dict)
        #  doc格式
        elif root.tag == 'doc':
            object = root.find("outputs").find('object')

            for item in object.findall('item'):
                dict = {}
                item.find('name').text = item.find(
                    'name').text.replace(' ', '')
                dict['label'] = item.find('name').text.replace(' ', '')
                dict['xmin'] = int(item.find('bndbox').find('xmin').text)
                dict['ymin'] = int(item.find('bndbox').find('ymin').text)
                dict['xmax'] = int(item.find('bndbox').find('xmax').text)
                dict['ymax'] = int(item.find('bndbox').find('ymax').text)
                bndboxes.append(dict)

        MoFarmImagesDataset.objects.filter(
            datasetname=datasetname, image_md5=md5).update(tag_status='1', label_msg=bndboxes)
        response['code'] = 200
        response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

#   分页查询数据


@request_verify('get', ['dataSetName'])
def get_data_by_page(request):
    response = {}
    if request.method == 'GET':
        dataset = request.GET.get("dataSetName", None)
        try:
            page_number = int(request.GET.get('page_number'))
        except Exception as e:
            page_number = 1
        try:
            page_size = int(request.GET.get('page_size'))
        except Exception as e:
            page_size = 12

        exist = MoFarmDataset.objects.filter(name=dataset).first()
        if not exist:
            response['code'] = 404
            response['message'] = 'Fail!dataset is not found'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        dataType = MoFarmDataset.objects.filter(name=dataset).first().type
        if not dataType:
            response['code'] = 404
            response['message'] = 'the dataType is not found!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        if dataType == 'image':  # 图片查询
            showImgAll = MoFarmImagesDataset.objects.filter(
                datasetname=dataset).first()
            if not showImgAll:  # 分类不存在
                response['code'] = 200
                response['message'] = 'Failed! The dataset classes of images does not exist!'
                response['dataType'] = dataType
                show_images = {
                    "total_pics": 0,
                    "total_pages": 0,
                    "tagging_imgs": []
                }
                response['images'] = show_images
                return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

            # 展示所有图片
            total_pics = MoFarmImagesDataset.objects.filter(
                datasetname=dataset).count()
            # 已标注图片数量
            tagging_pics = MoFarmImagesDataset.objects.filter(
                datasetname=dataset, tag_status='1').count()
            total_pages = math.ceil(total_pics / page_size)
            print(total_pics)
            if page_number > total_pages:
                page_number = total_pages

            image_all = MoFarmImagesDataset.objects.filter(datasetname=dataset)\
                .values('image_md5', 'label_msg', 'image_type', 'image_size', 'ratio')\
                .order_by('id')  # id升序

            # 当前游标位置
            cursor = (page_number - 1) * page_size

            if page_number == total_pics:

                if total_pics == 1:    # 当只有一张时不切片
                    results = [image_all[cursor]]
                else:
                    results = image_all[cursor:total_pics - 1]
            else:
                results = image_all[cursor:cursor + page_size]
            # 保存分页数据
            tagging_imgs = []
            
            dataset_path = os.path.join(
            settings.WEB_DATA_SERVER_ROOT, dataType, dataset, "model_data")

            voc_classes_path = os.path.join(dataset_path, 'voc_classes.txt')
            voc_classes = []
            if os.path.exists(voc_classes_path):
                with open(voc_classes_path, 'r') as f:
                    for line in f.readlines():
                        line = line.strip('\n')
                    # if data !="\n":
                        voc_classes.append(line)
                f.close()
            print(voc_classes)
            for var in results:
                md5s = var['image_md5']
                try:
                    labelboxes = literal_eval(var['label_msg'])
                except Exception as e:
                    labelboxes = []
                imagename = md5s+var['image_type']
                # 内网访问
                image_web_path = 'http://' + settings.WEB_HOST_NAME + \
                    settings.WEB_DATA_SERVER_PATH + '/' + dataType + \
                    '/' + dataset + settings.UPLOAD_IMAGE_SERVER_PATH
                image_web_file = os.path.join(image_web_path, imagename)
                #   统计标签的数目
                classes_count = { key:0 for key in voc_classes }  # 初始化
                for bndbox in labelboxes:
                    try:
                        classes_count[bndbox['label']]+=1
                    except:
                        classes_count[bndbox['label']]=1
                
                #   增加标签按value值排序 22/04/13 by lgm 
                sort_count_list = sorted(classes_count.items(),key = lambda x:x[1],reverse=True)
                sorted_classes_count_dict={}
                for sorted_class in sort_count_list:
                    sorted_classes_count_dict[sorted_class[0]]=sorted_class[1]
                tra_images = {'imagename': image_web_file, 'imagesize': var['image_size'],
                              'labelboxes': labelboxes, 'ratio': var['ratio'],'classes_count':sorted_classes_count_dict}
                
                
                
                tagging_imgs.append(tra_images)
            show_images = {
                "total_pics": total_pics,
                "total_pages": total_pages,
                "total_tagging_pics": tagging_pics,
                "total_untagging_pics": total_pics-tagging_pics,
                "tagging_imgs": tagging_imgs
            }
            # 返回状态信息
            response['code'] = 200
            response['message'] = 'Success! The images of dataset had been shown!'
            response['dataType'] = dataType
            response['images'] = show_images
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        elif dataType == 'text':  # 表格类
            relative_path = MoFarmDataset.objects.filter(
                name=dataset).first().dataset_path
            target_path = os.path.join(
                settings.WEB_DATASET_SERVER_ROOT, relative_path)
            print(target_path)
            try:
                file = os.listdir(target_path)[0]
            except:
                response['code'] = 200
                response['message'] = 'Fail,file is not found!'
                response['dataType'] = dataType
                response['table_header'] = []
                response['table_data'] = []
                return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

            #   扩展名
            ext = os.path.splitext(file)[-1]
            if ext == '.txt':
                pass
            elif ext == '.csv':
                df = pd.read_csv(os.path.join(target_path, file))
                fields_table_list = list(df.columns.values)
                fields_table_header = []
                #   生成表头
                for i in range(len(fields_table_list)):
                    table_config_dict = {
                        'label': fields_table_list[i],
                        'dataName': fields_table_list[i],
                    }
                    fields_table_header.append(table_config_dict)

                total_rows = df.shape[0]
                total_pages = math.ceil(total_rows / page_size)
                # 当前游标位置
                cursor = (page_number - 1) * page_size
                if page_number == total_rows:

                    if total_rows == 1:    # 当只有一张时不切片
                        results = [df[cursor]]
                    else:
                        results = df[cursor:total_rows - 1]
                else:
                    results = df[cursor:cursor + page_size]
                if page_number > total_pages:
                    page_number = total_pages

                # 返回数据
                response['code'] = 200
                response['message'] = 'Success!'
                response['dataType'] = dataType
                response['table_header'] = fields_table_header

                rows_data = []
                for index, row in results.iterrows():
                    data_dict = {}
                    for field in fields_table_list:
                        data_dict[field] = row[field]
                    rows_data.append(data_dict)

                show_data = {
                    "total_pics": total_rows,
                    "total_pages": total_pages,
                    "rows_data": rows_data
                }
                response['table_data'] = show_data
                return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        elif dataType== 'remote_sensing':
            relative_path = MoFarmDataset.objects.filter(
                name=dataset).first().dataset_path
            target_path = os.path.join(
                settings.WEB_DATASET_SERVER_ROOT, relative_path)
            print(target_path)
            try:
                files = os.listdir(target_path)
            except:
                response['code'] = 200
                response['message'] = 'Fail,the dataset do not have file!'
                response['dataType'] = dataType
                response['total_files'] = 0
                response['total_pages'] = 0
                response['fileList'] = []
                return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

            total_files = len(files)
            total_pages = math.ceil(total_files/page_size)
            file_list = []
            response['code'] = 200
            response['message'] = 'Success!'
            response['dataType'] = dataType
            response['total_files'] = total_files
            response['total_pages'] = total_pages
            for file in files:
                file_path = os.path.join(target_path,file)
                img_base64_code = img_zip2base64(file_path,240)
                print(len(img_base64_code))
                file_list.append(img_base64_code)

            response['tifList'] = file_list
        else:  # 视频、音频类

            relative_path = MoFarmDataset.objects.filter(
                name=dataset).first().dataset_path
            target_path = os.path.join(
                settings.WEB_DATASET_SERVER_ROOT, relative_path)
            print(target_path)
            try:
                files = os.listdir(target_path)
            except:
                response['code'] = 200
                response['message'] = 'Fail,the dataset do not have file!'
                response['dataType'] = dataType
                response['total_files'] = 0
                response['total_pages'] = 0
                response['fileList'] = []
                return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

            total_files = len(files)
            total_pages = math.ceil(total_files/page_size)
            file_list = []
            response['code'] = 200
            response['message'] = 'Success!'
            response['dataType'] = dataType
            response['total_files'] = total_files
            response['total_pages'] = total_pages
            for file in files:
                file_web_path = 'http://' + settings.WEB_HOST_NAME + \
                    settings.WEB_DATA_SERVER_PATH + '/' + dataType+'/' + dataset + '/' + file
                file_list.append(file_web_path)

            response['fileList'] = file_list

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

#   删除数据集


def delete_dataset(request):
    response = {}

    if request.method == 'POST':
        paramslist = request.body
        json_data = json.loads(paramslist, strict=False)
        dataset = json_data['dataSetName']

        manager = DatasetManager()
        src_dataset = manager.get_dataset(dataset)
        if not src_dataset:
            response['code'] = 404
            response['message'] = 'the dataset is not found!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        dataType = MoFarmDataset.objects.filter(name=dataset).first().type

        #   删库操作
        MoFarmDataset.objects.filter(name=dataset).delete()
        if dataType == 'image':
            MoFarmImagesDataset.objects.filter(datasetname=dataset).delete()

        #   删除对应数据集文件夹下的文件
        delete_dir = os.path.join(
            settings.WEB_DATASET_SERVER_ROOT, dataType, dataset)
        if os.path.exists(delete_dir):
            shutil.rmtree(delete_dir)
        response['code'] = 200
        response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

#   在线标注一个样本


def upload_label_online(request):
    response = {}
    if request.method == 'POST':
        paramslist = request.body
        json_data = json.loads(paramslist, strict=False)
        print(json_data)
        dataset = json_data['dataset']
        file_name = json_data['imgName'].split('/')[-1]

        md5, ext = os.path.splitext(file_name)
        ratio = json_data['ratio']
        TagList = json_data['TagList']

        imgWidth = json_data['imgWidth']
        imgHeight = json_data['imgHeight']


        img_exist_or_not = MoFarmImagesDataset.objects.filter(
            datasetname=dataset, image_md5=md5).first()
        if not img_exist_or_not:
            response['code'] = 404
            response['message'] = 'the image is not found!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        dataType = MoFarmDataset.objects.filter(name=dataset).first().type

        # 检测通过，开始保存标注信息
        annotation_dir = settings.WEB_DATASET_SERVER_ROOT + dataType+'/' +\
            dataset+settings.ANNOTATION_SERVER_PATH

        annotation_path = annotation_dir + md5 + '.xml'

        xml_file = open(annotation_path.replace(
            '\\', '/'), 'w', encoding='utf-8')
        xml_file.write('<?xml version="1.0" ?>\n')
        xml_file.write('<annotation>\n')
        xml_file.write('    <folder>'+annotation_dir+'</folder>\n')
        xml_file.write('    <filename>' + file_name + '</filename>\n')
        xml_file.write('    <path>' + file_name + '</path>\n')
        xml_file.write('    <size>\n')
        xml_file.write('        <width>' + str(imgWidth) + '</width>\n')
        xml_file.write('        <height>' + str(imgHeight) + '</height>\n')
        xml_file.write('        <depth>3</depth>\n')
        xml_file.write('    </size>\n')
        bndboxes = []
        for i in range(len(TagList)):
            dataItem = TagList[i]
            xmin = dataItem['leftUp'][0]
            ymin = dataItem['leftUp'][1]
            xmax = dataItem['rightDown'][0]
            ymax = dataItem['rightDown'][1]
            dict = {
                'label': dataItem['tagName'],
                'xmin': xmin,
                'ymin': ymin,
                'xmax': xmax,
                'ymax': ymax,
            }
            bndboxes.append(dict)
            xml_file.write('    <object>\n')
            xml_file.write('        <name>' +
                           dataItem['tagName'] + '</name>\n')
            xml_file.write('        <pose>Unspecified</pose>\n')
            xml_file.write('        <truncated>0</truncated>\n')
            xml_file.write('        <difficult>0</difficult>\n')
            xml_file.write('        <bndbox>\n')
            xml_file.write('            <xmin>' + str(xmin) + '</xmin>\n')
            xml_file.write('            <ymin>' + str(ymin) + '</ymin>\n')
            xml_file.write('            <xmax>' + str(xmax) + '</xmax>\n')
            xml_file.write('            <ymax>' + str(ymax) + '</ymax>\n')
            xml_file.write('        </bndbox>\n')
            xml_file.write('    </object>\n')
        xml_file.write('</annotation>')
        xml_file.close()

        MoFarmImagesDataset.objects.filter(
            datasetname=dataset, image_md5=md5).update(tag_status='1', label_msg=bndboxes)
        response['code'] = 200
        response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

#   删除一个标注样本


def delete_label_record(request):
    response = {}
    if request.method == 'POST':
        paramslist = request.body
        json_data = json.loads(paramslist, strict=False)

        dataset = json_data['dataset']
        file_name = json_data['imgName'].split('/')[-1]
        md5, ext = os.path.splitext(file_name)
        # TagList = json_data['TagList']

        img_exist_or_not = MoFarmImagesDataset.objects.filter(
            datasetname=dataset, image_md5=md5).first()
        if not img_exist_or_not:
            response['code'] = 404
            response['message'] = 'the image is not found!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        # 删库操作
        MoFarmImagesDataset.objects.filter(datasetname=dataset, image_md5=md5).update(
            label_msg='', tag_status='0'
        )
        #  xml文件删除
        xml_path = settings.WEB_DATASET_SERVER_ROOT + "image/" +\
            dataset+settings.ANNOTATION_SERVER_PATH+md5+'.xml'
        if os.path.exists(xml_path):
            os.remove(xml_path)
            print("delete .xml done!")

    response['code'] = 200
    response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

#   关键字搜索数据集


def search_dataset_by_keyword(request):
    response = {}
    keyword = request.GET.get('keyword', None)
    dataType = request.GET.get('dataType', None)
    try:
        page_number = int(request.GET.get('pageNum'))
    except Exception as e:
        page_number = 1
    try:
        page_size = int(request.GET.get('pageSize'))
    except Exception as e:
        page_size = 12
    datasets_all = MoFarmDataset.objects.filter(type=dataType,
        name__icontains=keyword).order_by('-updated_time')
    total_datasets_count = MoFarmDataset.objects.filter(type=dataType,
        name__icontains=keyword).count()

    if not datasets_all:
        response['code'] = 401
        response['message'] = 'Fail!do not have contain results'
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

    total_pages = math.ceil(total_datasets_count / page_size)
    if page_number > total_pages:
        page_number = total_pages
    cursor = (page_number - 1) * page_size

    if page_number == total_datasets_count:

        if total_datasets_count == 1:    # 当只有一张时不切片
            results = [datasets_all[cursor]]
        else:
            results = datasets_all[cursor:total_datasets_count - 1]
    else:
        results = datasets_all[cursor:cursor + page_size]

    datasets_query = []
    for var in results:
        datasets_query.append(
            {'id': var.id, 'dataSetName': var.name, 'desc': var.desc}
        )
    if page_number >= total_pages:
        isNext = False
    else:
        isNext = True

    response['code'] = 200
    response['message'] = 'Success!'
    response['totalPages'] = total_pages
    response['currentPage'] = page_number
    response['isNext'] = isNext
    response['mapMsg'] = datasets_query
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

# Create your views here.


def test_dataset(request):
    response = {}
    manager = DatasetManager()
    name = 'first'
    desc = '第一个数据集',
    dataset_path = 'first_dataset.csv'
    type = 'table'
    print('hello!!!')
    manager.add_dataset(name, desc, dataset_path, type)
    manager.get_datasets()
    # manager.query_dataset(1,0,10)

    response['code'] = 200
    response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def clear_dataset(request):
    response = {}
    manager = DatasetManager()
    manager.remove_all()
    response['code'] = 200
    response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def get_datasets(request):
    response = {}
    results = MoFarmDataset.objects.all()
    query_result = []
    for var in results:
        dict = {
            'id': var.id,
            'dataType': var.type,
            'dataSetName': var.name,
            'desc': var.desc
        }
        query_result.append(dict)
    if query_result == []:
        response['code'] = 401
        response['message'] = 'Fail!'
        response['mapMsg'] = []
    else:
        # 返回状态信息
        response['code'] = 200
        response['message'] = 'Success!'
        response['mapMsg'] = query_result

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

#   v1


def get_dataset_by_page(request):
    response = {}
    id = int(request.GET.get("id"))  # 数据集id
    page = int(request.GET.get("page"))  # 查询的数据页
    page_size = int(request.GET.get("page_size"))  # 每一页的数据的条数

    manager = DatasetManager()
    query_result = manager.query_dataset(id, page, page_size)

    if query_result == None:
        response['code'] = 401
        response['message'] = 'Fail!'
        response['mapMsg'] = []
    else:
        # 返回状态信息
        response['code'] = 200
        response['message'] = 'Success!'
        response['mapMsg'] = query_result

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def download_dataset(request):
    # response = {}

    dataset_name = request.GET.get("dataSetName")
    manager = DatasetManager()

    src_dataset = manager.get_dataset(dataset_name)

    if not src_dataset:
        response['code'] = 401
        response['message'] = 'the dataset is not found!'
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

    relative_path = src_dataset.dataset_path
    data_type = src_dataset.type
    data_path = settings.WEB_DATASET_SERVER_ROOT+relative_path
    print(data_path)
    if data_type == 'text':  # csv/txt
        filename = os.listdir(data_path)[0]

        image_path = os.path.join(data_path, filename)

        def file_iterator(image_path, chunk_size=512):
            with open(image_path, mode='rb') as f:
                while True:
                    count = f.read(chunk_size)
                    if count:
                        yield count
                    else:
                        break
        try:
            response = StreamingHttpResponse(file_iterator(image_path))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = \
                'attachment;filename="%s"' % (
                    urlquote(filename.encode('utf-8').decode('utf-8')))
        except:
            response['code'] = 404
            response['message'] = 'Fialed! Sorry but Not Found the File!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
        return response

    else:  # zip压缩打包下载
        utilities = ZipUtilities()
        print(data_path)
        utilities.add_folder_to_zip(data_path, dataset_name)
        response = StreamingHttpResponse(
            utilities.zip_file,
            content_type='application/zip'
        )
        response['Content-Disposition'] = \
            'attachment;filename="{0}.zip"'.format(
                dataset_name.encode('utf-8').decode('ISO-8859-1'))
        return response


#   v2
def get_datasets_by_page_v2(request):
    response = {}
    dataset_type = request.GET.get("dataType") 
    try:
        page_number = int(request.GET.get('pageNum'))
    except Exception as e:
        page_number = 1
    try:
        page_size = int(request.GET.get('pageSize'))
    except Exception as e:
        page_size = 12

    dataset_all = MoFarmDataset.objects.filter(
        type=dataset_type).order_by('-updated_time')
    total_dataset_count = MoFarmDataset.objects.filter(
        type=dataset_type).count()
    if total_dataset_count == 0:
        response['code'] = 401
        response['message'] = 'Fail,zero!'
        response['dataset_msg'] = []
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

    total_pages = math.ceil(total_dataset_count / page_size)
    if page_number > total_pages:
        page_number = total_pages
    cursor = (page_number - 1) * page_size

    if page_number == total_dataset_count:

        if total_dataset_count == 1:    # 当只有一张时不切片
            results = [dataset_all[cursor]]
        else:
            results = dataset_all[cursor:total_dataset_count - 1]
    else:
        results = dataset_all[cursor:cursor + page_size]

    datasets_query = []
    for var in results:
        datasets_query.append(
            {'id': var.id, 'dataSetName': var.name, 'desc': var.desc}
        )
    if page_number >= total_pages:
        isNext = False
    else:
        isNext = True

    response['code'] = 200
    response['message'] = 'Success!'
    response['totalPages'] = total_pages
    response['currentPage'] = page_number
    response['isNext'] = isNext
    response['mapMsg'] = datasets_query

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

#   上传数据集的标签分类


def upload_voc_classes(request):
    response = {}
    if request.method == "POST":

        manager = DatasetManager()
        paramslist = request.body
        json_data = json.loads(paramslist, strict=False)
        dataset_name = json_data['dataSetName']
        voc_classes = json_data['voc_classes']
        print(type(voc_classes))
        #   检测是否有存在的数据集
        src_dataset = manager.get_dataset(dataset_name)
        if not src_dataset:
            response['code'] = 402
            response['message'] = 'the dataset is not exist!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        dataType = src_dataset.type
        dataset_path = os.path.join(
            settings.WEB_DATA_SERVER_ROOT, dataType, dataset_name, "model_data")

        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)
        voc_classes_path = os.path.join(dataset_path, 'voc_classes.txt')

        with open(voc_classes_path, "w") as f:
            for var in voc_classes:
                print(var['value'])
                f.write(var['value']+'\n')
            f.close()
        response['code'] = 200
        response['message'] = 'Success!'
    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")


def get_voc_classes(request):
    response = {}
    if request.method == "GET":

        manager = DatasetManager()
        dataset_name = request.GET.get('dataSetName', None)
        #   检测是否有存在的数据集
        src_dataset = manager.get_dataset(dataset_name)
        if not src_dataset:
            response['code'] = 402
            response['message'] = 'the dataset is not exist!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        dataType = src_dataset.type
        dataset_path = os.path.join(
            settings.WEB_DATA_SERVER_ROOT, dataType, dataset_name, "model_data")

        voc_classes_path = os.path.join(dataset_path, 'voc_classes.txt')
        voc_classes = []
        if os.path.exists(voc_classes_path):
            with open(voc_classes_path, 'r') as f:

                for line in f.readlines():
                    line = line.strip('\n')
                # if data !="\n":
                    voc_classes.append({
                        'value': line
                    })

            f.close()

        # print(voc_classes)
        # 返回状态信息
        response['code'] = 200
        response['message'] = 'Success!'
        response['voc_classes'] = voc_classes

        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

#   标注页面分页查看图片


def get_image_by_page(request):
    dataset_name = '梅州五华现场图片'
    response = {}
    if request.method == "GET":

        manager = DatasetManager()
        dataset_name = request.GET.get('dataSetName', None)
        #   检测是否有存在的数据集
        src_dataset = manager.get_dataset(dataset_name)
        if not src_dataset:
            response['code'] = 402
            response['message'] = 'the dataset is not exist!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
        dataType = src_dataset.type
        try:
            page_number = int(request.GET.get('pageNum'))
        except Exception as e:
            page_number = 1
        try:
            page_size = int(request.GET.get('pageSize'))
        except Exception as e:
            page_size = 12
        try:
            scale_height = int(request.GET.get('scaleHeight'))
        except Exception as e:
            scale_height = 240
        tag_status = request.GET.get('tagStatus')  # 标注状态  0  未标注  1 已标注

        images_query = MoFarmImagesDataset.objects.filter(datasetname=dataset_name, tag_status=tag_status)\
            .values('image_md5', 'label_msg', 'image_type', 'image_size', 'ratio')\


        total_dataset_count = MoFarmImagesDataset.objects.filter(
            datasetname=dataset_name, tag_status=tag_status).count()
        if total_dataset_count == 0:
            message = ["notagging_images", 'tagging_images']
            response['code'] = 402
            response['message'] = 'Fail!{:}的数目为空'.format(
                message[int(tag_status)])
            response['image_msg'] = []
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        total_pages = math.ceil(total_dataset_count / page_size)
        if page_number > total_pages:
            page_number = total_pages
        cursor = (page_number - 1) * page_size

        if page_number == total_dataset_count:

            if total_dataset_count == 1:    # 当只有一张时不切片
                results = [images_query[cursor]]
            else:
                results = images_query[cursor:total_dataset_count - 1]
        else:
            results = images_query[cursor:cursor + page_size]

        images_list = []
        for var in results:
            md5s = var['image_md5']
            imagename = md5s+var['image_type']
            # 内网访问
            image_web_path = 'http://' + settings.WEB_HOST_NAME + \
                settings.WEB_DATA_SERVER_PATH + '/' + dataType + \
                '/' + dataset_name + settings.UPLOAD_IMAGE_SERVER_PATH
            image_web_url = os.path.join(image_web_path, imagename)

            #   图片文件路径
            image_file_path = os.path.join(
                settings.WEB_DATA_SERVER_ROOT, dataType, dataset_name, "JPEGImages", imagename)
            # print(image_file_path)
            #   图片压缩转base64编码
            img_base64_code = img_zip2base64(image_file_path, scale_height)

            tra_images = {'imagename': image_web_url, 'imagesize': var['image_size'],
                          'ratio': var['ratio']}
            if tag_status == "1":  # 若已标注则额外展示标注信息
                try:
                    labelboxes = literal_eval(var['label_msg'])
                except Exception as e:
                    labelboxes = []
                tra_images['labelBoxes'] = labelboxes
            tra_images['image'] = img_base64_code
            images_list.append(tra_images)
        show_images = {
            "total_pics": total_dataset_count,
            "total_pages": total_pages,
            "imgs": images_list
        }
        response['code'] = 200
        response['message'] = 'Success!'
        response['images'] = show_images
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

#motified by lgm 
#22/4/1
#标签信息统计
def parse_obj(xml_path, filename):
    tree=ET.parse(os.path.join(xml_path,filename))
    objects=[]
    for obj in tree.findall('object'):
        obj_struct={}
        obj_struct['name']=obj.find('name').text
        objects.append(obj_struct)
    return objects

# 统计xml目录的所有目标的标签
def get_obj_names(xml_path):
    if not os.path.exists(xml_path):
        os.mkdir(xml_path)
    filenamess=os.listdir(xml_path)
    filenames=[]
    for name in filenamess:
        name=name.replace('.xml','')
        filenames.append(name)
    recs={}
    obs_shape={}
    classnames=[]
    num_objs={}
    obj_avg={}
    for i,name in enumerate(filenames):
        recs[name]=parse_obj(xml_path, name+ '.xml' )
    for name in filenames:
        for object in recs[name]:
            if object['name'] not in num_objs.keys():
                num_objs[object['name']]=1
            else:
                num_objs[object['name']]+=1
            if object['name'] not in classnames:
                classnames.append(object['name'])
    
    x,y = [],[]
    for name in classnames:
        # print('{}:{}个'.format(name,num_objs[name]))
        y.append(name)
        x.append(num_objs[name])
    # print(x,y)
    return x,y,num_objs

#统计标签
def update_label(request):
    response={}
    if request.method=='POST':
        paramslist = request.body
        json_data = json.loads(paramslist, strict=False)
        
        manager = DatasetManager()
        dataset_name = json_data["dataSetName"]# 数据集名称,train1,train, test1,...
        #   检测是否有存在的数据集
        src_dataset = manager.get_dataset(dataset_name)
        if not src_dataset:
            response['code'] = 402
            response['message'] = 'the dataset is not exist!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
        
        if src_dataset.type != 'image':
            response['code'] = 403
            response['message'] = 'the dataset must be image type!'
            return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")
        
        classes = []
        dataset_path = settings.WEB_DATASET_SERVER_ROOT+src_dataset.type+"/"+dataset_name
        annotation_path = os.path.join(dataset_path,'Annotations')
        print(annotation_path)  
        _,classes,num_objs = get_obj_names(annotation_path)
        print(classes)
        txt_dir = dataset_path +"/model_data"
        if not os.path.exists(txt_dir):
            os.mkdir(txt_dir)
        txt_path = dataset_path +"/model_data/voc_classes.txt"
        file = open(txt_path,'w+')
        for item in classes:
            file.write(item+"\n")
        file.close()
        
        response['code'] = 200
        response['message'] = 'Success!'
        response['labels'] = classes

    return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

#   本地导入数据


def import_dataset_offline(datasetName, target_path, desc, type):

    manager = DatasetManager()
    src_dataset = manager.get_dataset(datasetName)
    if src_dataset:
        print('the dataset is exist!')
        return

    dataset_path = settings.WEB_DATASET_SERVER_ROOT+type+"/"+datasetName

    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    command = 'unzip -o {} -d {}'.format(target_path, dataset_path+'/')
    os.system(command)
    # 数据集写库
    import_dataset = MoFarmDataset()
    import_dataset.name = datasetName
    import_dataset.dataset_path = dataset_path
    import_dataset.type = type
    import_dataset.desc = desc
    import_dataset.save()

    print('success import!')
    #   同步图片存放表
    if type == 'image':
        update_img_database(datasetName)


# 计算文件的md5
def pCalculateMd5(file):
    md5Obj = hashlib.md5()
    for chunk in file.chunks():
        md5Obj.update(chunk)
    return md5Obj.hexdigest()


# 检测文件类型
def pGetFileExtension(file):
    rawData = bytearray()
    for c in file.chunks():
        rawData += c
    try:
        ext = filetype.guess_extension(rawData)
        return ext
    except Exception as e:
        # todo log
        return None


# 文件的复制
def mycopy(file1, file2):  # 定义一个复制文件的函数

    f1 = open(file1, "rb")  # 读文件
    f2 = open(file2, "wb")  # 写文件

    content = f1.readline()
    while len(content) > 0:
        f2.write(content)
        content = f1.readline()

    f1.close()  # 关闭file1
    f2.close()


# 自定义目录复制函数
def copydir(origin_path, target_path):  # 定义复制文件夹函数coppydir
    # 获取被复制目录中的所有文件信息
    src_list = os.listdir(origin_path)  # 以列表模式赋给dlist
    # 创建新目录
    if not os.path.exists(target_path):
        os.mkdir(target_path)  # 创建新文件夹dir2
    # 遍历所有文件并执行文件复制
    for f in src_list:
        # 为遍历的文件添加目录路径
        # 将f遍历出的文件名给file1（origin_path+f即路径+文件名）
        src_file = os.path.join(origin_path, f)
        target_file = os.path.join(target_path, f)  # 同样也给file2
        # 判断是否是文件
        if os.path.isfile(src_file):  # 判断是否为文件的方式为os库中的函数 os.path.isfile(文件名)
            mycopy(src_file, target_file)  # 调用复制文件
        if os.path.isdir(src_file):
            copydir(src_file, target_file)  # 递归


# 根据VOC目录同步到图片数据库
def update_img_database(datasetName):

    dataset_path = settings.WEB_DATA_SERVER_ROOT + "image/" + datasetName
    img_path = dataset_path + settings.UPLOAD_IMAGE_SERVER_PATH
    annotation_path = dataset_path + settings.ANNOTATION_SERVER_PATH

    for file in os.listdir(img_path):
        md5, ext = os.path.splitext(file)
        annotation_file = os.path.join(annotation_path, md5+'.xml')

        import_img_dataset = MoFarmImagesDataset()
        import_img_dataset.datasetname = datasetName
        import_img_dataset.image_name = file
        import_img_dataset.image_md5 = md5
        img_pillow = Image.open(os.path.join(img_path,file))
        img_width = img_pillow.width  # 图片宽度
        img_height = img_pillow.height  # 图片高度
        img_size = str(img_width)+','+str(img_height)
        import_img_dataset.image_size = img_size
        if os.path.exists(annotation_file):
            import_img_dataset.tag_status = '1'
            tree = ET.parse(annotation_file)
            root = tree.getroot()
            # try:
            #     width = root.find("size").find("width").text
            #     height = root.find("size").find("height").text
            #     img_size = width+','+height
                
            # except Exception as e:
            #     img_pillow = Image.open(os.path.join(img_path,file))
            #     img_width = img_pillow.width  # 图片宽度
            #     img_height = img_pillow.height  # 图片高度
            #     img_size = str(img_width)+','+str(img_height)
                
            # import_img_dataset.image_size = img_size
            bndboxes = []

            # if root.tag == 'annotation':
            #     for item in root.findall('object'):
            #         dict = {}
            #         dict['label'] = item.find('name').text.replace(' ', '')
            #         dict['xmin'] = int(item.find('bndbox').find('xmin').text)
            #         dict['ymin'] = int(item.find('bndbox').find('ymin').text)
            #         dict['xmax'] = int(item.find('bndbox').find('xmax').text)
            #         dict['ymax'] = int(item.find('bndbox').find('ymax').text)
            #         bndboxes.append(dict)
            # #  doc格式
            # elif root.tag == 'doc':
            #     object = root.find("outputs").find('object')

            #     for item in object.findall('item'):
            #         dict = {}
            #         item.find('name').text = item.find(
            #             'name').text.replace(' ', '')
            #         dict['label'] = item.find('name').text.replace(' ', '')
            #         dict['xmin'] = int(item.find('bndbox').find('xmin').text)
            #         dict['ymin'] = int(item.find('bndbox').find('ymin').text)
            #         dict['xmax'] = int(item.find('bndbox').find('xmax').text)
            #         dict['ymax'] = int(item.find('bndbox').find('ymax').text)
            #         bndboxes.append(dict)
            # annotation格式
            try:
                if root.tag == 'annotation':
                    for item in root.findall('object'):
                        dict = {}
                        dict['label'] = item.find('name').text.replace(' ', '')
                        dict['xmin'] = int(item.find('bndbox').find('xmin').text)
                        dict['ymin'] = int(item.find('bndbox').find('ymin').text)
                        dict['xmax'] = int(item.find('bndbox').find('xmax').text)
                        dict['ymax'] = int(item.find('bndbox').find('ymax').text)
                        bndboxes.append(dict)
                #  doc格式
                elif root.tag == 'doc':
                    object = root.find("outputs").find('object')

                    for item in object.findall('item'):
                        dict = {}
                        item.find('name').text = item.find(
                            'name').text.replace(' ', '')
                        dict['label'] = item.find('name').text.replace(' ', '')
                        dict['xmin'] = int(item.find('bndbox').find('xmin').text)
                        dict['ymin'] = int(item.find('bndbox').find('ymin').text)
                        dict['xmax'] = int(item.find('bndbox').find('xmax').text)
                        dict['ymax'] = int(item.find('bndbox').find('ymax').text)
                        bndboxes.append(dict)
            except:                
                print(annotation_file)
                import_img_dataset.tag_status = '0'
                print('xml数据有问题')

            # 保存标注信息
            if len(bndboxes)>0:
                import_img_dataset.label_msg = bndboxes
        import_img_dataset.image_type = ext
        import_img_dataset.ratio = 1.0
        import_img_dataset.save()
