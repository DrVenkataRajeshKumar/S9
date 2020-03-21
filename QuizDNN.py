
from datetime import datetime 
print("Current Date/Time: ", datetime.now())

from torchsummary import summary
import torch
import torch.nn as nn
import torch.nn.functional as F
from eva4modeltrainer import ModelTrainer

class Net(nn.Module):
    """
    Base network that defines helper functions, summary and mapping to device
    """
    def conv2d(self, in_channels, out_channels, kernel_size=(3,3), dilation=1, groups=1, padding=1, bias=False, padding_mode="zeros"):
      return [nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, groups=groups, dilation=dilation, padding=padding, bias=bias, padding_mode=padding_mode)]

    def separable_conv2d(self, in_channels, out_channels, kernel_size=(3,3), dilation=1, padding=1, bias=False, padding_mode="zeros"):
      return [nn.Conv2d(in_channels=in_channels, out_channels=in_channels, kernel_size=kernel_size, groups=in_channels, dilation=dilation, padding=padding, bias=bias, padding_mode=padding_mode),
              nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=(1,1), bias=bias)]

    def activate(self, l, out_channels, bn=True, dropout=0, relu=True):
      if bn:
        l.append(nn.BatchNorm2d(out_channels))
      if dropout>0:
        l.append(nn.Dropout(dropout))
      if relu:
        l.append(nn.ReLU())

      return nn.Sequential(*l)

    def create_conv2d(self, in_channels, out_channels, kernel_size=(3,3), dilation=1, groups=1, padding=1, bias=False, bn=True, dropout=0, relu=True, padding_mode="zeros"):
      return self.activate(self.conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, groups=groups, dilation=dilation, padding=padding, bias=bias, padding_mode=padding_mode), out_channels, bn, dropout, relu)

    def create_depthwise_conv2d(self, in_channels, out_channels, kernel_size=(3,3), dilation=1, padding=1, bias=False, bn=True, dropout=0, relu=True, padding_mode="zeros"):
      return self.activate(self.separable_conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, dilation=dilation, padding=padding, bias=bias, padding_mode=padding_mode),
                 out_channels, bn, dropout, relu)

    def __init__(self, name="Model"):
        super(Net, self).__init__()
        self.trainer = None
        self.name = name

    def summary(self, input_size): #input_size=(1, 28, 28)
      summary(self, input_size=input_size)

    def gotrain(self, optimizer, train_loader, test_loader, epochs, statspath, scheduler=None, batch_scheduler=False, L1lambda=0):
      self.trainer = ModelTrainer(self, optimizer, train_loader, test_loader, statspath, scheduler, batch_scheduler, L1lambda)
      self.trainer.run(epochs)

    def stats(self):
      return self.trainer.stats if self.trainer else None
class QuizDNN(Net):
    def __init__(self, name="Model", dropout_value=0):
      self.num_channels=64
      super(QuizDNN, self).__init__(name)
      self.conv1=nn.Sequential(nn.Conv2d(3,64,3,padding=1,bias=False))
      self.conv2=nn.Sequential(nn.BatchNorm2d(64),nn.ReLU(),nn.Conv2d(64,64,3,padding=1,bias=False))
      self.conv3=nn.Sequential(nn.BatchNorm2d(64),nn.ReLU(),nn.Conv2d(64,64,3,padding=1,bias=False))
      self.one1=nn.Sequential(nn.Conv2d(64,128,1,bias=False),nn.BatchNorm2d(128),nn.ReLU())
      self.pool1=nn.MaxPool2d(2)
      self.conv4=nn.Sequential(nn.Conv2d(128,128,3,padding=1,bias=False))
      self.conv5=nn.Sequential(nn.BatchNorm2d(128),nn.ReLU(),nn.Conv2d(128,128,3,padding=1,bias=False))
      self.conv6=nn.Sequential(nn.BatchNorm2d(128),nn.ReLU(),nn.Conv2d(128,128,3,padding=1,bias=False))
      self.one2=nn.Sequential(nn.Conv2d(128,256,1,bias=False),nn.BatchNorm2d(256),nn.ReLU())
      self.pool2=nn.MaxPool2d(2)
      self.conv7=nn.Sequential(nn.Conv2d(256,256,3,padding=1,bias=False))
      self.conv8=nn.Sequential(nn.BatchNorm2d(256),nn.ReLU(),nn.Conv2d(256,256,3,padding=1,bias=False))
      self.conv9=nn.Sequential(nn.BatchNorm2d(256),nn.ReLU(),nn.Conv2d(256,256,3,padding=1,bias=False))
      self.conv10=nn.Conv2d(256,10,1)
    def forward(self, x):
      x1 = self.conv1(x)
      x2 = self.conv2(x1)
      x3= self.conv3(x1+x2)
      x4 = self.pool1(x1+x2+x3)
      x4 = self.one1(x4)
      x5 = self.conv4(x4)
      x6 = self.conv5(x4+x5)
      x7 = self.conv6(x4+x5+x6)
      x8 = self.pool2(x5+x6+x7)
      x8 = self.one2(x8)
      x9 = self.conv7(x8)
      x10 = self.conv8(x8+x9)
      x11 = self.conv9(x8+x9+x10)
      out = F.adaptive_avg_pool2d(x11, 1)
      out = self.conv10(out)
      out = out.view(-1, 10)
      return F.log_softmax(out, dim=-1)