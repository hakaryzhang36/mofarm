from module.feature_extractor_mnist import feature_extractor_mnist
from module.datasource_mnist import datasource_mnist
from module.classifier_mnist import classifier_mnist
import os
import json
if __name__ == '__main__':
	os.environ["CUDA_VISIBLE_DEVICES"] = "2"
	config = {'layer': '3', 'learning_rate': '0.01', 'model': 'feature_extractor_1.pth'}
	feature_extractor_mnist_2 = feature_extractor_mnist("new-mnist","feature_extractor_mnist",config)
	config = {'layer': '3', 'learning_rate': '0.02'}
	datasource_mnist_3 = datasource_mnist("new-mnist","datasource_mnist",config)
	config = {'layer': '3', 'learning_rate': '0.01', 'epoch': '2', 'model': 'classifier_1.pth'}
	classifier_mnist_5 = classifier_mnist("new-mnist","classifier_mnist",config)
	feature_extractor_mnist_2.link(datasource_mnist_3)
	classifier_mnist_5.link(feature_extractor_mnist_2)
	classifier_mnist_5.train()
