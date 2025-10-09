import torch


def chooseDevice(device=None):
    if device == None:
        # setting device on GPU if available, else MPS (Apple M1) or CPU
        if torch.cuda.is_available():
            device = torch.device('cuda') # CUDA backend for NVIDIA or AMD graphic cards
        else:
            try:
                if torch.backends.mps.is_available():
                    device = torch.device('mps') # MPS for Apple M# processors
                else:
                    device = torch.device('cpu')
            except AttributeError:
                device = torch.device('cpu')
    else:
        device = torch.device(device)
    
    print('Using device:', device)
    print()

    # additional info when using cuda
    if device.type == 'cuda':
        print(torch.cuda.get_device_name(0))
        print('Memory Usage:')
        print('Allocated:', round(torch.cuda.memory_allocated(0)/1024**3,1), 'GB')
        print('Cached:   ', round(torch.cuda.memory_reserved(0)/1024**3,1), 'GB')

    return device



def torchImg2Numpy(image):
    # reorder dimensions (C, N, M) -> (M, N, C) and move to CPU
    image = torch.moveaxis(image, [0, 1, 2], [2, 0, 1]).to('cpu')

    if image.shape[-1] == 1:
        image = image[..., 0]

    np_img = image.numpy()

    return (np_img-np.min(np_img)) / (np.max(np_img)-np.min(np_img))
    


def getData(trainer, mode):
    data = dict()
    for epoch, record in trainer.history[mode]:
        data.setdefault("epoch", []).append(epoch)
        for metric, value in record.items():
            data.setdefault(metric, []).append(value)

    return data

