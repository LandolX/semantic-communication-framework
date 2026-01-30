#!/usr/bin/env python3
"""
可视化Polar码性能测试结果
"""

import os
import matplotlib.pyplot as plt

def plot_polar_performance(result_file, output_dir):
    """
    绘制Polar码在不同码率和SNR下的性能曲线
    
    Args:
        result_file: 测试结果文件路径
        output_dir: 输出目录
    """
    # 读取测试结果
    data = {}
    
    with open(result_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        # 跳过表头
        for line in lines[7:]:  # 从第8行开始读取数据
            line = line.strip()
            if not line:
                continue
            
            # 解析行数据
            parts = line.split()
            if len(parts) >= 5:
                code_rate = float(parts[0])
                snr = float(parts[1])
                ber = float(parts[4])
                
                if code_rate not in data:
                    data[code_rate] = []
                data[code_rate].append((snr, ber))
    
    if not data:
        print("No test data found")
        return
    
    # 按SNR排序数据
    for code_rate in data:
        data[code_rate].sort(key=lambda x: x[0])
    
    # 创建图表
    plt.figure(figsize=(12, 8))
    
    # 定义颜色和标记
    colors = {'0.3': 'r', '0.5': 'g', '0.7': 'b'}
    markers = {'0.3': 'o', '0.5': 's', '0.7': '^'}
    
    # 绘制不同码率的曲线
    for code_rate in sorted(data.keys()):
        snr_values = [item[0] for item in data[code_rate]]
        ber_values = [item[1] for item in data[code_rate]]
        
        # 绘制BER曲线
        plt.semilogy(snr_values, ber_values, 
                    marker=markers.get(str(code_rate), 'o'),
                    linestyle='-',
                    linewidth=2,
                    markersize=8,
                    color=colors.get(str(code_rate), 'k'),
                    label=f'Code Rate = {code_rate}')
    
    # 添加性能临界点标记
    # 对于码率=0.5，5dB是临界点
    plt.axvline(x=5.0, color='k', linestyle='--', alpha=0.5, label='Critical SNR (5.0 dB)')
    plt.axhline(y=0.01, color='gray', linestyle='--', alpha=0.5, label='BER = 0.01')
    
    # 设置图表标题和标签
    plt.title('Polar Code Performance at Different Code Rates', fontsize=16)
    plt.xlabel('SNR (dB)', fontsize=12)
    plt.ylabel('Bit Error Rate (BER)', fontsize=12)
    
    # 设置坐标轴范围
    plt.xlim(0, 20)
    plt.ylim(1e-5, 1)
    
    # 添加网格
    plt.grid(True, which='both', linestyle='--', alpha=0.7)
    
    # 添加图例
    plt.legend(loc='upper right', fontsize=10)
    
    # 保存图表
    output_path = os.path.join(output_dir, 'polar_performance_plot.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    
    print(f"Chart saved to: {output_path}")
    
    # 显示图表
    plt.show()

def plot_snr_comparison(snr_result_file, polar_result_file, output_dir):
    """
    比较图像测试和误码率测试的SNR性能
    
    Args:
        snr_result_file: 图像SNR测试结果文件
        polar_result_file: Polar码误码率测试结果文件
        output_dir: 输出目录
    """
    # 读取图像SNR测试结果
    snr_data = []
    with open(snr_result_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[7:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 3:
                snr = float(parts[0])
                recovery_ratio = float(parts[2].replace('%', '')) / 100.0
                snr_data.append((snr, recovery_ratio))
    
    # 读取Polar码误码率测试结果（只取码率=0.5的数据）
    polar_data = []
    with open(polar_result_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[7:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 5:
                code_rate = float(parts[0])
                if code_rate == 0.5:
                    snr = float(parts[1])
                    ber = float(parts[4])
                    polar_data.append((snr, ber))
    
    if not snr_data or not polar_data:
        print("Insufficient test data for comparison")
        return
    
    # 排序数据
    snr_data.sort(key=lambda x: x[0])
    polar_data.sort(key=lambda x: x[0])
    
    # 创建双Y轴图表
    fig, ax1 = plt.subplots(figsize=(12, 8))
    
    # 绘制恢复比例曲线（左侧Y轴）
    snr_values = [item[0] for item in snr_data]
    recovery_values = [item[1] for item in snr_data]
    ax1.plot(snr_values, recovery_values, 'o-', linewidth=2, markersize=8, color='b', label='Recovery Ratio')
    ax1.set_xlabel('SNR (dB)', fontsize=12)
    ax1.set_ylabel('Recovery Ratio', fontsize=12, color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_ylim(0, 1.1)
    
    # 创建右侧Y轴用于BER
    ax2 = ax1.twinx()
    polar_snr = [item[0] for item in polar_data]
    polar_ber = [item[1] for item in polar_data]
    ax2.semilogy(polar_snr, polar_ber, 's-', linewidth=2, markersize=8, color='r', label='BER')
    ax2.set_ylabel('Bit Error Rate (BER)', fontsize=12, color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.set_ylim(1e-5, 1)
    
    # 添加性能临界点标记
    plt.axvline(x=5.0, color='k', linestyle='--', alpha=0.5, label='Critical SNR (5.0 dB)')
    
    # 设置图表标题
    plt.title('Comparison of Image Recovery and BER Performance', fontsize=16)
    
    # 添加网格
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)
    
    # 保存图表
    output_path = os.path.join(output_dir, 'performance_comparison_plot.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    
    print(f"Comparison chart saved to: {output_path}")
    
    # 显示图表
    plt.show()

if __name__ == "__main__":
    # 设置路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 1. 绘制Polar码性能曲线
    polar_result_file = os.path.join(project_root, 'evaluation', 'polar_code_evaluation.txt')
    output_dir = os.path.join(project_root, 'output', 'snr_test')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    if os.path.exists(polar_result_file):
        plot_polar_performance(polar_result_file, output_dir)
    else:
        print(f"Polar result file not found: {polar_result_file}")
    
    # 2. 绘制性能比较图
    snr_result_file = os.path.join(output_dir, 'snr_performance_results.txt')
    if os.path.exists(snr_result_file) and os.path.exists(polar_result_file):
        plot_snr_comparison(snr_result_file, polar_result_file, output_dir)
    else:
        print("Required result files not found for comparison")
