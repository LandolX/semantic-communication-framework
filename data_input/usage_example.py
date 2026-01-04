#!/usr/bin/env python3
"""
图像加载器使用示例
"""

from image_loader import load_images_from_dir, get_image_loader
import os


def main():
    """
    主函数，演示图像加载器的使用
    """
    # 获取当前目录
    current_dir = os.path.dirname(__file__)
    # 图像文件夹路径
    image_dir = os.path.join(current_dir, 'image')
    
    print("\n=== 示例1: 使用便捷函数加载原始图像 ===")
    # 使用便捷函数加载原始图像
    images = load_images_from_dir(image_dir)
    
    # 循环处理前5张图像
    print(f"从 {image_dir} 加载原始图像：")
    count = 0
    for img in images:
        count += 1
        print(f"  图像 {count}: 形状 = {img.shape}, 数据类型 = {img.dtype}")
        if count >= 5:
            break
    
    print("\n=== 示例2: 使用 ImageLoader 类 ===")
    # 获取 ImageLoader 实例
    loader = get_image_loader(image_dir)
    
    # 显示图像信息
    loader.show_image_info()
    
    # 处理所有图像（这里只处理前3张）
    print("\n处理图像：")
    count = 0
    for img in loader.load_images():
        count += 1
        print(f"  处理第 {count} 张图像，形状: {img.shape}")
        # 这里可以添加你的图像处理逻辑
        # 例如：将图像传递给外部预处理模块
        if count >= 3:
            break
    
    print(f"\n=== 完成 ===")
    print(f"总共处理了 {count} 张图像")


if __name__ == "__main__":
    main()