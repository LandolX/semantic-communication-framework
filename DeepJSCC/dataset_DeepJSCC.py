import os
from PIL import Image
from torch.utils.data import Dataset
import torchvision.transforms as transforms


class MedicalDataset(Dataset):
    def __init__(self, img_dir, mask_dir, size=(512, 512)):
        self.img_dir = img_dir
        self.mask_dir = mask_dir
        # 只读取 .png 或 .jpg 结尾的文件，防止读取到隐藏文件报错
        self.images = [f for f in os.listdir(img_dir) if f.endswith('.png') or f.endswith('.jpg')]
        self.size = size

        # 预处理：转为 Tensor 并归一化到 0-1
        self.transform = transforms.Compose([
            transforms.Resize(size),
            transforms.Grayscale(num_output_channels=1),  # 医学图通常是单通道
            transforms.ToTensor(),
        ])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        # 1. 获取原图文件名 (例如 "GongYihe002.jpg")
        img_name = self.images[idx]

        # 2. 构建掩码文件名：强制把后缀改成 .png
        # 无论原图是 .jpg 还是 .png，掩码都去读 .png
        mask_name = os.path.splitext(img_name)[0] + '.png'

        # 3. 拼接完整路径
        img_path = os.path.join(self.img_dir, img_name)
        mask_path = os.path.join(self.mask_dir, mask_name)

        # 4. 读取图片
        image = Image.open(img_path)

        try:
            mask = Image.open(mask_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到掩码文件！程序试图寻找：{mask_path}，请检查该文件是否存在。")

        image = self.transform(image)
        mask = self.transform(mask)

        # 确保 Mask 是二值的 (0 或 1)
        mask = (mask > 0).float()

        return image, mask
