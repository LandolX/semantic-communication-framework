#!/usr/bin/env python3
"""
测试脚本：验证数据输入模块和预处理模块的配合使用
"""

import sys
import os

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（当前目录的父目录）
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到系统路径
sys.path.insert(0, project_root)

# 导入数据输入模块
from data_input.image_loader import load_images_from_dir

# 导入预处理模块（同一目录，相对导入）
from image_preprocessor import preprocess_image


def test_data_input_with_preprocessing():
    """
    测试数据输入与预处理模块的配合使用
    """
    print("\n=== 测试数据输入与预处理模块的配合使用 ===")
    
    # 图像目录路径（相对路径）
    image_dir = os.path.join(project_root, 'data_input', 'image')
    
    try:
        # 1. 使用数据输入模块加载原始图像
        print(f"从 {image_dir} 加载原始图像...")
        original_images = load_images_from_dir(image_dir)
        
        # 2. 对每张图像进行预处理
        print("\n对原始图像进行预处理...")
        processed_count = 0
        
        for i, img in enumerate(original_images):
            try:
                # 转换为PIL Image对象
                from PIL import Image
                pil_img = Image.fromarray(img)
                
                # 进行预处理
                preprocessed_img = preprocess_image(pil_img)
                
                print(f"图像 {i+1}:")
                print(f"  原始形状: {img.shape}")
                print(f"  预处理后形状: {preprocessed_img.shape}")
                print(f"  预处理后数据类型: {preprocessed_img.dtype}")
                print(f"  预处理后像素值范围: [{preprocessed_img.min():.4f}, {preprocessed_img.max():.4f}]")
                
                processed_count += 1
                
                # 只处理前5张图像
                if processed_count >= 5:
                    break
                    
            except Exception as e:
                print(f"  处理图像 {i+1} 时出错: {e}")
                continue
        
        print(f"\n成功处理了 {processed_count} 张图像")
        print("=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        return False
    
    return True


if __name__ == "__main__":
    test_data_input_with_preprocessing()