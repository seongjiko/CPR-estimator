import numpy as np
import pandas as pd 
import os
import torch
import torch.nn as nn
from tqdm.auto import tqdm
import torch.nn.functional as F
import timm
from torchvision import transforms

from sklearn.metrics import accuracy_score
import cv2
import matplotlib.pyplot as plt
from torch.utils.data import Dataset,DataLoader
from PIL import Image 
import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2

class CustomDataset(Dataset):
    def __init__(self, images, transforms=None): # 이미지 경로가 아닌 이미지 입력
        self.images = images
        self.transforms = transforms
    
    def __getitem__(self, idx):
        x = self.images
        if self.transforms is not None:
            # x = Image.fromarray(x)  # 이미지를 PIL 이미지 객체로 변환
            x = np.array(x)
            transformed = self.transforms(image=x)  # 데이터를 명명된 인자로 전달
            x = transformed['image']
        return x
    
    def __len__(self):
        return len(self.images)

def start_estimation(critical_image):
    os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"]= "0"

    device = 'cuda'  if torch.cuda.is_available() else 'cpu'
   
    A_test_transform = A.Compose([
        A.Normalize(),
        A.pytorch.ToTensorV2(),
    ])
    
    test_dataset = CustomDataset(critical_image, A_test_transform)
    test_loader = DataLoader(test_dataset, batch_size = 1, shuffle=False)
    images = next(iter(test_loader))

    class MultiTaskModel(nn.Module):
        def __init__(self, num_classes1 = 1, num_classes2 = 1, num_classes3 = 1):
            super(MultiTaskModel, self).__init__()
            self.base_model = timm.create_model('efficientnetv2_rw_s', pretrained=True, num_classes=128)

            self.fc1 = nn.Linear(128, num_classes1)
            self.fc2 = nn.Linear(128, num_classes2)
            self.fc3 = nn.Linear(128, num_classes3)
            self.sig = nn.Sigmoid()

        def forward(self, x):

            x = self.base_model(x)
            hand = self.fc1(x)
            release = self.fc2(x)
            depth = self.fc3(x)
                   
            hand = self.sig(hand)
            release = self.sig(release)

            return depth, release, hand

    model = MultiTaskModel()
    model.to(device)
    model = nn.DataParallel(model).to(device)
    model.load_state_dict(torch.load('Best_QCPR.pt'))
    model.eval()
    images = images.to(device)
    output_depth, output_release, output_hand = model(images)
    output_depth_origin = (output_depth * 43) + 20
    
    hand = "부적절" if output_hand.item() >= 0.5 else "적절"
    release = "부적절" if output_release.item() >= 0.5 else "적절"
    depth = round(output_depth_origin.item(),2)

    # print("압박깊이 : ",depth, "mm")
    # print("손 위치 : ", hand)
    # print("완전이완여부 : ", release)

    return depth, release, hand
