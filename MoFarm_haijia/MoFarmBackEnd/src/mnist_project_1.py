from module.DataSource_MNIST import DataSource_MNIST
from module.FeatureExtractor_MNIST import FeatureExtractor_MNIST
from module.Classifier_MNIST import Classifier_MNIST
import os
import json
if __name__ == '__main__':
	os.environ["CUDA_VISIBLE_DEVICES"] = "3"
	config = {}
	data_source_1 = DataSource_MNIST("mnist_project_1",config)
	config = {'layer': 3, 'learning_rate': 0.01, 'model': 'feature_extractor_1.pth', 'running': ''}
	feature_extractor_1 = FeatureExtractor_MNIST("mnist_project_1",config)
	config = {'layer': 3, 'learning_rate': 0.01, 'epoch': 5, 'model': 'classifier_1.pth', 'runing': 'tratin'}
	classifier_1 = Classifier_MNIST("mnist_project_1",config)
	feature_extractor_1.set_data_source(data_source_1)
	classifier_1.set_feature_extractor(feature_extractor_1)
	classifier_1.train()
