import pytest
import numpy as np
from image_recover.channel_coding.ldpc_channel_codec.ldpc_channel_decoder import LDPCChannelDecoder

class TestLDPCDecoder:
    def setup_method(self):
        self.decoder = LDPCChannelDecoder()
    
    def test_decode(self):
        test_data = np.random.randint(0, 2, 200, dtype=np.uint8)
        decoded_data = self.decoder.decode(test_data)
        assert decoded_data is not None
        # LDPC解码器返回的是元组 (decoded_bits, success)
        assert isinstance(decoded_data, tuple)
        assert len(decoded_data) == 2
        assert isinstance(decoded_data[0], np.ndarray)
        assert isinstance(decoded_data[1], bool)
    
    def test_decode_with_different_data_lengths(self):
        # 测试不同长度的数据
        for length in [150, 200, 250]:
            test_data = np.random.randint(0, 2, length, dtype=np.uint8)
            decoded_data = self.decoder.decode(test_data)
            assert decoded_data is not None
            assert isinstance(decoded_data, tuple)
