import os
import numpy as np
import torch
from torchvision import datasets
from typing import Literal
from pathlib import Path
from byzh.core import B_os

from ..standard import b_data_standard2d
from .base import Download_Base


class B_Download_MNIST(Download_Base):
    def __init__(self, save_dir='./MNIST', mean=None, std=None):
        super().__init__(save_dir, mean, std)

    def _get_num_classes(self):
        return 10

    def _get_shape(self):
        return (1, 28, 28)
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
        train_data = datasets.MNIST(root=downloading_dir, train=True, download=True)
        test_data = datasets.MNIST(root=downloading_dir, train=False, download=True)

        # 拆分
        X_train = torch.tensor(train_data.data).unsqueeze(1) / 255.0  # shape [60000, 1, 28, 28]
        y_train = torch.tensor(train_data.targets)  # shape [60000]
        X_test = torch.tensor(test_data.data).unsqueeze(1) / 255.0  # shape [10000, 1, 28, 28]
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


class B_Download_FashionMNIST(Download_Base):
    def __init__(self, save_dir='./FashionMNIST', mean=None, std=None):
        super().__init__(save_dir, mean, std)

    def _get_num_classes(self):
        return 10

    def _get_shape(self):
        return (1, 28, 28)

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
        train_data = datasets.FashionMNIST(root=downloading_dir, train=True, download=True)
        test_data = datasets.FashionMNIST(root=downloading_dir, train=False, download=True)

        # 拆分
        X_train = torch.tensor(train_data.data).unsqueeze(1) / 255.0  # shape [60000, 1, 28, 28]
        y_train = torch.tensor(train_data.targets)  # shape [60000]
        X_test = torch.tensor(test_data.data).unsqueeze(1) / 255.0  # shape [10000, 1, 28, 28]
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


class B_Download_KMNIST(Download_Base):
    def __init__(self, save_dir='./KMNIST', mean=None, std=None):
        super().__init__(save_dir, mean, std)

    def _get_num_classes(self):
        return 10

    def _get_shape(self):
        return (1, 28, 28)

    def download(self):
        """
        使用 torchvision 下载 KMNIST
        :return: X_train, y_train, X_test, y_test
        """
        downloading_dir = os.path.join(self.save_dir, f'{self.name}_download_dir')
        if self._check(self.save_paths):
            X_train = torch.load(self.save_paths[0])
            y_train = torch.load(self.save_paths[1])
            X_test = torch.load(self.save_paths[2])
            y_test = torch.load(self.save_paths[3])
            return X_train, y_train, X_test, y_test

        # torchvision 数据集
        train_data = datasets.KMNIST(root=downloading_dir, train=True, download=True)
        test_data = datasets.KMNIST(root=downloading_dir, train=False, download=True)

        # 转 tensor
        X_train = torch.tensor(train_data.data).unsqueeze(1) / 255.0  # [60000, 1, 28, 28]
        y_train = torch.tensor(train_data.targets)  # [60000]
        X_test = torch.tensor(test_data.data).unsqueeze(1) / 255.0  # [10000, 1, 28, 28]
        y_test = torch.tensor(test_data.targets)  # [10000]
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


class B_Download_EMNIST(Download_Base):
    def __init__(self, save_dir='./EMNIST', mean=None, std=None, split='byclass'):
        '''
        :param split: EMNIST 的划分方式，常用 'byclass'
                      其它还包括 'bymerge', 'balanced', 'letters', 'digits', 'mnist'
        '''
        self.split = split
        super().__init__(save_dir, mean, std)

    def _get_num_classes(self):
        match self.split:
            case 'byclass': return 62
            case 'bymerge': return 47
            case 'balanced': return 47
            case 'letters': return 26
            case 'digits': return 10
            case 'mnist': return 10
            case _: raise ValueError(f"split={self.split}错误")

    def _get_shape(self):
        return (1, 28, 28)

    def download(self):
        """
        使用 torchvision 下载 EMNIST
        :return: X_train, y_train, X_test, y_test
        """
        downloading_dir = os.path.join(self.save_dir, f'{self.name}_download_dir')
        if self._check(self.save_paths):
            X_train = torch.load(self.save_paths[0])
            y_train = torch.load(self.save_paths[1])
            X_test = torch.load(self.save_paths[2])
            y_test = torch.load(self.save_paths[3])
            return X_train, y_train, X_test, y_test

        # torchvision 数据集
        train_data = datasets.EMNIST(root=downloading_dir, split=self.split, train=True, download=True)
        test_data = datasets.EMNIST(root=downloading_dir, split=self.split, train=False, download=True)

        # 转 tensor
        X_train = torch.tensor(train_data.data).unsqueeze(1) / 255.0
        y_train = torch.tensor(train_data.targets)
        X_test = torch.tensor(test_data.data).unsqueeze(1) / 255.0
        y_test = torch.tensor(test_data.targets)
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


    # def _download_HF(self):
    #     """
    #     使用 Hugging Face datasets 下载 MNIST
    #
    #     :param save_dir: 保存路径
    #     :param mean, std: 标准化用
    #     :return: X_train, y_train, X_test, y_test (torch.Tensor)
    #     """
    #     save_paths = [
    #         os.path.join(self.save_dir, f'{self.name}_X_train.pt'),
    #         os.path.join(self.save_dir, f'{self.name}_y_train.pt'),
    #         os.path.join(self.save_dir, f'{self.name}_X_test.pt'),
    #         os.path.join(self.save_dir, f'{self.name}_y_test.pt'),
    #     ]
    #
    #     if self.__check(save_paths):
    #         X_train = torch.load(save_paths[0])
    #         y_train = torch.load(save_paths[1])
    #         X_test = torch.load(save_paths[2])
    #         y_test = torch.load(save_paths[3])
    #         return X_train, y_train, X_test, y_test
    #
    #     # HF 数据集
    #     from datasets import load_dataset
    #     train_ds = load_dataset("ylecun/mnist", split="train")
    #     test_ds = load_dataset("ylecun/mnist", split="test")
    #
    #     # 转 torch.Tensor
    #     X_train = torch.tensor(np.stack([np.array(img) for img in train_ds['image']])).unsqueeze(1) / 255.0
    #     y_train = torch.tensor(train_ds['label'])
    #     X_test = torch.tensor(np.stack([np.array(img) for img in test_ds['image']])).unsqueeze(1) / 255.0
    #     y_test = torch.tensor(test_ds['label'])
    #     print(f"X_train.shape: {X_train.shape}")
    #     print(f"y_train.shape: {y_train.shape}")
    #     print(f"X_test.shape: {X_test.shape}")
    #     print(f"y_test.shape: {y_test.shape}")
    #     B, C, H, W = X_train.shape
    #     print(f"X_train[{B // 2}, {C // 2}, {H // 2}]=\n{X_train[B // 2, C // 2, H // 2]}")
    #
    #     # 标准化
    #     X_train, X_test = b_data_standard2d([X_train, X_test], template_data=X_train, mean=self.mean, std=self.std)
    #
    #     # 保存
    #     os.makedirs(self.save_dir, exist_ok=True)
    #     torch.save(X_train, save_paths[0])
    #     torch.save(y_train, save_paths[1])
    #     torch.save(X_test, save_paths[2])
    #     torch.save(y_test, save_paths[3])
    #
    #     return X_train, y_train, X_test, y_test