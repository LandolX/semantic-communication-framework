import pytest
import numpy as np
from image_process.channel_coding.ldpc_channel_codec.ldpc_channel_encoder import LDPCChannelEncoder

class TestLDPCEncoder:
    def setup_method(self):
        self.encoder = LDPCChannelEncoder()
    
    def test_encode(self):
        test_data = np.random.randint(0, 2, 100, dtype=np.uint8)
        encoded_data = self.encoder.encode(test_data)
        assert encoded_data is not None
        assert isinstance(encoded_data, (bytes, np.ndarray))
    
    def test_encode_with_different_data_lengths(self):
        # 测试不同长度的数据
        for length in [50, 100, 150]:
            test_data = np.random.randint(0, 2, length, dtype=np.uint8)
            encoded_data = self.encoder.encode(test_data)
            assert encoded_data is not None
