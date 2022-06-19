from module.datasource_mnist import datasource_mnist
from module.feature_extractor_mnist import feature_extractor_mnist
from module.classifier_mnist import classifier_mnist
import os
import json
if __name__ == '__main__':
	os.environ["CUDA_VISIBLE_DEVICES"] = "2"
	config = {'layer': '3', 'learning_rate': '0.02'}
	datasource_mnist_2 = datasource_mnist("mnist字符识别","datasource_mnist",config)
	config = {'layer': '3', 'learning_rate': '0.01', 'model': 'feature_extractor_1.pth'}
	feature_extractor_mnist_3 = feature_extractor_mnist("mnist字符识别","feature_extractor_mnist",config)
	config = {'layer': '3', 'learning_rate': '0.01', 'epoch': '3', 'model': 'classifier_1.pth'}
	classifier_mnist_4 = classifier_mnist("mnist字符识别","classifier_mnist",config)
	feature_extractor_mnist_3.link(datasource_mnist_2)
	classifier_mnist_4.link(feature_extractor_mnist_3)
	classifier_mnist_4.test()
