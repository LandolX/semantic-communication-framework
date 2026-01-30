#!/usr/bin/env python3
"""
测试 CRC 信道编码模块
"""

import pytest
from image_process.channel_coding.crc_channel_codec.crc_encoder import CRCEncoder


class TestCRCEncoder:
    """测试 CRC 信道编码模块"""
    
    def test_encode_decode(self):
        """测试编码功能"""
        # 初始化 CRC 编码器
        encoder = CRCEncoder(crc_polynomial='crc16')
        
        # 测试数据
        test_data = b'Hello, CRC Channel Coding!'
        
        # 编码
        encoded_data = encoder.encode(test_data)
        assert isinstance(encoded_data, bytes), "编码后应该返回bytes"
        assert len(encoded_data) > len(test_data), "编码后数据长度应该大于原始数据"
    
    def test_encode_with_crc8(self):
        """测试使用 CRC8 的编码"""
        # 初始化 CRC 编码器（使用 CRC8）
        encoder = CRCEncoder(crc_polynomial='crc8')
        
        # 测试数据
        test_data = b'Hello, CRC8!'
        
        # 编码
        encoded_data = encoder.encode(test_data)
        assert isinstance(encoded_data, bytes), "编码后应该返回bytes"
        assert len(encoded_data) > len(test_data), "编码后数据长度应该大于原始数据"
    
    def test_encode_with_crc32(self):
        """测试使用 CRC32 的编码"""
        # 初始化 CRC 编码器（使用 CRC32）
        encoder = CRCEncoder(crc_polynomial='crc32')
        
        # 测试数据
        test_data = b'Hello, CRC32!'
        
        # 编码
        encoded_data = encoder.encode(test_data)
        assert isinstance(encoded_data, bytes), "编码后应该返回bytes"
        assert len(encoded_data) > len(test_data), "编码后数据长度应该大于原始数据"
    
    def test_get_crc_info(self):
        """测试获取 CRC 信息"""
        # 初始化 CRC 编码器
        encoder = CRCEncoder(crc_polynomial='crc16')
        
        # 获取 CRC 信息
        crc_info = encoder.get_crc_info()
        assert isinstance(crc_info, dict), "get_crc_info 应该返回字典"
        assert 'crc_polynomial' in crc_info, "CRC 信息应该包含 crc_polynomial 字段"
        assert crc_info['crc_polynomial'] == 'crc16', "CRC 多项式应该是 crc16"


if __name__ == "__main__":
    pytest.main([__file__])
