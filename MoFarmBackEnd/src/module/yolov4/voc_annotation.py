# -*- coding:UTF-8 -*-
import xml.etree.ElementTree as ET

#sets=[('2007', 'train'), ('2007', 'val'), ('2007', 'test')]
#   这里设定的classes顺序要和model_data里的txt一样
#classes = ["person","garbagetruck","bulldozer","slagcar","digger","structures"]

def convert_annotation(data_path, classes, year, image_id, list_file):
    in_file = open('%s/VOC%s/Annotations/%s.xml'%(data_path, year, image_id), encoding='utf-8')
    tree=ET.parse(in_file)
    root = tree.getroot()

    for obj in root.iter('object'):
        difficult = 0 
        if obj.find('difficult')!=None:
            difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (int(float(xmlbox.find('xmin').text)), int(float(xmlbox.find('ymin').text)), int(float(xmlbox.find('xmax').text)), int(float(xmlbox.find('ymax').text)))
        list_file.write(" " + ",".join([str(a) for a in b]) + ',' + str(cls_id))

def voc_to_annotation(data_path, classes, action):
    if action == 'train':
        sets=[('2007', 'train')]
    else:
        sets=[('2007', 'test')]
    for year, image_set in sets:
        image_ids_txt = '%s/VOC%s/ImageSets/Main/%s.txt'%(data_path, year, image_set)
        image_ids = open(image_ids_txt, encoding='utf-8').read().strip().split()
        data_txt = '%s/VOC%s/ImageSets/Main/%s_%s.txt'%(data_path, year, year, image_set)
        list_file = open(data_txt, 'w', encoding='utf-8')
        for image_id in image_ids:
            list_file.write('%s/VOC%s/JPEGImages/%s.jpg'%(data_path, year, image_id))
            convert_annotation(data_path, classes, year, image_id, list_file)
            list_file.write('\n')
        list_file.close()
    print('Voc to annotation done!')
    return image_ids_txt, data_txt