'''
Author: your name
Date: 2022-04-28 16:13:32
LastEditTime: 2022-04-28 16:45:33
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /MoFarm_jmlv/test/字符识别.py
'''
import sys
sys.path.append('../modules')
from classifier_mnist import classifier_mnist
from datasource_mnist import datasource_mnist
from feature_extractor_mnist import feature_extractor_mnist
import os
import json
if __name__ == '__main__':    
	os.environ["CUDA_VISIBLE_DEVICES"] = "1"

	config = {'layer': '3', 'learning_rate': '0.01', 'epoch': '1', 'model': 'classifier_1.pth'}
	classifier_mnist_2 = classifier_mnist("字符识别","classifier_mnist",config)
	
	config = {'layer': '3', 'learning_rate': '0.02'}
	datasource_mnist_3 = datasource_mnist("字符识别","datasource_mnist",config)
	
	config = {'layer': '3', 'learning_rate': '0.01', 'model': 'feature_extractor_1.pth'}	
	feature_extractor_mnist_4 = feature_extractor_mnist("字符识别","feature_extrator_mnist",config)
	
	feature_extractor_mnist_4.link(datasource_mnist_3)
	classifier_mnist_2.link(feature_extractor_mnist_4)
	classifier_mnist_2.train()
	#classifier_mnist_2.test()
