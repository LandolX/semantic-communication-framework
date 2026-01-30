#!/usr/bin/env python3
"""
测试 image_loader 模块
"""

import os
import pytest
from data_input.image_loader import load_images_from_dir


class TestImageLoader:
    """测试图像加载器"""
    
    def test_load_images_from_dir(self):
        """测试从目录加载图像"""
        # 获取测试图像目录路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_input_root = os.path.dirname(current_dir)
        image_dir = os.path.join(data_input_root, 'image')
        
        # 验证图像目录存在
        assert os.path.exists(image_dir), f"测试图像目录不存在: {image_dir}"
        
        # 加载图像（返回的是生成器）
        images_generator = load_images_from_dir(image_dir)
        
        # 验证返回值是生成器
        assert hasattr(images_generator, '__next__'), "load_images_from_dir 应该返回生成器"
        
        # 转换生成器为列表并验证
        import numpy as np
        images = list(images_generator)
        assert len(images) > 0, "加载的图像列表为空"
        
        # 验证列表中的元素是 numpy 数组
        for img in images:
            assert isinstance(img, np.ndarray), "图像应该是 numpy 数组"
            assert img.ndim == 3, "图像应该是 3 维数组 (H, W, C)"
            assert img.shape[0] > 0, "图像高度应该大于 0"
            assert img.shape[1] > 0, "图像宽度应该大于 0"


if __name__ == "__main__":
    pytest.main([__file__])
