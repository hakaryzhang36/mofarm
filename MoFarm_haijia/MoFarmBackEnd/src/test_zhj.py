from module.classifier_mnist import classifier_mnist
from module.datasource_mnist import datasource_mnist
from module.feature_extractor_mnist import feature_extractor_mnist
import os
import json
if __name__ == '__main__':
	os.environ["CUDA_VISIBLE_DEVICES"] = "2"
	config = {'layer': '3', 'learning_rate': '0.01', 'epoch': '2', 'model': 'classifier_1.pth'}
	classifier_mnist_2 = classifier_mnist("test_zhj","classifier_mnist",config)
	config = {'layer': '3', 'learning_rate': '0.02'}
	datasource_mnist_3 = datasource_mnist("test_zhj","datasource_mnist",config)
	config = {'layer': '3', 'learning_rate': '0.01', 'model': 'feature_extractor_1.pth'}
	feature_extractor_mnist_4 = feature_extractor_mnist("test_zhj","feature_extractor_mnist",config)
	feature_extractor_mnist_4.link(datasource_mnist_3)
	classifier_mnist_2.link(feature_extractor_mnist_4)
	classifier_mnist_2.train()
