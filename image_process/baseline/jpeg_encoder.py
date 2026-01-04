#!/usr/bin/env python3
"""
JPEG编码器 - 传统编码baseline实现
将图像转换为JPEG格式的bytes数据，与数字通信系统对齐
"""

from PIL import Image
import io
import numpy as np
import struct


class JPEGEncoder:
    """
    JPEG编码器类
    """
    
    def __init__(self, quality=90):
        """
        初始化JPEG编码器
        :param quality: JPEG压缩质量，0-100，默认为90
        """
        self.quality = quality
    
    def encode_image(self, image):
        """
        将图像编码为JPEG格式的bytes数据，并添加简单的FEC编码和交织
        :param image: 输入图像，可以是PIL Image对象或numpy数组
        :return: 编码后的bytes数据，包含FEC编码和交织
        """
        try:
            # 如果输入是numpy数组，转换为PIL Image对象
            if isinstance(image, np.ndarray):
                # 确保图像数据类型正确
                if image.dtype == np.float32 or image.dtype == np.float64:
                    image = (image * 255).astype(np.uint8)
                image = Image.fromarray(image)
            
            # 确保图像是RGB格式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 创建字节流缓冲区
            buffer = io.BytesIO()
            
            # 将图像保存为JPEG格式到缓冲区
            image.save(buffer, format='JPEG', quality=self.quality)
            
            # 获取字节数据
            jpeg_data = buffer.getvalue()
            
            # 关闭缓冲区
            buffer.close()
            
            # 1. 添加简单的FEC编码 - 字节级重复编码
            # 对JPEG文件头和关键段使用更强的FEC
            # JPEG文件头（前100字节）使用2倍重复
            # 其余部分使用1倍重复
            if len(jpeg_data) > 100:
                header_part = jpeg_data[:100]
                body_part = jpeg_data[100:]
                # 对文件头使用2倍重复，其余部分使用1倍重复
                fec_data = header_part * 2 + body_part * 1
            else:
                # 整个文件使用2倍重复
                fec_data = jpeg_data * 2
            
            # 2. 实现简单的块交织
            # 将数据分成16字节的块，然后按列交织
            block_size = 16
            # 计算需要的块数
            num_blocks = (len(fec_data) + block_size - 1) // block_size
            # 填充到块大小的整数倍
            padded_data = fec_data + b'\x00' * (num_blocks * block_size - len(fec_data))
            # 创建块矩阵
            blocks = [padded_data[i*block_size:(i+1)*block_size] for i in range(num_blocks)]
            # 按列交织（转置块矩阵）
            interleaved_blocks = []
            for i in range(block_size):
                for block in blocks:
                    if i < len(block):
                        interleaved_blocks.append(block[i:i+1])
            # 合并交织后的数据
            interleaved_data = b''.join(interleaved_blocks)
            
            # 3. 添加简单的帧标记，便于解码器识别
            # 使用更简单可靠的帧标记
            frame_marker = b'JPEG' + struct.pack('>I', len(jpeg_data)) + interleaved_data
            
            return frame_marker
            
        except Exception as e:
            print(f"JPEG编码失败: {e}")
            raise
    
    def _simple_repeat_fec(self, data, repeat=1):
        """
        简单的重复FEC编码 - 将数据重复多次
        :param data: 输入数据
        :param repeat: 重复次数，默认1次
        :return: 重复编码后的数据
        """
        # 简单地重复数据
        return data * (repeat + 1)
    
    def encode_from_file(self, image_path):
        """
        从文件加载图像并编码为JPEG格式
        :param image_path: 图像文件路径
        :return: JPEG格式的bytes数据
        """
        try:
            # 加载图像
            image = Image.open(image_path)
            
            # 编码图像
            return self.encode_image(image)
            
        except Exception as e:
            print(f"从文件编码JPEG失败: {e}")
            raise
    
    def get_compression_ratio(self, original_image, jpeg_data):
        """
        计算压缩比
        :param original_image: 原始图像（PIL Image对象或numpy数组）
        :param jpeg_data: JPEG编码后的bytes数据
        :return: 压缩比（原始大小 / 压缩后大小）
        """
        try:
            # 如果输入是numpy数组
            if isinstance(original_image, np.ndarray):
                # 计算原始大小（假设是RGB图像）
                original_size = original_image.nbytes
            else:
                # 对于PIL Image，转换为numpy数组计算大小
                original_array = np.array(original_image)
                original_size = original_array.nbytes
            
            # 计算压缩后大小
            compressed_size = len(jpeg_data)
            
            # 计算压缩比
            compression_ratio = original_size / compressed_size
            
            return compression_ratio
            
        except Exception as e:
            print(f"计算压缩比失败: {e}")
            return 0.0


# 便捷函数
def jpeg_encode(image, quality=90):
    """
    便捷的JPEG编码函数
    :param image: 输入图像（PIL Image对象或numpy数组）
    :param quality: JPEG压缩质量，0-100
    :return: JPEG格式的bytes数据
    """
    encoder = JPEGEncoder(quality)
    return encoder.encode_image(image)


def jpeg_encode_from_file(image_path, quality=90):
    """
    便捷的从文件编码JPEG函数
    :param image_path: 图像文件路径
    :param quality: JPEG压缩质量，0-100
    :return: JPEG格式的bytes数据
    """
    encoder = JPEGEncoder(quality)
    return encoder.encode_from_file(image_path)


if __name__ == "__main__":
    """
    测试JPEG编码器
    """
    import os
    
    # 获取当前文件的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建项目根目录路径：当前目录 -> image_process -> semantic-communication-workplace
    project_root = os.path.dirname(os.path.dirname(current_dir))
    # 构建测试图像的绝对路径
    test_image_path = os.path.join(project_root, 'data_input', 'image', '1-img-00000-00000_00002.png')
    
    if os.path.exists(test_image_path):
        # 创建编码器
        encoder = JPEGEncoder(quality=90)
        
        # 从文件编码
        jpeg_data = encoder.encode_from_file(test_image_path)
        print(f"从文件编码成功，JPEG数据大小: {len(jpeg_data)} bytes")
        
        # 加载图像并编码
        image = Image.open(test_image_path)
        jpeg_data2 = encoder.encode_image(image)
        print(f"从PIL对象编码成功，JPEG数据大小: {len(jpeg_data2)} bytes")
        
        # 测试numpy数组编码
        image_np = np.array(image)
        jpeg_data3 = encoder.encode_image(image_np)
        print(f"从numpy数组编码成功，JPEG数据大小: {len(jpeg_data3)} bytes")
        
        # 计算压缩比
        compression_ratio = encoder.get_compression_ratio(image, jpeg_data)
        print(f"压缩比: {compression_ratio:.2f}:1")
        
    else:
        print(f"测试图像不存在: {test_image_path}")