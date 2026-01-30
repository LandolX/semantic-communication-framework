#!/usr/bin/env python3
"""
测试 JPEG 解码模块
"""

import pytest
from PIL import Image
from image_process.compression_coding.jpeg.jpeg_encoder import JPEGEncoder
from image_recover.compression_coding.jpeg.jpeg_decoder import JPEGDecoder


class TestJPEGDecoder:
    """测试 JPEG 解码模块"""
    
    def test_decode_image(self):
        """测试解码图像功能"""
        # 创建测试图像
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        
        # 初始化 JPEG 编码器和解码器
        encoder = JPEGEncoder(quality=90, use_block_codec=False)
        decoder = JPEGDecoder(use_block_codec=False)
        
        # 编码图像
        encoded_data = encoder.encode_image(img, lossless=False)
        
        # 解码图像
        decoded_image, recovery_ratio = decoder.decode_image(encoded_data, return_type='pil')
        assert decoded_image is not None, "解码后应该返回图像"
        assert recovery_ratio > 0, "恢复比例应该大于0"
    
    def test_decode_image_with_block_codec(self):
        """测试解码使用分块编码的图像"""
        # 创建测试图像
        img = Image.new('RGB', (100, 100), color=(0, 255, 0))
        
        # 初始化 JPEG 编码器和解码器（使用分块编码）
        encoder = JPEGEncoder(quality=90, use_block_codec=True)
        decoder = JPEGDecoder(use_block_codec=True)
        
        # 编码图像
        encoded_data = encoder.encode_image(img, lossless=False)
        
        # 解码图像
        decoded_image, recovery_ratio = decoder.decode_image(encoded_data, return_type='pil')
        assert decoded_image is not None, "解码后应该返回图像"
        assert recovery_ratio > 0, "恢复比例应该大于0"
    
    def test_verify_image_data(self):
        """测试验证图像数据功能"""
        # 创建测试图像
        img = Image.new('RGB', (100, 100), color=(0, 0, 255))
        
        # 初始化 JPEG 编码器和解码器
        encoder = JPEGEncoder(quality=90)
        decoder = JPEGDecoder()
        
        # 编码图像
        encoded_data = encoder.encode_image(img, lossless=False)
        
        # 验证图像数据
        is_valid = decoder.verify_image_data(encoded_data)
        assert isinstance(is_valid, bool), "验证结果应该返回布尔值"


if __name__ == "__main__":
    pytest.main([__file__])
