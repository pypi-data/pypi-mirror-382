import torch
from torch.utils.data import TensorDataset, DataLoader

def b_get_dataloader_from_tensor(
    X_train, y_train, X_test, y_test,
    batch_size=128,
    num_workers=2,
):
    """
    根据张量构建 DataLoader

    :param X_train, y_train, X_test, y_test: torch.Tensor
    :param batch_size: batch 大小
    :param num_workers: DataLoader 的子进程数
    :return: train_loader, test_loader
    """
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers
    )

    return train_loader, test_loader