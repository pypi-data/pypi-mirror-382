import torch
from torch import Generator
from torch.utils.data import Dataset, TensorDataset
from torchvision.transforms import ToTensor

from PIL import Image

from pathlib import Path



""" dataset classes """
class BSDSDataset(Dataset):
    def __init__(self, root_dir="data/bsds500", mode="train",
                 image_size=(256, 256), image_cnt=None,
                 gray=False, device="cpu"):
        """ BSDS500 Dataset construction

        Parameters
        ----------
        root_dir: str or Path object
            Local path to the dataset
        mode: str
            Dataset type: "train", "val" or "test"
        image_size: tuple of int
            Crop the image to the given size
        image_cnt: int
            If specified, extract at most the given number of images
        gray: bool
            If True, convert images to grayscale
        device: str or torch.device
            Device where the dataset is created
        """

        # Properties
        self.root_dir = Path(root_dir)
        self.mode = mode
        self.image_size = image_size
        self.gray = gray
        self.device = device

        # Create the list of corresponding images (sorted for reprocibility purpose)
        self.image_list = sorted((self.root_dir / self.mode).glob("*.jpg"))
        if image_cnt is not None:
            self.image_list = self.image_list[:image_cnt]
            
    def __repr__(self):
        """ Nice representation when displaying the variable """
        return f"BSDSDataset(mode={self.mode}, image_size={self.image_size})"

    def __len__(self):
        """ Number of samples """
        return len(self.image_list)

    def __getitem__(self, idx):
        """ Reading a sample """

        # set image path and id
        image_path = self.image_list[idx]
        image_id   = int(image_path.stem)

        # load and crop clean image
        clean_image = Image.open(image_path).convert('RGB')
        i = max(0, (clean_image.size[0] - self.image_size[0]) // 2)
        j = max(0, (clean_image.size[1] - self.image_size[1]) // 2)
        clean_image = clean_image.crop([
            i, j,
            min(clean_image.size[0], i + self.image_size[0]),
            min(clean_image.size[1], j + self.image_size[1]),
        ])
        clean_image = ToTensor()(clean_image).to(self.device) # move to the requested device

        # optional conversion to grayscale
        if self.gray:
            clean_image = clean_image.mean(-3, keepdim=True)

        return clean_image, image_id


class NoisyDataset(Dataset):
    def __init__(self, dataset, degradation_model, sigma=0.1, seed=None):
        """ Noisy Dataset construction

        Parameters
        ----------
        dataset: torch.utils.data.Dataset
            Original BSDS dataset
        degradation_model: function handle
            Function modeling the degradation model
        sigma: float
            Standard deviation of the noise (default: 0.1)
        seed: int
            If specified, the whole dataset is reproductible with given seed.
        """
        self.dataset = dataset
        self.degradation_model = degradation_model
        self.sigma = sigma
        self.seed = seed if seed is not None else Generator().seed()

    def __repr__(self):
        return f"NoisyDataset(dataset={self.dataset}, sigma={self.sigma})"

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        clean_image, image_id = self.dataset[idx]

        # generate noisy image
        noisy_image = self.degradation_model(clean_image, self.sigma, seed=self.seed)

        return noisy_image, clean_image, int(image_id)
    

    def toTensorDataset(self):
        """ Store the whole dataset in memory """
        noised_images, clean_images, images_id = zip(*self)
        return TensorDataset(
            torch.stack(noised_images),
            torch.stack(clean_images),
            torch.tensor(images_id),
        )
