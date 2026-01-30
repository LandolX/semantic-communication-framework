#!/usr/bin/env python3
"""
比较不同Polar码评估方法的结果差异
"""

import os
import numpy as np
import matplotlib.pyplot as plt

def compare_evaluations(github_result_file, current_result_file, output_dir):
    """
    比较GitHub库评估和当前评估的Polar码性能差异
    
    Args:
        github_result_file: GitHub库评估结果文件
        current_result_file: 当前评估结果文件
        output_dir: 输出目录
    """
    # 读取GitHub库评估结果
    github_data = {
        '512_256': [],  # P(512,256)
        '1024_512': []   # P(1024,512)
    }
    
    with open(github_result_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[1:]:  # 从第2行开始读取数据
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 3:
                snr = float(parts[0])
                ber_512_256 = float(parts[1])
                ber_1024_512 = float(parts[2])
                github_data['512_256'].append((snr, ber_512_256))
                github_data['1024_512'].append((snr, ber_1024_512))
    
    # 读取当前评估结果
    current_data = {}
    with open(current_result_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[7:]:  # 从第8行开始读取数据
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 5:
                coding_scheme = parts[0]
                snr = float(parts[1])
                ber = float(parts[4])
                if coding_scheme == 'POLAR':
                    if 'POLAR' not in current_data:
                        current_data['POLAR'] = []
                    current_data['POLAR'].append((snr, ber))
    
    # 按SNR排序数据
    for key in github_data:
        github_data[key].sort(key=lambda x: x[0])
    if 'POLAR' in current_data:
        current_data['POLAR'].sort(key=lambda x: x[0])
    
    # 创建对比图表
    plt.figure(figsize=(14, 10))
    
    # 绘制GitHub库评估结果
    for code, data in github_data.items():
        snr_values = [item[0] for item in data]
        ber_values = [item[1] for item in data]
        plt.semilogy(snr_values, ber_values, 
                    marker='o',
                    linestyle='-',
                    linewidth=2,
                    markersize=8,
                    label=f'GitHub {code}')
    
    # 绘制当前评估结果
    if 'POLAR' in current_data:
        snr_values = [item[0] for item in current_data['POLAR']]
        ber_values = [item[1] for item in current_data['POLAR']]
        plt.semilogy(snr_values, ber_values, 
                    marker='s',
                    linestyle='--',
                    linewidth=2,
                    markersize=8,
                    color='r',
                    label='Current Evaluation (POLAR)')
    
    # 设置图表标题和标签
    plt.title('Comparison of Polar Code Performance Evaluations', fontsize=16)
    plt.xlabel('SNR (dB)', fontsize=12)
    plt.ylabel('Bit Error Rate (BER)', fontsize=12)
    
    # 设置坐标轴范围
    plt.xlim(0, 12)
    plt.ylim(1e-6, 0.6)
    
    # 添加网格
    plt.grid(True, which='both', linestyle='--', alpha=0.7)
    
    # 添加图例
    plt.legend(loc='upper right', fontsize=10)
    
    # 保存图表
    output_path = os.path.join(output_dir, 'polar_evaluation_comparison.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    
    print(f"Comparison chart saved to: {output_path}")
    
    # 显示图表
    plt.show()

if __name__ == "__main__":
    # 设置路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    github_result_file = os.path.join(project_root, 'advanced_polar_coding', 'polar_code_evaluation_results_github.txt')
    current_result_file = os.path.join(project_root, 'evaluation', 'coding_schemes_evaluation.txt')
    output_dir = os.path.join(project_root, 'output', 'snr_test')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    if os.path.exists(github_result_file) and os.path.exists(current_result_file):
        compare_evaluations(github_result_file, current_result_file, output_dir)
    else:
        print("Required result files not found for comparison")
