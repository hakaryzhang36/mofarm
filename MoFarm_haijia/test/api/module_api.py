import json
import requests
import torch

model_dir_path ='../models/'# 'MoFarmBackEnd/config/models/'
log_dir_path = '../log/'#'MoFarmBackEnd/log/'
back_end_url = 'http://127.0.0.1:9000/'

class DataSource(object):
    def __init__(self, project_name, module_name,config):
        self.project_name = project_name
        self.model_name = module_name
        self.config = config
   
    #return a torch.utils.data.DataLoader object
    def get_train_data_loader(self):
        pass
    #return a torch.utils.data.DataLoader object
    def get_validation_data_loader(self):
        pass
    #return a torch.utils.data.DataLoader object
    def get_test_data_loader(self):
        pass

        
class ModelModule(object):
    def __init__(self, project_name, module_name,config):
        self.project_name = project_name
        self.module_name = module_name
        self.config = config

        self.model = None

    def link(self, module):
        pass

    def get_model(self):
        return self.model
    def set_model(self, model):
        self.model = model

    def save_model(self):
        global model_dir_path
        global back_end_url
        
        if self.config.__contains__("model"):
            model_name = self.config["model"]
            print ("saving model：" +model_name)
            torch.save(self.model.state_dict(),(model_dir_path + model_name))
        
            url = back_end_url +"MoFarmBackEnd/add_model/"
        
            values = {'model_name':model_name,'module_name':self.module_name}        
            res = requests.get(url,values) 
        else:
            print("no matching model !")   


    def load_model(self):
        if self.config.__contains__("model"):
            model_name = self.config["model"]
            print ("load model %s " %model_name)
            self.model.load_state_dict(torch.load(model_dir_path + model_name))
        else:
            print("no matching model !") 
       
    def freeze_model(self):
        for param in self.model.parameters():
            param.requires_grad = False

    def unfreeze_model(self):
        for param in self.model.parameters():
            param.requires_grad = True

    def report_status(self, project_name, first_report_time, is_first_report, progress, msg):
        url = back_end_url + "MoFarmBackEnd/update_project_status/"

        history_file_path = log_dir_path + project_name + '_' +first_report_time + '_log.csv'
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
            status = {'total_progress': progress, 'run_real_time_msg': msg, 'run_history_path': history_file_path}
        else:
            status = {'total_progress': progress,'run_real_time_msg': msg, 'run_history_path': history_file_path}
        values = {'name':project_name,'status':json.dumps(status)}
        
        res = requests.get(url,values)

        #change = res.json()
        #new_req = json.dumps(change, ensure_ascii=False)
        # 打印接口返回的数据,且以中文编码
        #print(new_req)
        
class FeatureExtractor(ModelModule):  
    def __init__(self, project_name, module_name,config):
        super(FeatureExtractor, self).__init__(project_name, module_name,config)
       
        self.data_source = None

    def link(self, module):
        if (module.__class__.__bases__[0].__name__=="DataSource"):
            print ('------->link from datasource to feature extractor')
            self.data_source = module 

    def get_data_source (self):
        return self.data_source
 

class Classifier(ModelModule):
    def __init__(self,project_name, module_name,config):
        super(Classifier, self).__init__(project_name, module_name,config)

        self.data_source = None
        self.feature_extractor = None

    def link(self, module):
        if (module.__class__.__bases__[0].__name__=="FeatureExtractor"):
            print ('------->link from feature extractor to classifier')
            feature_extractor = module
            self.feature_extractor = feature_extractor
            self.data_source = feature_extractor.get_data_source()
            return True
        return False 

    def get_feature_extractor(self):
        return self.feature_extractor
 
    def train(self):
        pass
    def test(self):
        pass


        

class MUDA(object):
    def __init__(self,project_name, module_name,config):
        self.project_name = project_name
        self.model_name = module_name
        self.config = config
        
        self.feature_extractors = []
        self.classifiers = []
        self.src_data_sources = []
        self.target_data_source = None 
        
    
    def link(self, module):
        if (module.__class__.__bases__[0].__name__=="Classifier"):
            print ('------->link from classifier to MUDA')
            classifier = module
            feature_extractor = classifier.get_feature_extractor()
            data_source = feature_extractor.get_data_source() 
            self.classifiers.append(classifier)
            self.feature_extractors.append(feature_extractor)
            self.src_data_sources.append(data_source)
        elif (module.__class__.__bases__[0].__name__=="DataSource"):
            print ('------->link from target datasource to MUDA module')            
            self.target_data_source = module
         
            

 