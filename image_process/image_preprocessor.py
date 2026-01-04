from PIL import Image
import numpy as np


def preprocess_image(image):
    """
    预处理图像
    :param image: PIL Image对象
    :return: 预处理后的图像数组
    """
    # 转换为灰度图
    gray = image.convert('L')
    # 调整大小为统一尺寸
    resized = gray.resize((224, 224))
    # 转换为numpy数组
    img_array = np.array(resized, dtype=np.float32)
    # 归一化
    normalized = img_array / 255.0
    # 扩展维度，适应模型输入
    processed = np.expand_dims(normalized, axis=0)  # (1, 224, 224)
    processed = np.expand_dims(processed, axis=-1)   # (1, 224, 224, 1)
    return processed


def preprocess_image_custom(image, target_size=(224, 224), normalize=True, expand_dims=True):
    """
    自定义预处理图像
    :param image: PIL Image对象
    :param target_size: 目标尺寸，默认为(224, 224)
    :param normalize: 是否归一化，默认为True
    :param expand_dims: 是否扩展维度，默认为True
    :return: 预处理后的图像数组
    """
    # 转换为灰度图
    gray = image.convert('L')
    # 调整大小
    resized = gray.resize(target_size)
    # 转换为numpy数组
    img_array = np.array(resized, dtype=np.float32)
    
    # 归一化
    if normalize:
        img_array = img_array / 255.0
    
    # 扩展维度
    if expand_dims:
        img_array = np.expand_dims(img_array, axis=0)  # 添加批次维度
        img_array = np.expand_dims(img_array, axis=-1)  # 添加通道维度
    
    return img_array


if __name__ == "__main__":
    # 测试预处理功能
    print("=== 测试图像预处理功能 ===")
    print("预处理模块已加载")