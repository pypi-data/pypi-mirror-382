import os
import numpy as np
import torch
from torchvision import datasets
from typing import Literal
from pathlib import Path
from byzh.core import B_os

from ..standard import b_data_standard2d
from .base import Download_Base

class B_Download_CIFAR10(Download_Base):
    def __init__(self, save_dir='./CIFAR10', mean=None, std=None):
        super().__init__(save_dir=save_dir, mean=mean, std=std)
    def _get_num_classes(self):
        return 10
    def _get_shape(self):
        return (3, 32, 32)
    def download(self):
        '''
        采用 torchvision 下载数据集\n

        :param save_dir:
        :return: X_train, y_train, X_test, y_test
        '''
        downloading_dir = os.path.join(self.save_dir, f'{self.name}_download_dir')
        if self._check(self.save_paths):
            X_train = torch.load(self.save_paths[0])
            y_train = torch.load(self.save_paths[1])
            X_test = torch.load(self.save_paths[2])
            y_test = torch.load(self.save_paths[3])
            return X_train, y_train, X_test, y_test

        # 未标准化
        train_data = datasets.CIFAR10(root=downloading_dir, train=True, download=True)
        test_data = datasets.CIFAR10(root=downloading_dir, train=False, download=True)

        # 拆分
        X_train = torch.tensor(train_data.data).permute(0, 3, 1, 2) / 255.0  # shape [50000, 3, 32, 32]
        y_train = torch.tensor(train_data.targets)  # shape [50000]
        X_test = torch.tensor(test_data.data).permute(0, 3, 1, 2) / 255.0  # shape [10000, 3, 32, 32]
        y_test = torch.tensor(test_data.targets)  # shape [10000]
        print(f"X_train.shape: {X_train.shape}")
        print(f"y_train.shape: {y_train.shape}")
        print(f"X_test.shape: {X_test.shape}")
        print(f"y_test.shape: {y_test.shape}")
        B, C, H, W = X_train.shape
        print(f"X_train[{B // 2}, {C // 2}, {H // 2}]=\n{X_train[B // 2, C // 2, H // 2]}")

        # 保存
        os.makedirs(self.save_dir, exist_ok=True)
        torch.save(X_train, self.save_paths[0])
        torch.save(y_train, self.save_paths[1])
        torch.save(X_test, self.save_paths[2])
        torch.save(y_test, self.save_paths[3])

        B_os.rm(downloading_dir)

        return X_train, y_train, X_test, y_test


class B_Download_CIFAR100(Download_Base):
    def __init__(self, save_dir='./CIFAR100', mean=None, std=None):
        super().__init__(save_dir=save_dir, mean=mean, std=std)
    def _get_num_classes(self):
        return 100
    def _get_shape(self):
        return (3, 32, 32)
    def download(self):
        '''
        采用 torchvision 下载数据集\n

        :param save_dir:
        :return: X_train, y_train, X_test, y_test
        '''
        downloading_dir = os.path.join(self.save_dir, f'{self.name}_download_dir')
        if self._check(self.save_paths):
            X_train = torch.load(self.save_paths[0])
            y_train = torch.load(self.save_paths[1])
            X_test = torch.load(self.save_paths[2])
            y_test = torch.load(self.save_paths[3])
            return X_train, y_train, X_test, y_test

        # 未标准化
        train_data = datasets.CIFAR100(root=downloading_dir, train=True, download=True)
        test_data = datasets.CIFAR100(root=downloading_dir, train=False, download=True)

        # 拆分
        X_train = torch.tensor(train_data.data).permute(0, 3, 1, 2) / 255.0  # shape [50000, 3, 32, 32]
        y_train = torch.tensor(train_data.targets)  # shape [50000]
        X_test = torch.tensor(test_data.data).permute(0, 3, 1, 2) / 255.0  # shape [10000, 3, 32, 32]
        y_test = torch.tensor(test_data.targets)  # shape [10000]
        print(f"X_train.shape: {X_train.shape}")
        print(f"y_train.shape: {y_train.shape}")
        print(f"X_test.shape: {X_test.shape}")
        print(f"y_test.shape: {y_test.shape}")
        B, C, H, W = X_train.shape
        print(f"X_train[{B // 2}, {C // 2}, {H // 2}]=\n{X_train[B // 2, C // 2, H // 2]}")

        # 保存
        os.makedirs(self.save_dir, exist_ok=True)
        torch.save(X_train, self.save_paths[0])
        torch.save(y_train, self.save_paths[1])
        torch.save(X_test, self.save_paths[2])
        torch.save(y_test, self.save_paths[3])

        B_os.rm(downloading_dir)

        return X_train, y_train, X_test, y_test
