import pytest
import numpy as np
from image_recover.compression_coding.h264.h264_decoder import H264Decoder

class TestH264Decoder:
    def setup_method(self):
        self.decoder = H264Decoder()
    
    def test_decode_image(self):
        test_data = b'test_h264_data'
        decoded_result = self.decoder.decode_image(test_data)
        assert decoded_result is not None
        # H264解码器返回的是元组 (PIL Image, float)
        assert isinstance(decoded_result, tuple)
        assert len(decoded_result) == 2
    
    def test_decode_with_different_data(self):
        # 测试不同长度的数据
        test_data1 = b'short'
        test_data2 = b'longer test data for h264 decoder'
        
        decoded_result1 = self.decoder.decode_image(test_data1)
        decoded_result2 = self.decoder.decode_image(test_data2)
        
        assert decoded_result1 is not None
        assert decoded_result2 is not None
        assert isinstance(decoded_result1, tuple)
        assert isinstance(decoded_result2, tuple)
