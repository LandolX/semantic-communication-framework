#!/usr/bin/env python3
"""
测试 CRC 信道解码模块
"""

import pytest
from image_process.channel_coding.crc_channel_codec.crc_encoder import CRCEncoder
from image_recover.channel_coding.crc_channel_codec.crc_decoder import CRCDecoder


class TestCRCDecoder:
    """测试 CRC 信道解码模块"""
    
    def test_decode(self):
        """测试解码功能"""
        # 初始化 CRC 编码器和解码器
        encoder = CRCEncoder(crc_polynomial='crc16')
        decoder = CRCDecoder()
        
        # 测试数据
        test_data = b'Hello, CRC Channel Coding!'
        
        # 编码
        encoded_data = encoder.encode(test_data)
        
        # 解码
        decoded_data, status = decoder.decode(encoded_data)
        assert isinstance(decoded_data, bytes), "解码后应该返回bytes"
        assert status is True, "解码状态应该为True"
    
    def test_decode_with_corrupted_data(self):
        """测试解码损坏的数据"""
        # 初始化 CRC 编码器和解码器
        encoder = CRCEncoder(crc_polynomial='crc16')
        decoder = CRCDecoder()
        
        # 测试数据
        test_data = b'Hello, CRC Channel Coding!'
        
        # 编码
        encoded_data = encoder.encode(test_data)
        
        # 模拟数据损坏（修改前几个字节）
        corrupted_data = b'XXXX' + encoded_data[4:]
        
        # 解码
        decoded_data, status = decoder.decode(corrupted_data)
        assert isinstance(decoded_data, bytes), "解码后应该返回bytes"


if __name__ == "__main__":
    pytest.main([__file__])
