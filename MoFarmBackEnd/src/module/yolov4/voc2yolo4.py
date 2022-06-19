# -*- coding:UTF-8 -*-
import os
import random 
random.seed(0)


def voc_to_yolo4(path, action):
    '''loads the datasetpath'''
    xmlfilepath=r'%s/VOC2007/Annotations' % path
    saveBasePath=r'%s/VOC2007/ImageSets/Main/' % path
    if not os.path.exists(saveBasePath):
            os.makedirs(saveBasePath)

    temp_xml = os.listdir(xmlfilepath)
    total_xml = []
    for xml in temp_xml:
        if xml.endswith(".xml"):
            total_xml.append(xml)

    num=len(total_xml)  
    list=range(num)  
    image_ids = random.sample(list,int(num))

    if action == 'train':
        print("Train size is ", int(num))
        ftrain = open(os.path.join(saveBasePath,'train.txt'), 'w')  
        for i  in list:  
            name=total_xml[i][:-4]+'\n'  
            if i in image_ids:  
                ftrain.write(name)  
        ftrain.close()  
    else:
        print("Test size is ", int(num))
        ftest = open(os.path.join(saveBasePath,'test.txt'), 'w')  
        for i  in list:  
            name=total_xml[i][:-4]+'\n'  
            if i in image_ids:  
                ftest.write(name)  
        ftest.close()  
    
    return 
