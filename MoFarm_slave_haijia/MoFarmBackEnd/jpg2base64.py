'''
Author: lgm
Date: 2022-02-24 17:19:00
LastEditTime: 2022-03-28 15:25:54
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /AIProject/ImageManagement/jpg2base64.py
'''
import base64
import cv2
import numpy as np
from PIL import Image
import imutils
base64_head = 'data:image/jpg;base64,'

def cv_imread(filePath):
    cv_img=cv2.imdecode(np.fromfile(filePath,dtype=np.uint8),-1)
    ## imdecode读取的是rgb，如果后续需要opencv处理的话，需要转换成bgr，转换后图片颜色会变化
    ##cv_img=cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)
    return cv_img
    
def img_zip2base64(filepath,height):
    Img = Image.open(filepath)
    img = cv2.cvtColor(np.asarray(Img), cv2.COLOR_RGB2BGR)
    h,w,_ = img.shape
    img_resize = imutils.resize(img, height=height)
    image = cv2.imencode('.jpg',img_resize)[1]
    image_code = base64_head+str(base64.b64encode(image))[2:-1]
    return image_code
