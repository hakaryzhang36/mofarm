import os
import torch   
import json
import threading

from .YOLOv4_MODEL.module_manager import ModuleManager

def run_cmd(cmd_line):
    os.system(cmd_line)

class ProjectFactory(object):
    def __init__(self, name):   
        self.project_name = name     
        self.module_dict = {}
        self.relation_list = []
        self.running_list = []

    def add_module(self, name, local_name, config):
        manager = ModuleManager()
        if config != None:
            self.module_dict[local_name] = {"name":name, "config":config}
            return True
        else:
            return False
  
    def add_connection(self, local_name1, local_name2):
        print ('adding connection ...')
        if self.module_dict.__contains__(local_name1) and self.module_dict.__contains__(local_name2):            
            self.relation_list += ((local_name1,local_name2),)
            print ('add ' + local_name1 + ' ' +local_name2)
            return True
        else:
            return False

    def add_running(self, local_name, function):
        if self.module_dict.__contains__(local_name):
            self.running_list += ((local_name, function),)
            return True
        else:
            return False


    '''
    {
    "modules": [
            {
            "name":"MNIST_DataSource",
            "local_name":"data_source_1"
            },
        
    ],
    "links":[
        ["data_source_1","feature_extrator_1","set_datasource"],
        ["feature_extrator_1","classifier_1","set_feature_extrator"]
    ],
    "runing":{"classifier_1":"train"}
    }
    '''
    def parse_json(self, config_json):
        #try:
        if True:
            config = json.loads(config_json)
            modules = config["modules"]
            links = config["links"]
            runnings = config["running"]

            for module in modules:
                self.add_module(module["name"], module["local_name"], module["config"])
            
            for link in links:
                self.add_connection(link[0], link[1])

            for local_name,function in runnings.items():
                self.add_running(local_name, function)

            return True

        #except:
        #    print ('解析项目配置失败: %s' %config_json)
        #    return False
    


    def build_project(self):
        of = open('MoFarmBackEnd/src/'+self.project_name + '.py', 'w')
        for local_name, attribute in self.module_dict.items():
            module_name = attribute["name"]
            of.write('from module.' + module_name + ' import ' + module_name + '\n')
        of.write('import os\n')
        of.write('import json\n')
        of.write('if __name__ == \'__main__\':\n')
        # add by lxj
        num_gpu = torch.cuda.device_count()
        if num_gpu > 0:
            gpu_ids = [n for n in range(num_gpu)]
            
            of.write('\tos.environ["CUDA_VISIBLE_DEVICES"] = "%d"\n' % gpu_ids[-1])
        
        variables = {}
        for module_local_name, attribute in self.module_dict.items():
            module_name = attribute["name"]
            module_config = attribute["config"]
            of.write (('\tconfig = %s' %module_config).replace('\n', ''))
            of.write('\n')
            of.write('\t%s = %s(\"%s\",\"%s\",config)\n' %(module_local_name, module_name, self.project_name, module_name))
        
        for i in range (len(self.relation_list)):
            local_name1 = self.relation_list[i][0]
            local_name2 = self.relation_list[i][1]
            of.write('\t%s.link(%s)\n' %(local_name2,local_name1))

        for i in range(len(self.running_list)):
            local_name = self.running_list[i][0]            
            function = self.running_list[i][1]
            of.write('\t%s.%s()\n' %(local_name, function))

        of.close()           

         
    def run_project(self):
        cmd_line = 'python MoFarmBackEnd/src/'+ self.project_name + '.py'
        t = threading.Thread(target=run_cmd, args=(cmd_line,))
        t.start()
        return
    
    def draw_project(self):
        for i in range (len(self.relation_list)):
            local_name1 = self.relation_list[i][0]
            local_name2 = self.relation_list[i][1]
            print ('| %s | ---->| %s |' %(local_name1,local_name2))

  
if __name__ == '__main__':
    manager = ModuleManager()
    manager.register_module('YOLO_DataSource', 'DataSource')
    manager.register_module('YOLO_FeatureExtractor', 'FeatureExtractor')
    manager.register_module('YOLO_Classifier', 'Classifier')

    session = manager.new_session('first_session')
    session.add_connection('YOLO_DataSource', 'YOLO_FeatureExtractor', 'set_data_source')
    session.add_connection('YOLO_FeatureExtractor','YOLO_Classifier', 'set_feature_extractor')

    session.add_invocation('YOLO_Classifier', 'load_model')
    #session.add_invocation('YOLO_Classifier', 'freeze_model')
    #session.add_invocation('YOLO_Classifier', 'train')
    session.add_invocation('YOLO_Classifier', 'test')
    session.build_session()
    session.draw_session()
    #session.run_session()
     
    