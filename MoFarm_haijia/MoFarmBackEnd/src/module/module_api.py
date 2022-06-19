import json
import requests
import torch

class DataSource(object):
    def set_url(self,url):
        print ('Not implemented ： DataSource.set_url')    
    def get_train_data_labeled(self):
        print('Not implemented ： DataSource.get_train_data_labeled')
    def get_validation_data(self):
        print('Not implemented ： DataSource.get_validation_data')
    def get_test_data(self):
        print('Not implemented ： DataSource.get_test_data')
    def get_source_data_labeled(self):
        print('Not implemented ： DataSource.get_source_data_labeled')
    def get_target_data_unlabeled(self):
        print('Not implemented ： DataSource.get_target_data_unlabeled')       

class ModelModule(object):
    def get_model(self):
        print('Not implemented ：FeatureExtractor.get_model')    
    def save_model(self):
        print('Not implemented ：FeatureExtractor.save_model')   
    def load_model(self):
        print('Not implemented ：FeatureExtractor.load_model')
    def freeze_model(self):
        print('Not implemented ：FeatureExtractor.freeze_model')
    def unfreeze_model(self):
        print('Not implemented ：FeatureExtractor.unfreeze_model')

class FeatureExtractor(ModelModule):     
    def set_data_source(self,data_source):
        print("Not implemented ：FeatureExtractor.set_data")
    def get_data_source (self):
        print("Not implemented ：FeatureExtractor.set_data")
    def get_feature(self):
        print('Not implemented ：FeatureExtractor.get_feature')

class Classifier(ModelModule):
    def set_feature_extractor(self, feature_extractor):
        print ('Not implemented ：Classifier.set_feature_model')    
    def get_model(self): 
        print ('Not implemented ：Classifier.get_model')
    def train(self):
        print ('Not implemented ：Classifier.train')
    def test(self):
        print ('Not implemented ：Classifier.test')
    def get_test_result(self):
        print ('Not implemented ：Classifier.get_test_result')
    def test_on_train(self):
        print ('Not implemented ：Classifier.test_on_train')    

    def save_model (self, model, model_name, module_name):
        model_path = ('MoFarmBackEnd/config/models/%s' %model_name)
        torch.save(model.state_dict(), model_path)
        url = "http://127.0.0.1:9000/MoFarmBackEnd/add_model/"
        
        values = {'model_name':model_name,'module_name':module_name}        
        res = requests.get(url,values) 

    def report_status(self, project_name, first_report_time, is_first_report, progress, msg,run_status):
        url = "http://127.0.0.1:9000/MoFarmBackEnd/update_project_status/"

        history_file_path = 'MoFarmBackEnd/log/' + project_name + '_' +first_report_time + '_log.csv'
        of = open(history_file_path, 'a')
        buf = ''  
        if is_first_report == True:            
            for attribute, value in msg.items():
                buf += (str(attribute) + ',')       
            buf = buf[:-1]
            of.write(buf)
            of.write('\n')
        
        buf = ''
        for attribute, value in msg.items():    
            buf += (str(value) + ',')                       
            
        buf = buf[:-1]
        of.write(buf)
        of.write('\n')
        of.close()                
        if progress<100:
            status = {'total_progress': progress, 'run_status':run_status,'run_real_time_msg': msg, 'run_history_path': history_file_path}
        else:
            status = {'total_progress': progress, 'run_status':'stop','run_real_time_msg': msg, 'run_history_path': history_file_path}
        values = {'name':project_name,'status':json.dumps(status)}
        
        res = requests.get(url,values)

        #change = res.json()
        #new_req = json.dumps(change, ensure_ascii=False)
        # 打印接口返回的数据,且以中文编码
        #print(new_req)
    def report_test_status(self, project_name,progress,run_status):
        url = "http://127.0.0.1:9000/MoFarmBackEnd/update_project_status/"
        status = {'total_progress': progress, 'run_status':run_status}

        values = {'name':project_name,'status':json.dumps(status)}
        
        res = requests.get(url,values)

class MUDA(object):
    def set_num_of_modality(self, n):
        print ('Not implemented ：MUDA.set_num_of_modality')
    def set_modality(self, feature_v):
        print ('Not implemented ：MUDA.set_modality')
    def set_source_data(self, source_data):
        print ('Not implemented ：MUDA.ce_data')
    def set_target_data(self, target_data):
        print ('Not implemented ：MUDA.set_target_data')
 
 
 