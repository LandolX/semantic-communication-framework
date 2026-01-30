import pytest
import numpy as np
from image_process.compression_coding.jpeg2000.jpeg2000_encoder import JPEG2000Encoder

class TestJPEG2000Encoder:
    def setup_method(self):
        self.encoder = JPEG2000Encoder()
    
    def test_encode_image(self):
        test_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        encoded_data = self.encoder.encode_image(test_image)
        assert encoded_data is not None
        assert isinstance(encoded_data, bytes)
    
    def test_encode_from_file(self):
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
        test_image_path = os.path.join(project_root, 'data_input', 'image', '1-img-00000-00002_00002.png')
        
        if os.path.exists(test_image_path):
            encoded_data = self.encoder.encode_from_file(test_image_path)
            assert encoded_data is not None
            assert isinstance(encoded_data, bytes)
    
    def test_get_compression_ratio(self):
        test_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        encoded_data = self.encoder.encode_image(test_image)
        ratio = self.encoder.get_compression_ratio(test_image, encoded_data)
        assert ratio > 0
