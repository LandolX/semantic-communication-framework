#!/usr/bin/env python3
"""
测试分块编码模块
"""

import pytest
from image_process.block_coding.block_codec.block_codec import BlockCodec


class TestBlockCodec:
    """测试分块编码模块"""
    
    def test_encode_decode(self):
        """测试编码和解码功能"""
        # 初始化分块编码器
        codec = BlockCodec(block_size=1024, fec_strategy='repetition', fec_level=2)
        
        # 测试数据
        test_data = b'Hello, Block Codec! This is a test message for block encoding and decoding.'
        
        # 编码
        encoded_data = codec.encode(test_data, 'jpeg')
        assert isinstance(encoded_data, bytes), "编码后应该返回bytes"
        assert len(encoded_data) > len(test_data), "编码后数据长度应该大于原始数据"
        
        # 解码
        decoded_data = codec.decode(encoded_data, 'jpeg')
        assert isinstance(decoded_data, bytes), "解码后应该返回bytes"
        assert decoded_data == test_data, "解码后数据应该与原始数据相同"
    
    def test_encode_decode_with_xor(self):
        """测试使用XOR策略的编码和解码"""
        # 初始化分块编码器（使用XOR策略）
        codec = BlockCodec(block_size=1024, fec_strategy='xor', fec_level=2)
        
        # 测试数据
        test_data = b'Hello, Block Codec with XOR!'
        
        # 编码
        encoded_data = codec.encode(test_data, 'jpeg')
        assert isinstance(encoded_data, bytes), "编码后应该返回bytes"
        assert len(encoded_data) > len(test_data), "编码后数据长度应该大于原始数据"
        
        # 解码
        decoded_data = codec.decode(encoded_data, 'jpeg')
        assert isinstance(decoded_data, bytes), "解码后应该返回bytes"
        assert decoded_data == test_data, "解码后数据应该与原始数据相同"
    
    def test_decode_with_corrupted_data(self):
        """测试解码损坏的数据"""
        # 初始化分块编码器
        codec = BlockCodec(block_size=1024, fec_strategy='repetition', fec_level=2)
        
        # 测试数据
        test_data = b'Hello, Block Codec!'
        
        # 编码
        encoded_data = codec.encode(test_data, 'jpeg')
        
        # 模拟数据损坏（修改前几个字节）
        corrupted_data = b'XXXX' + encoded_data[4:]
        
        # 解码（可能返回None，表示无法完全恢复）
        decoded_data = codec.decode(corrupted_data, 'jpeg')
        # 解码可能返回None，这是正常的，因为数据被严重损坏
        assert decoded_data is None or isinstance(decoded_data, bytes), "解码后应该返回bytes或None"


if __name__ == "__main__":
    pytest.main([__file__])
