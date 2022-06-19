import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda, Compose
from .module_api import *
from .datasource_mnist import datasource_mnist
from .feature_extractor_mnist import feature_extractor_mnist
import datetime

class Model_Classifier(nn.Module):
    def __init__(self, feature_extractor):
        super(Model_Classifier, self).__init__()        
        self.feature_extractor = feature_extractor.get_model()
        self.classifier_stack = nn.Sequential(
            nn.Linear(512, 10)
        )        

    def forward(self, x):
        x = self.feature_extractor(x)
        logits = self.classifier_stack(x)
        return logits


class classifier_mnist(Classifier):
    def __init__(self, project_name, module_name,config):
        # Get cpu or gpu device for training.
        self.device = "cuda" if torch.cuda.is_available() else "cpu"                
        self.data_source = None
        self.model = None #Model_Classifier().to(device)
        self.project_name = project_name
        self.module_name = module_name
        self.config = config        
         

    def link(self, module):
        if (module.__class__.__bases__[0].__name__=="FeatureExtractor"):
            print ('------->link from feature extractor to classifier')
            feature_extractor = module
            self.data_source = feature_extractor.get_data_source()
            self.model = Model_Classifier(feature_extractor).to(self.device)        
               
         
    def get_model(self): 
        return self.model

 

    def train(self):
        print ('begin training...')
        epoch = int(self.config["epoch"])
        loss_fn = nn.CrossEntropyLoss()
        print (self.model.parameters())
        optimizer = torch.optim.SGD(self.model.parameters(), lr=1e-3)
        dataloader = self.data_source.get_train_data_labeled()
      

        size = len(dataloader.dataset)
        self.model.train()

        lossv = 0

        first_report_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        progress = 0   
        msg = {"epoch":0, "loss":0, "precision":0, "batch":0}                  
        super().report_status(self.project_name, first_report_time, True, progress, msg,'training')

        for i in range(epoch):
            for batch, (X, y) in enumerate(dataloader):
                X, y = X.to(self.device), y.to(self.device)
                #print (X.shape)
                #print (y.shape)
                #break

                # Compute prediction error
                pred = self.model(X)
                loss = loss_fn(pred, y)

                # Backpropagation
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                if batch % 300 == 0:
                    loss_v, current = loss.item(), batch * len(X)
                    print(f"loss: {loss_v:>7f}  [{current:>5d}/{size:>5d}]")            

                    progress = int(100*(size * i + current)/(epoch * size) )    
                    msg = {"epoch":i, "loss":loss_v, "precision":1/loss_v, "batch":batch}                  
                    super().report_status(self.project_name,first_report_time, False, progress, msg,'training')
        
        progress = 100 
        msg = {"epoch":epoch, "loss":loss_v,  "precision":1/loss_v, "batch":batch}
        super().report_status(self.project_name, first_report_time,False, progress, msg,'training')

        if self.config.__contains__("model"):
            model_name = self.config["model"]
            super().save_model(self.model, model_name, self.module_name)
        else:
            print("no matching model !")

    def test(self):
        if self.config.__contains__("model"):
            model_path = self.config["model"]
            print ("loading model SoFuseBackEnd/config/models/%s " %model_path)
            self.load_model('MoFarmBackEnd/config/models/%s' %model_path)
        
        first_report_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        progress = 0   
        msg = {"epoch":0, "loss":0, "precision":0, "batch":0}                  
        super().report_status(self.project_name, first_report_time, True, progress, msg,'testing')
                
        loss_fn = nn.CrossEntropyLoss()        
        dataloader = self.data_source.get_test_data()
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        self.model.eval()
        test_loss, correct = 0, 0
        with torch.no_grad():
            for X, y in dataloader:
                X, y = X.to(self.device), y.to(self.device)
                pred = self.model(X)
                test_loss += loss_fn(pred, y).item()
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()
        super().report_test_status(self.project_name,100,'stop')
        test_loss /= num_batches
        correct /= size
        
        print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

        first_report_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        progress = 100 
        msg = {"epoch":0, "loss":0, "precision":correct, "batch":0}                
        super().report_status(self.project_name, first_report_time, False, progress, msg,'testing')

    def get_test_result(self):
        print ('Not implemented ：Classifier.get_test_result')
    def test_on_train(self):
        print ('Not implemented ：Classifier.test_on_train')

    #def save_model(self, model_path):        
    #    torch.save(self.model.state_dict(), model_path)
        
    def load_model(self, model_path):
        self.model.load_state_dict(torch.load(model_path))

    def get_model(self):
        return self.model
    def freeze_model(self):
        for param in self.model.parameters():
            param.requires_grad = False
    def unfreeze_model(self):
        for param in self.model.parameters():
            param.requires_grad = True


if __name__ == '__main__':
    data_source  = MNISTDataSource ()
    extractor = MNIST_FeatureExtractor()
    classifier = MNIST_Classifier()
    
    extractor.set_data_source(data_source)
    classifier.set_feature_extractor(extractor)

    epochs = 20
    classifier.test()
    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        classifier.train()
        classifier.test()
   
    #classifier.save_model()
    #extractor.save_model()    '''
    #classifier.load_model()
    #classifier.test()
    
    print("Done!")    
    
    
