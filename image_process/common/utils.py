#!/usr/bin/env python3
"""
通用工具模块
包含所有编码器和解码器共有的功能
"""

import struct
import numpy as np
from PIL import Image
import io


def simple_repeat_encode(data, repeat):
    """
    简单的重复编码（逐字节重复）
    :param data: 原始数据
    :param repeat: 重复次数
    :return: 编码后的数据
    """
    if repeat <= 1:
        return data
    result = b''
    for byte in data:
        result += bytes([byte]) * repeat
    return result


def simple_repeat_decode(data, repeat):
    """
    简单的重复解码（多数投票）
    兼容旧版本的解码逻辑
    :param data: 编码数据
    :param repeat: 重复次数
    :return: 解码后的数据
    """
    if repeat <= 1:
        return data
    
    decoded = b''
    total_len = len(data)
    for i in range(0, total_len, repeat):
        if i + repeat <= total_len:
            block = data[i:i+repeat]
            byte = max(set(block), key=block.count)
            decoded += bytes([byte])
        else:
            remaining = total_len - i
            if remaining > 0:
                decoded += data[i:i+remaining]
    return decoded


class CRCUtils:
    """
    CRC工具类
    提供CRC计算和验证功能
    """
    
    # 预定义CRC多项式
    CRC_POLYNOMIALS = {
        'crc8': 0x1D,      # x^8 + x^4 + x^3 + x^2 + 1
        'crc16': 0x8005,    # x^16 + x^15 + x^2 + 1 (CRC-16-IBM)
        'crc32': 0x04C11DB7  # x^32 + x^26 + x^23 + x^22 + x^16 + x^12 + x^11 + x^10 + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1
    }
    
    # CRC位数映射
    CRC_BITS_MAP = {'crc8': 8, 'crc16': 16, 'crc32': 32}
    
    @classmethod
    def get_crc_polynomial(cls, crc_type):
        """
        获取CRC多项式
        :param crc_type: CRC类型
        :return: CRC多项式
        """
        return cls.CRC_POLYNOMIALS.get(crc_type, 0x8005)
    
    @classmethod
    def get_crc_bits(cls, crc_type):
        """
        获取CRC位数
        :param crc_type: CRC类型
        :return: CRC位数
        """
        return cls.CRC_BITS_MAP.get(crc_type, 16)
    
    @classmethod
    def calculate_crc(cls, data, crc_type='crc16'):
        """
        计算CRC值
        :param data: 原始数据
        :param crc_type: CRC类型
        :return: CRC值
        """
        polynomial = cls.get_crc_polynomial(crc_type)
        crc_bits = cls.get_crc_bits(crc_type)
        
        crc = 0
        for byte in data:
            crc ^= byte << (crc_bits - 8)
            for _ in range(8):
                if crc & (1 << (crc_bits - 1)):
                    crc = (crc << 1) ^ polynomial
                else:
                    crc <<= 1
                crc &= (1 << crc_bits) - 1
        return crc


class ImageUtils:
    """
    图像工具类
    提供图像预处理和格式转换功能
    """
    
    @staticmethod
    def convert_to_rgb(image):
        """
        将图像转换为RGB模式
        :param image: 输入图像
        :return: RGB模式的图像
        """
        if isinstance(image, np.ndarray):
            if image.dtype == np.float32 or image.dtype == np.float64:
                image = (image * 255).astype(np.uint8)
            image = Image.fromarray(image)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    @staticmethod
    def save_image_to_buffer(image, format_type, quality=90):
        """
        将图像保存到缓冲区
        :param image: 输入图像
        :param format_type: 格式类型
        :param quality: 质量参数
        :return: 编码后的数据
        """
        buffer = io.BytesIO()
        
        try:
            if format_type == 'jpeg':
                image.save(buffer, format='JPEG', quality=quality)
            elif format_type in ['jpeg2000', 'jpeg2000bgr']:
                image.save(buffer, format='JPEG2000', quality_mode='rates', quality_layers=[quality/100])
            elif format_type == 'png':
                # PNG格式支持无损压缩
                image.save(buffer, format='PNG')
        except Exception as e:
            print(f"{format_type.upper()}保存失败，回退到JPEG格式: {e}")
            image.save(buffer, format='JPEG', quality=quality)
        
        data = buffer.getvalue()
        buffer.close()
        return data


class FrameUtils:
    """
    帧处理工具类
    提供帧头和数据组装功能
    """
    
    @staticmethod
    def create_frame_marker(codec_type, original_size):
        """
        创建帧标记
        :param codec_type: 编解码器类型
        :param original_size: 原始数据大小
        :return: 帧标记
        """
        if codec_type == 'jpeg':
            return b'JPEG' + struct.pack('>I', original_size)
        elif codec_type == 'jpeg2000':
            return b'JP2K' + struct.pack('>I', original_size)
        elif codec_type == 'jpeg2000bgr':
            return b'JP2B' + struct.pack('>I', original_size)
        elif codec_type == 'h264':
            return b'H264' + struct.pack('>I', original_size)
        else:
            return b'UNKN' + struct.pack('>I', original_size)
    
    @staticmethod
    def parse_frame_marker(data):
        """
        解析帧标记
        :param data: 带帧标记的数据
        :return: (编解码器类型, 原始大小, 数据部分)
        """
        if data.startswith(b'JPEG'):
            return 'jpeg', struct.unpack('>I', data[4:8])[0], data[8:]
        elif data.startswith(b'JP2K'):
            return 'jpeg2000', struct.unpack('>I', data[4:8])[0], data[8:]
        elif data.startswith(b'JP2B'):
            return 'jpeg2000bgr', struct.unpack('>I', data[4:8])[0], data[8:]
        elif data.startswith(b'H264'):
            return 'h264', struct.unpack('>I', data[4:8])[0], data[8:]
        elif data.startswith(b'BLKH'):
            return 'block_' + data[4:8].decode('utf-8', errors='ignore'), struct.unpack('>I', data[8:12])[0], data[12:]
        else:
            return 'unknown', 0, data


def calculate_recovery_ratio(image, expected_size):
    """
    计算图像恢复比例
    :param image: 恢复的图像
    :param expected_size: 期望的图像尺寸
    :return: 恢复比例
    """
    if image.size != expected_size:
        valid_pixels = image.size[0] * image.size[1]
        total_pixels = expected_size[0] * expected_size[1]
        return valid_pixels / total_pixels
    
    image_np = np.array(image)
    avg_brightness = np.mean(image_np)
    
    if avg_brightness > 50:
        return 1.0
    
    black_low = np.array([0, 0, 0])
    black_high = np.array([10, 10, 10])
    black_mask = np.all((image_np >= black_low) & (image_np <= black_high), axis=2)
    non_black_pixels = np.sum(~black_mask)
    total_pixels = image_np.shape[0] * image_np.shape[1]
    
    return non_black_pixels / total_pixels


def fix_image(image, expected_size):
    """
    修复图像尺寸
    :param image: 恢复的图像
    :param expected_size: 期望的图像尺寸
    :return: 修复后的图像
    """
    if image.size != expected_size:
        fixed_image = Image.new('RGB', expected_size, (128, 128, 128))
        paste_x = (expected_size[0] - image.size[0]) // 2
        paste_y = (expected_size[1] - image.size[1]) // 2
        fixed_image.paste(image, (paste_x, paste_y))
        return fixed_image
    
    image_np = np.array(image)
    avg_brightness = np.mean(image_np)
    
    if avg_brightness < 10:
        black_low = np.array([0, 0, 0])
        black_high = np.array([10, 10, 10])
        black_mask = np.all((image_np >= black_low) & (image_np <= black_high), axis=2)
        if np.any(black_mask):
            image_np[black_mask] = [128, 128, 128]
            return Image.fromarray(image_np)
    
    return image
