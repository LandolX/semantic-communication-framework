import os
from PIL import Image
import numpy as np

class ImageLoader:
    def __init__(self, image_dir):
        """
        初始化图像加载器
        :param image_dir: 图像文件夹路径
        """
        self.image_dir = image_dir
        self.image_files = self._get_image_files()
    
    def _get_image_files(self):
        """
        获取文件夹中所有图像文件
        :return: 图像文件路径列表
        """
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        image_files = []
        
        for file in os.listdir(self.image_dir):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(self.image_dir, file))
        
        return sorted(image_files)
    
    def load_images(self):
        """
        循环加载并返回所有原始图像
        :return: 生成器，每次返回一个原始图像
        """
        for image_path in self.image_files:
            try:
                # 读取图像
                with Image.open(image_path) as img:
                    # 转换为RGB格式（处理不同图像模式）
                    img = img.convert('RGB')
                    # 转换为numpy数组返回
                    yield np.array(img)
            except Exception as e:
                print(f"Warning: Failed to read image {image_path}, error: {e}")
                continue
    
    def get_image_count(self):
        """
        获取图像数量
        :return: 图像数量
        """
        return len(self.image_files)
    
    def show_image_info(self):
        """
        显示图像信息
        """
        print(f"Image directory: {self.image_dir}")
        print(f"Total images: {self.get_image_count()}")
        print("Image files:")
        for i, file in enumerate(self.image_files):
            print(f"  {i+1}. {os.path.basename(file)}")


def load_images_from_dir(image_dir):
    """
    从指定目录加载所有图像的便捷函数
    :param image_dir: 图像文件夹路径
    :return: 图像生成器，每次返回一个原始图像
    """
    loader = ImageLoader(image_dir)
    return loader.load_images()


def get_image_loader(image_dir):
    """
    获取图像加载器实例
    :param image_dir: 图像文件夹路径
    :return: ImageLoader实例
    """
    return ImageLoader(image_dir)


def example_usage():
    """
    示例用法
    """
    # 获取当前文件所在目录
    current_dir = os.path.dirname(__file__)
    # 图像文件夹路径
    image_dir = os.path.join(current_dir, 'image')
    
    print("=== Example 1: Using load_images_from_dir function ===")
    # 使用便捷函数加载原始图像
    images = load_images_from_dir(image_dir)
    
    # 循环处理图像
    image_count = 0
    for img in images:
        image_count += 1
        print(f"Processing image {image_count}, shape: {img.shape}")
        if image_count >= 2:  # 只处理前2张
            break
    
    print("\n=== Example 2: Using ImageLoader class directly ===")
    # 直接使用ImageLoader类
    loader = get_image_loader(image_dir)
    loader.show_image_info()
    
    # 处理所有图像（这里只处理前2张）
    image_count = 0
    for img in loader.load_images():
        image_count += 1
        print(f"Processing image {image_count}, shape: {img.shape}")
        if image_count >= 2:  # 只处理前2张
            break


if __name__ == "__main__":
    example_usage()