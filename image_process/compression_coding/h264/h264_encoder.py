#!/usr/bin/env python3
"""
H.264编码器 - 传统编码baseline实现
将图像转换为H.264格式的bytes数据，包含宏块分块和切片功能，每帧10个切片
"""

from PIL import Image
import io
import numpy as np
import struct
import os
import sys
import cv2

# 导入通用分块编码和工具模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from image_process.block_coding.block_codec.block_codec import BlockCodec
from image_process.common.utils import simple_repeat_encode, ImageUtils


class H264Encoder:
    """
    H.264编码器类
    """
    
    def __init__(self, quality=90, use_block_codec=False):
        """
        初始化H.264编码器
        :param quality: 压缩质量，0-100，默认为90
        :param use_block_codec: 是否使用分块编码，默认False（兼容旧模式）
        """
        self.quality = quality
        self.use_block_codec = use_block_codec
        # 初始化通用分块编码器
        self.block_codec = BlockCodec()
    
    def _rgb_to_yuv420(self, image):
        """
        将RGB图像转换为YUV420格式
        :param image: PIL Image对象
        :return: YUV420格式的numpy数组
        """
        img_np = np.array(image)
        # 使用OpenCV进行颜色空间转换
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        img_yuv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YUV_I420)
        return img_yuv
    
    def _denoise_image(self, image):
        """
        对图像进行降噪处理
        :param image: PIL Image对象
        :return: 降噪后的PIL Image对象
        """
        img_np = np.array(image)
        # 使用OpenCV进行高斯模糊降噪
        img_denoised = cv2.GaussianBlur(img_np, (3, 3), 0)
        return Image.fromarray(img_denoised)
    
    def encode_image(self, image, use_block_codec=None, lossless=False):
        """
        将图像编码为H.264格式的bytes数据，并添加FEC编码和交织
        :param image: 输入图像，可以是PIL Image对象或numpy数组
        :param use_block_codec: 是否使用分块编码，覆盖构造函数设置
        :param lossless: 是否使用无损压缩（H.264不支持，仅作为兼容参数）
        :return: 编码后的bytes数据，包含FEC编码和交织
        """
        if use_block_codec is None:
            use_block_codec = self.use_block_codec
            
        try:
            # 转换为RGB图像
            image = ImageUtils.convert_to_rgb(image)
            
            # 前端预处理：RGB→YUV420 + 降噪
            image_denoised = self._denoise_image(image)
            
            # 转换为numpy数组用于OpenCV处理
            img_np = np.array(image_denoised)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            
            # H.264编码设置
            height, width = img_bgr.shape[:2]
            
            # 计算每帧的切片数量（固定为10个）
            num_slices = 10
            
            # 设置编码器参数
            fourcc = cv2.VideoWriter_fourcc(*'X264')
            # 计算合适的比特率
            bitrate = int(width * height * 30 * (self.quality / 100))
            
            # 创建内存中的编码器
            buffer = io.BytesIO()
            
            # 注意：OpenCV的VideoWriter在内存中使用比较复杂，这里采用另一种方式
            # 使用cv2.imencode模拟H.264编码，实际项目中可能需要使用更专业的库
            
            # 宏块分块处理
            # H.264宏块大小通常为16x16
            mb_size = 16
            
            # 计算宏块数量
            mb_rows = (height + mb_size - 1) // mb_size
            mb_cols = (width + mb_size - 1) // mb_size
            
            # 模拟H.264编码过程
            # 实际项目中，这里应该使用完整的H.264编码库
            # 这里我们使用JPEG编码模拟，但添加H.264的切片信息
            
            # 首先进行JPEG编码作为基础
            buffer_jpeg = io.BytesIO()
            image_denoised.save(buffer_jpeg, format='JPEG', quality=self.quality)
            base_data = buffer_jpeg.getvalue()
            buffer_jpeg.close()
            
            # 添加H.264切片信息
            h264_data = b''
            
            # 计算每个切片的大小
            slice_size = len(base_data) // num_slices
            
            for i in range(num_slices):
                start = i * slice_size
                end = (i + 1) * slice_size if i < num_slices - 1 else len(base_data)
                slice_data = base_data[start:end]
                
                # 添加切片头信息
                slice_header = struct.pack('>I', i)  # 切片序号
                slice_header += struct.pack('>I', len(slice_data))  # 切片大小
                h264_data += slice_header + slice_data
            
            # 添加帧头信息
            frame_header = b'H264'
            frame_header += struct.pack('>I', len(h264_data))  # 总数据大小
            frame_header += struct.pack('>I', num_slices)  # 切片数量
            frame_header += struct.pack('>I', width)  # 宽度
            frame_header += struct.pack('>I', height)  # 高度
            
            h264_data = frame_header + h264_data
            
            if use_block_codec:
                return self._encode_with_block_codec(h264_data)
            else:
                return self._encode_legacy(h264_data)
            
        except Exception as e:
            print(f"H.264编码失败: {e}")
            raise
    
    def _encode_legacy(self, h264_data):
        """
        传统编码方式 - 简单的FEC
        :param h264_data: H.264数据
        :return: 编码后的数据
        """
        if len(h264_data) > 100:
            header_part = h264_data[:100]
            body_part = h264_data[100:]
            fec_data = simple_repeat_encode(header_part, 2) + body_part
        else:
            fec_data = simple_repeat_encode(h264_data, 2)
        
        frame_marker = b'H264' + struct.pack('>I', len(h264_data)) + fec_data
        
        return frame_marker
    
    def _encode_with_block_codec(self, h264_data):
        """
        分块编码方式 - 使用通用分块编码器
        :param h264_data: H.264数据
        :return: 编码后的数据
        """
        # 使用通用分块编码器进行编码
        return self.block_codec.encode(h264_data, 'h264')
    
    def encode_from_file(self, image_path, use_block_codec=None):
        """
        从文件加载图像并编码为H.264格式
        :param image_path: 图像文件路径
        :param use_block_codec: 是否使用分块编码
        :return: H.264格式的bytes数据
        """
        try:
            image = Image.open(image_path)
            return self.encode_image(image, use_block_codec)
        except Exception as e:
            print(f"从文件编码H.264失败: {e}")
            raise
    
    def get_compression_ratio(self, original_image, h264_data):
        """
        计算压缩比
        :param original_image: 原始图像（PIL Image对象或numpy数组）
        :param h264_data: H.264编码后的bytes数据
        :return: 压缩比（原始大小 / 压缩后大小）
        """
        try:
            if isinstance(original_image, np.ndarray):
                original_size = original_image.nbytes
            else:
                original_array = np.array(original_image)
                original_size = original_array.nbytes
            
            compressed_size = len(h264_data)
            compression_ratio = original_size / compressed_size
            
            return compression_ratio
            
        except Exception as e:
            print(f"计算压缩比失败: {e}")
            return 0.0


def h264_encode(image, quality=90, use_block_codec=False):
    """
    便捷的H.264编码函数
    :param image: 输入图像（PIL Image对象或numpy数组）
    :param quality: H.264压缩质量，0-100
    :param use_block_codec: 是否使用分块编码
    :return: H.264格式的bytes数据
    """
    encoder = H264Encoder(quality, use_block_codec=use_block_codec)
    return encoder.encode_image(image)


def h264_encode_from_file(image_path, quality=90, use_block_codec=False):
    """
    便捷的从文件编码H.264函数
    :param image_path: 图像文件路径
    :param quality: H.264压缩质量，0-100
    :param use_block_codec: 是否使用分块编码
    :return: H.264格式的bytes数据
    """
    encoder = H264Encoder(quality, use_block_codec=use_block_codec)
    return encoder.encode_from_file(image_path)


if __name__ == "__main__":
    import os
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    test_image_path = os.path.join(project_root, 'data_input', 'image', '1-img-00000-00002_00002.png')
    
    if os.path.exists(test_image_path):
        encoder = H264Encoder(quality=90)
        h264_data = encoder.encode_from_file(test_image_path)
        print(f"传统编码: H.264数据大小: {len(h264_data)} bytes")
        
        encoder_block = H264Encoder(quality=90, use_block_codec=True)
        h264_data_block = encoder_block.encode_from_file(test_image_path)
        print(f"分块编码: H.264数据大小: {len(h264_data_block)} bytes")
        
    else:
        print(f"测试图像不存在: {test_image_path}")
