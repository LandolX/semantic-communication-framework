#!/usr/bin/env python3
"""
测试极化码信道解码模块
"""

import pytest
import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.abspath('../'))

# 添加image_process目录到Python路径
sys.path.insert(0, os.path.abspath('../../../../image_process'))

from channel_coding.polar_channel_codec.polar_encoder import PolarEncoder
from polar_decoder import PolarDecoder


class TestPolarDecoder:
    """测试极化码信道解码模块"""
    
    def test_decode(self):
        """测试解码功能"""
        # 初始化极化码编码器和解码器
        encoder = PolarEncoder(code_rate=0.5)
        decoder = PolarDecoder()
        
        # 测试数据
        test_data = b'Hello, Polar Channel Coding!'
        
        # 编码
        encoded_data = encoder.encode(test_data)
        
        # 解码
        decoded_data, status = decoder.decode(encoded_data)
        assert isinstance(decoded_data, bytes), "解码后应该返回bytes"
        assert status is True, "解码状态应该为True"
    
    def test_decode_with_corrupted_data(self):
        """测试解码损坏的数据"""
        # 初始化极化码编码器和解码器
        encoder = PolarEncoder(code_rate=0.5)
        decoder = PolarDecoder()
        
        # 测试数据
        test_data = b'Hello, Polar Channel Coding!'
        
        # 编码
        encoded_data = encoder.encode(test_data)
        
        # 模拟数据损坏（修改前几个字节）
        corrupted_data = b'XXXX' + encoded_data[4:]
        
        # 解码
        decoded_data, status = decoder.decode(corrupted_data)
        assert isinstance(decoded_data, bytes), "解码后应该返回bytes"


if __name__ == "__main__":
    pytest.main([__file__])
