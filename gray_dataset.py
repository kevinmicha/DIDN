import torch.utils.data as data
import torch
from torch.autograd import Variable
import h5py
import numpy as np


class DatasetFromHdf5(data.Dataset):
    def __init__(self, file_path):
        super(DatasetFromHdf5, self).__init__()
        self.path = file_path

    def __getitem__(self, index):
        hf = h5py.File(self.path, 'r')
        self.data = hf.get('data')
        self.target = hf.get('label')

        return torch.from_numpy(self.data[index, :, :]).float(), torch.from_numpy(self.target[index, :, :]).float()

    def __len__(self):
        hf = h5py.File(self.path, 'r')
        temp_data = hf.get('data')

        return temp_data.shape[0]


def tensor_augmentation(batch):  # Input, Output: (2,16,64,64) size tensor
    batch_return = []
    data = batch[0]  # (16,64,64)
    target = batch[1]  # (16,64,64)
    data_result = np.zeros(data.shape)
    target_result = np.zeros(target.shape)

    for i in range(data.shape[0]):
        a = np.random.randint(4, size=1)[0]  # 0-3
        b = np.random.randint(2, size=1)[0]  # 0-1

        # rotation
        data_temp = np.rot90(data[i, :, :], a).copy()
        target_temp = np.rot90(target[i, :, :], a).copy()

        # flip
        if b == 1:
            data_temp = np.fliplr(data_temp).copy()
            target_temp = np.fliplr(target_temp).copy()

        data_result[i, :, :] = data_temp
        target_result[i, :, :] = target_temp

    data_result = torch.from_numpy(data_result).float()
    target_result = torch.from_numpy(target_result).float()

    batch_return.append(data_result)
    batch_return.append(target_result)

    return batch_return

def add_noise(batch, return_noise_level):
    data = (batch[0]/255).float() # normalisation
    noise_std_range = (0, 55)
    noise = np.zeros((np.shape(data)))
    noise_std = np.random.uniform(
        low=noise_std_range[0],
        high=noise_std_range[1],
        size=np.shape(data)[0],
    )
    for i in range(np.shape(noise)[0]):
        noise[i,:,:] = np.random.normal(size=np.shape(data[i,:,:]), loc=0.0, scale=noise_std[i]/255)
    noise = torch.from_numpy(noise).float()
    noise_std = torch.from_numpy(noise_std).float()

    output = Variable(data + noise).view(16, 1, batch[0].shape[1], batch[0].shape[2])
    noise_std = Variable(noise_std/255).view(16, 1, 1, 1)
    if return_noise_level:
        return output, noise_std
    else:
        return output
