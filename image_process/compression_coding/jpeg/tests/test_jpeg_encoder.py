#!/usr/bin/env python3
"""
测试 JPEG 编码模块
"""

import pytest
from PIL import Image
from image_process.compression_coding.jpeg.jpeg_encoder import JPEGEncoder


class TestJPEGEncoder:
    """测试 JPEG 编码模块"""
    
    def test_encode_image(self):
        """测试编码图像功能"""
        # 创建测试图像
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        
        # 初始化 JPEG 编码器
        encoder = JPEGEncoder(quality=90, use_block_codec=False)
        
        # 编码图像（有损）
        encoded_data = encoder.encode_image(img, lossless=False)
        assert isinstance(encoded_data, bytes), "编码后应该返回bytes"
        assert len(encoded_data) > 0, "编码后数据长度应该大于0"
    
    def test_encode_image_lossless(self):
        """测试无损编码图像功能"""
        # 创建测试图像
        img = Image.new('RGB', (100, 100), color=(0, 255, 0))
        
        # 初始化 JPEG 编码器
        encoder = JPEGEncoder(quality=100, use_block_codec=False)
        
        # 编码图像（无损）
        encoded_data = encoder.encode_image(img, lossless=True)
        assert isinstance(encoded_data, bytes), "编码后应该返回bytes"
        assert len(encoded_data) > 0, "编码后数据长度应该大于0"
    
    def test_encode_image_with_block_codec(self):
        """测试使用分块编码的图像编码"""
        # 创建测试图像
        img = Image.new('RGB', (100, 100), color=(0, 0, 255))
        
        # 初始化 JPEG 编码器（使用分块编码）
        encoder = JPEGEncoder(quality=90, use_block_codec=True)
        
        # 编码图像
        encoded_data = encoder.encode_image(img, lossless=False)
        assert isinstance(encoded_data, bytes), "编码后应该返回bytes"
        assert len(encoded_data) > 0, "编码后数据长度应该大于0"
    
    def test_get_compression_ratio(self):
        """测试计算压缩比功能"""
        # 创建测试图像
        img = Image.new('RGB', (100, 100), color=(255, 255, 0))
        
        # 初始化 JPEG 编码器
        encoder = JPEGEncoder(quality=90)
        
        # 编码图像
        encoded_data = encoder.encode_image(img, lossless=False)
        
        # 计算压缩比
        compression_ratio = encoder.get_compression_ratio(img, encoded_data)
        assert isinstance(compression_ratio, float), "压缩比应该返回float"
        assert compression_ratio > 1.0, "压缩比应该大于1"


if __name__ == "__main__":
    pytest.main([__file__])
