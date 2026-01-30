#!/usr/bin/env python3
"""
测试通用工具模块
"""

import pytest
from PIL import Image
import numpy as np
from image_process.common.utils import ImageUtils, simple_repeat_encode, simple_repeat_decode


class TestUtils:
    """测试通用工具模块"""
    
    def test_image_utils_convert_to_rgb(self):
        """测试图像转换为RGB模式"""
        # 创建测试图像
        img_gray = Image.new('L', (100, 100), color=128)
        
        # 转换为RGB
        img_rgb = ImageUtils.convert_to_rgb(img_gray)
        
        # 验证转换结果
        assert img_rgb.mode == 'RGB', "图像应该转换为RGB模式"
        assert img_rgb.size == (100, 100), "图像尺寸应该保持不变"
    
    def test_image_utils_save_image_to_buffer(self):
        """测试将图像保存到缓冲区"""
        # 创建测试图像
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        
        # 保存为JPEG
        jpeg_data = ImageUtils.save_image_to_buffer(img, 'jpeg', quality=90)
        assert isinstance(jpeg_data, bytes), "保存为JPEG应该返回bytes"
        assert len(jpeg_data) > 0, "JPEG数据长度应该大于0"
        
        # 保存为PNG
        png_data = ImageUtils.save_image_to_buffer(img, 'png')
        assert isinstance(png_data, bytes), "保存为PNG应该返回bytes"
        assert len(png_data) > 0, "PNG数据长度应该大于0"
    
    def test_simple_repeat_encode(self):
        """测试简单重复编码"""
        test_data = b'Hello, World!'
        encoded_data = simple_repeat_encode(test_data, 2)
        
        assert isinstance(encoded_data, bytes), "编码后应该返回bytes"
        assert len(encoded_data) == len(test_data) * 2, "编码后数据长度应该是原始数据的2倍"
    
    def test_simple_repeat_decode(self):
        """测试简单重复解码"""
        test_data = b'Hello, World!'
        encoded_data = simple_repeat_encode(test_data, 2)
        decoded_data = simple_repeat_decode(encoded_data, 2)
        
        assert isinstance(decoded_data, bytes), "解码后应该返回bytes"
        assert decoded_data == test_data, "解码后数据应该与原始数据相同"


if __name__ == "__main__":
    pytest.main([__file__])
