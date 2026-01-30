#!/usr/bin/env python3
"""
测试不同SNR下Polar码的解码性能
"""

import os
import sys
import numpy as np
from PIL import Image

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data_input.image_loader import load_images_from_dir
from baseline.baseline_pipeline import BaselinePipeline


def test_snr_performance(snr_range, image_path, output_dir):
    """
    测试不同SNR下的解码性能
    
    Args:
        snr_range: SNR范围列表
        image_path: 测试图像路径
        output_dir: 输出目录
    """
    print(f"\n=== 测试SNR性能范围: {snr_range} ===")
    print(f"测试图像: {os.path.basename(image_path)}")
    
    results = []
    
    for snr in snr_range:
        print(f"\n--- 测试 SNR: {snr} dB ---")
        
        try:
            # 创建baseline流程实例，使用更高的压缩比
            pipeline = BaselinePipeline(
                compression_type='jpeg',           # 使用JPEG编码
                quality=70,                        # 降低质量以提高压缩比，加快速度
                modulation_type='qpsk',            # 使用QPSK调制
                lossless=False,                    # 有损压缩
                snr_dB=snr,                        # 当前SNR
                channel_type='awgn',               # 使用AWGN信道
                use_block_codec=True,             # 使用分块编码
                use_coding=True,                   # 启用信道编码
                coding_scheme='polar',             # 使用极化码编码
                visualize_constellation=False,     # 关闭星座图可视化
                debug=0                            # 关闭调试输出
            )
            
            # 处理图像
            output_path = os.path.join(output_dir, f"recovered_snr{snr}_{os.path.basename(image_path)}")
            recovered_image = pipeline.process_image(image_path, output_path)
            
            # 计算恢复程度
            # 读取原始图像和解码后图像
            original_image = Image.open(image_path)
            recovered_image = Image.open(output_path)
            
            # 确保图像大小相同
            if original_image.size != recovered_image.size:
                print(f"  警告: 恢复图像大小与原始图像不同")
                recovery_ratio = 0
            else:
                # 检查是否是灰色补全图像（所有像素值相近）
                import numpy as np
                recovered_array = np.array(recovered_image)
                
                # 计算像素值的标准差，如果很小说明是灰色补全
                if len(recovered_array.shape) == 3:
                    # 彩色图像，转换为灰度计算
                    gray_array = np.mean(recovered_array, axis=2)
                else:
                    gray_array = recovered_array
                
                std_dev = np.std(gray_array)
                
                if std_dev < 5:
                    # 标准差很小，说明是灰色补全图像
                    print(f"  检测到灰色补全图像，标准差: {std_dev:.2f}")
                    recovery_ratio = 0
                else:
                    # 不是灰色补全，计算实际恢复比例
                    # 将图像转换为灰度进行比较
                    def to_grayscale(img):
                        if img.mode == 'RGB':
                            return img.convert('L')
                        elif img.mode == 'L':
                            return img
                        else:
                            return img.convert('L')
                    
                    original_gray = to_grayscale(original_image)
                    recovered_gray = to_grayscale(recovered_image)
                    
                    original_array = np.array(original_gray)
                    recovered_array = np.array(recovered_gray)
                    
                    # 计算像素差异
                    diff = np.abs(original_array - recovered_array)
                    # 对于完全恢复的图像，差异应该很小
                    threshold = 5
                    matching_pixels = np.sum(diff < threshold)
                    total_pixels = original_array.size
                    recovery_ratio = (matching_pixels / total_pixels) * 100
            
            print(f"  恢复成功!")
            print(f"  原始图像尺寸: {original_image.size}")
            print(f"  恢复图像尺寸: {recovered_image.size}")
            print(f"  恢复比例: {recovery_ratio:.2f}%")
            
            results.append({
                'snr': snr,
                'recovery_ratio': recovery_ratio,
                'status': 'success',
                'original_size': original_image.size,
                'recovered_size': recovered_image.size
            })
            
        except Exception as e:
            print(f"  恢复失败: {e}")
            results.append({
                'snr': snr,
                'recovery_ratio': 0,
                'status': 'failed',
                'error': str(e)
            })
    
    # 输出结果
    print("\n=== 测试结果汇总 ===")
    print(f"{'SNR (dB)':<10} {'状态':<10} {'恢复比例':<15} {'备注':<30}")
    print("-" * 70)
    
    for result in results:
        snr = result['snr']
        status = '成功' if result['status'] == 'success' else '失败'
        recovery_ratio = f"{result.get('recovery_ratio', 0):.2f}%" if result['status'] == 'success' else "N/A"
        note = f"恢复尺寸: {result.get('recovered_size', 'N/A')}" if result['status'] == 'success' else result.get('error', 'N/A')[:30]
        
        print(f"{snr:<10} {status:<10} {recovery_ratio:<15} {note:<30}")
    
    return results


if __name__ == "__main__":
    """
    测试不同SNR下的性能
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 设置测试参数
    image_dir = os.path.join(project_root, 'data_input', 'image')
    output_dir = os.path.join(project_root, 'output', 'snr_test')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取测试图像
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    
    if not image_files:
        print(f"在目录 {image_dir} 中未找到图像文件")
        sys.exit(1)
    
    # 选择一张较小的图像（如果有的话）
    # 这里我们选择第三张图像，假设它可能较小
    image_file = image_files[2] if len(image_files) > 2 else image_files[0]
    image_path = os.path.join(image_dir, image_file)
    
    # 测试SNR范围：3.0到7.0dB，步长0.5dB，以找到临界点
    snr_range = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]
    
    # 运行测试
    results = test_snr_performance(snr_range, image_path, output_dir)
    
    # 保存结果到文本文件
    result_file = os.path.join(output_dir, 'snr_performance_results.txt')
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write("SNR性能测试结果\n")
        f.write("=" * 80 + "\n")
        f.write(f"测试图像: {os.path.basename(image_path)}\n")
        f.write(f"测试时间: {os.popen('date').read().strip()}\n")
        f.write("=" * 80 + "\n")
        f.write(f"{'SNR (dB)':<10} {'状态':<10} {'恢复比例':<15} {'详细信息':<30}\n")
        f.write("-" * 80 + "\n")
        
        for result in results:
            snr = result['snr']
            status = '成功' if result['status'] == 'success' else '失败'
            recovery_ratio = f"{result.get('recovery_ratio', 0):.2f}%" if result['status'] == 'success' else "N/A"
            
            if result['status'] == 'success':
                details = f"恢复尺寸: {result.get('recovered_size', 'N/A')}"
            else:
                details = result.get('error', 'N/A')[:30]
            
            f.write(f"{snr:<10} {status:<10} {recovery_ratio:<15} {details:<30}\n")
    
    print(f"\n=== 测试完成 ===")
    print(f"结果已保存到: {result_file}")
    print(f"恢复的图像已保存到: {output_dir}")
