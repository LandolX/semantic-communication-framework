#!/usr/bin/env python3
"""
生成不同信道编码在不同SNR下的BER对比图
"""

import os
import matplotlib.pyplot as plt

def plot_coding_comparison(result_file, output_dir):
    """
    生成不同信道编码在不同SNR下的BER对比图
    
    Args:
        result_file: 测试结果文件路径
        output_dir: 输出目录
    """
    # 读取测试结果
    data = {}
    
    with open(result_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        # 跳过表头
        for line in lines[6:]:  # 从第7行开始读取数据
            line = line.strip()
            if not line:
                continue
            
            # 解析行数据
            parts = line.split()
            if len(parts) >= 5:
                coding_scheme = parts[0]
                snr = float(parts[1])
                ber = float(parts[4])
                
                if coding_scheme not in data:
                    data[coding_scheme] = []
                data[coding_scheme].append((snr, ber))
    
    if not data:
        print("No test data found")
        return
    
    # 按SNR排序数据
    for coding_scheme in data:
        data[coding_scheme].sort(key=lambda x: x[0])
    
    # 创建图表
    plt.figure(figsize=(14, 10))
    
    # 定义颜色和标记
    styles = {
        'CRC': {'color': 'r', 'marker': 'o', 'linestyle': '-', 'label': 'CRC'}, 
        'LDPC': {'color': 'g', 'marker': 's', 'linestyle': '--', 'label': 'LDPC'},
        'POLAR': {'color': 'b', 'marker': '^', 'linestyle': '-.', 'label': 'Polar'}
    }
    
    # 绘制不同编码方案的曲线
    for coding_scheme in ['CRC', 'LDPC', 'POLAR']:
        if coding_scheme in data:
            snr_values = [item[0] for item in data[coding_scheme]]
            ber_values = [item[1] for item in data[coding_scheme]]
            
            # 绘制BER曲线
            style = styles.get(coding_scheme, {'color': 'k', 'marker': 'o', 'linestyle': '-', 'label': coding_scheme})
            plt.semilogy(snr_values, ber_values,
                        marker=style['marker'],
                        linestyle=style['linestyle'],
                        linewidth=2,
                        markersize=8,
                        color=style['color'],
                        label=style['label'])
    
    # 添加性能临界点标记
    # CRC 临界点 ~11.3dB
    plt.axvline(x=11.3, color='r', linestyle=':', alpha=0.5, label='CRC Threshold (11.3 dB)')
    # LDPC 临界点 ~11.0dB
    plt.axvline(x=11.0, color='g', linestyle=':', alpha=0.5, label='LDPC Threshold (11.0 dB)')
    # POLAR 临界点 ~10.0dB
    plt.axvline(x=10.0, color='b', linestyle=':', alpha=0.5, label='Polar Threshold (10.0 dB)')
    
    # 设置图表标题和标签
    plt.title('BER Performance Comparison of Different Channel Coding Schemes', fontsize=16)
    plt.xlabel('SNR (dB)', fontsize=12)
    plt.ylabel('Bit Error Rate (BER)', fontsize=12)
    
    # 设置坐标轴范围
    plt.xlim(0, 20)
    plt.ylim(1e-6, 0.6)
    
    # 添加网格
    plt.grid(True, which='both', linestyle='--', alpha=0.7)
    
    # 添加图例
    plt.legend(loc='upper right', fontsize=10)
    
    # 保存图表
    output_path = os.path.join(output_dir, 'coding_schemes_comparison.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    
    print(f"Comparison chart saved to: {output_path}")
    
    # 显示图表
    plt.show()

if __name__ == "__main__":
    # 设置路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    result_file = os.path.join(project_root, 'evaluation', 'coding_schemes_evaluation.txt')
    output_dir = os.path.join(project_root, 'output', 'snr_test')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    if os.path.exists(result_file):
        plot_coding_comparison(result_file, output_dir)
    else:
        print(f"Result file not found: {result_file}")
