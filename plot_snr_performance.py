#!/usr/bin/env python3
"""
绘制SNR性能测试结果的直线图
"""

import os
import matplotlib.pyplot as plt

def plot_snr_performance(result_file, output_dir):
    """
    绘制SNR性能测试结果的直线图
    
    Args:
        result_file: 测试结果文件路径
        output_dir: 输出目录
    """
    # 读取测试结果
    snr_values = []
    recovery_ratios = []
    
    with open(result_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        # 跳过表头
        for line in lines[7:]:  # 从第8行开始读取数据
            line = line.strip()
            if not line:
                continue
            
            # 解析行数据
            parts = line.split()
            if len(parts) >= 3:
                snr = float(parts[0])
                recovery_ratio = float(parts[2].replace('%', ''))
                snr_values.append(snr)
                recovery_ratios.append(recovery_ratio)
    
    if not snr_values:
        print("No test data found")
        return
    
    # 创建直线图
    plt.figure(figsize=(10, 6))
    
    # 绘制直线
    plt.plot(snr_values, recovery_ratios, 'o-', linewidth=2, markersize=8, color='b')
    
    # 添加数据点标签
    for i, (snr, ratio) in enumerate(zip(snr_values, recovery_ratios)):
        plt.text(snr, ratio + 1, f'{ratio:.2f}%', ha='center', va='bottom')
    
    # 设置图表标题和标签（使用英文）
    plt.title('Polar Code Performance at Different SNR Levels', fontsize=16)
    plt.xlabel('SNR (dB)', fontsize=12)
    plt.ylabel('Recovery Ratio (%)', fontsize=12)
    
    # 设置坐标轴范围
    plt.xlim(min(snr_values) - 0.5, max(snr_values) + 0.5)
    plt.ylim(-5, 105)
    
    # 添加网格
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 添加水平参考线
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Complete Failure (0%)')
    plt.axhline(y=100, color='g', linestyle='--', alpha=0.5, label='Complete Success (100%)')
    
    # 添加图例
    plt.legend()
    
    # 保存图表
    output_path = os.path.join(output_dir, 'snr_performance_plot.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    
    print(f"Chart saved to: {output_path}")
    
    # 显示图表
    plt.show()

if __name__ == "__main__":
    # 设置路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    result_file = os.path.join(project_root, 'output', 'snr_test', 'snr_performance_results.txt')
    output_dir = os.path.join(project_root, 'output', 'snr_test')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 绘制图表
    plot_snr_performance(result_file, output_dir)
