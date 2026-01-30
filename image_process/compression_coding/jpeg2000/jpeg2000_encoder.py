#!/usr/bin/env python3
"""
JPEG2000编码器 - 传统编码baseline实现
将图像转换为JPEG2000格式的bytes数据，包含宏块分块和切片功能，每帧10个切片
"""

from PIL import Image
import io
import numpy as np
import struct
import os
import sys

# 导入通用分块编码和工具模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from image_process.block_coding.block_codec.block_codec import BlockCodec
from image_process.common.utils import simple_repeat_encode, ImageUtils


class JPEG2000Encoder:
    """
    JPEG2000编码器类
    """
    
    def __init__(self, quality=90, use_block_codec=False):
        """
        初始化JPEG2000编码器
        :param quality: 压缩质量，0-100
        :param use_block_codec: 是否使用分块编码，默认False（兼容旧模式）
        """
        self.quality = quality
        self.use_block_codec = use_block_codec
        # 初始化通用分块编码器
        self.block_codec = BlockCodec()
    
    def encode_image(self, image, use_block_codec=None, lossless=False):
        """
        将图像编码为JPEG2000格式的bytes数据，并添加FEC编码和交织
        :param image: 输入图像，可以是PIL Image对象或numpy数组
        :param use_block_codec: 是否使用分块编码，覆盖构造函数设置
        :param lossless: 是否使用无损压缩（JPEG2000不支持，仅作为兼容参数）
        :return: 编码后的bytes数据，包含FEC编码和交织
        """
        if use_block_codec is None:
            use_block_codec = self.use_block_codec
            
        try:
            # 转换为RGB图像
            image = ImageUtils.convert_to_rgb(image)
            
            # 保存为JPEG2000格式
            jpeg2000_data = ImageUtils.save_image_to_buffer(image, 'jpeg2000', self.quality)
            
            if use_block_codec:
                return self._encode_with_block_codec(jpeg2000_data)
            else:
                return self._encode_legacy(jpeg2000_data)
            
        except Exception as e:
            print(f"JPEG2000编码失败: {e}")
            raise
    
    def _encode_legacy(self, jpeg2000_data):
        """
        传统编码方式 - 简单的FEC
        :param jpeg2000_data: JPEG2000数据
        :return: 编码后的数据
        """
        if len(jpeg2000_data) > 100:
            header_part = jpeg2000_data[:100]
            body_part = jpeg2000_data[100:]
            fec_data = simple_repeat_encode(header_part, 2) + body_part
        else:
            fec_data = simple_repeat_encode(jpeg2000_data, 2)
        
        frame_marker = b'JP2K' + struct.pack('>I', len(jpeg2000_data)) + fec_data
        
        return frame_marker
    
    def _encode_with_block_codec(self, jpeg2000_data):
        """
        分块编码方式 - 使用通用分块编码器
        :param jpeg2000_data: JPEG2000数据
        :return: 编码后的数据
        """
        # 使用通用分块编码器进行编码
        return self.block_codec.encode(jpeg2000_data, 'jpeg2000')
    
    def encode_from_file(self, image_path, use_block_codec=None):
        """
        从文件加载图像并编码为JPEG2000格式
        :param image_path: 图像文件路径
        :param use_block_codec: 是否使用分块编码
        :return: JPEG2000格式的bytes数据
        """
        try:
            image = Image.open(image_path)
            return self.encode_image(image, use_block_codec)
        except Exception as e:
            print(f"从文件编码JPEG2000失败: {e}")
            raise
    
    def get_compression_ratio(self, original_image, jpeg2000_data):
        """
        计算压缩比
        :param original_image: 原始图像（PIL Image对象或numpy数组）
        :param jpeg2000_data: JPEG2000编码后的bytes数据
        :return: 压缩比（原始大小 / 压缩后大小）
        """
        try:
            if isinstance(original_image, np.ndarray):
                original_size = original_image.nbytes
            else:
                original_array = np.array(original_image)
                original_size = original_array.nbytes
            
            compressed_size = len(jpeg2000_data)
            compression_ratio = original_size / compressed_size
            
            return compression_ratio
            
        except Exception as e:
            print(f"计算压缩比失败: {e}")
            return 0.0


def jpeg2000_encode(image, quality=90, use_block_codec=False):
    """
    便捷的JPEG2000编码函数
    :param image: 输入图像（PIL Image对象或numpy数组）
    :param quality: JPEG2000压缩质量，0-100
    :param use_block_codec: 是否使用分块编码
    :return: JPEG2000格式的bytes数据
    """
    encoder = JPEG2000Encoder(quality, use_block_codec=use_block_codec)
    return encoder.encode_image(image)


def jpeg2000_encode_from_file(image_path, quality=90, use_block_codec=False):
    """
    便捷的从文件编码JPEG2000函数
    :param image_path: 图像文件路径
    :param quality: JPEG2000压缩质量，0-100
    :param use_block_codec: 是否使用分块编码
    :return: JPEG2000格式的bytes数据
    """
    encoder = JPEG2000Encoder(quality, use_block_codec=use_block_codec)
    return encoder.encode_from_file(image_path)


if __name__ == "__main__":
    import os
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    test_image_path = os.path.join(project_root, 'data_input', 'image', '1-img-00000-00002_00002.png')
    
    if os.path.exists(test_image_path):
        encoder = JPEG2000Encoder(quality=90)
        jpeg2000_data = encoder.encode_from_file(test_image_path)
        print(f"传统编码: JPEG2000数据大小: {len(jpeg2000_data)} bytes")
        
        encoder_block = JPEG2000Encoder(quality=90, use_block_codec=True)
        jpeg2000_data_block = encoder_block.encode_from_file(test_image_path)
        print(f"分块编码: JPEG2000数据大小: {len(jpeg2000_data_block)} bytes")
        
    else:
        print(f"测试图像不存在: {test_image_path}")
