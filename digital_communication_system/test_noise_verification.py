#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
噪声叠加验证脚本

该脚本用于验证修改后的信道实现是否能够正确处理不同功率的信号
测试噪声叠加与生成是否合理
"""

import numpy as np
from py5g_phy_comm.channel import get_channel


def test_noise_superposition():
    """测试噪声叠加功能"""
    print("=== 测试噪声叠加功能 ===")
    
    # 测试信号功率
    signal_powers = [0.1, 0.5, 1.0, 2.0, 5.0]
    snr_dB = 10
    
    for power in signal_powers:
        print(f"\n测试信号功率={power}")
        
        # 生成测试信号
        np.random.seed(42)  # 固定随机种子
        signal = np.sqrt(power) * np.random.randn(1000)  # 实信号
        complex_signal = np.sqrt(power/2) * (np.random.randn(1000) + 1j * np.random.randn(1000))  # 复信号
        
        # 创建AWGN信道
        awgn_channel = get_channel('awgn', snr_dB=snr_dB)
        
        # 测试噪声叠加（实信号）
        output_signal = awgn_channel.propagate(signal)
        
        # 计算实际噪声功率
        actual_noise_power = np.mean(np.abs(output_signal - signal) ** 2)
        # 理论噪声功率
        theoretical_noise_power = power / (10 ** (snr_dB / 10))
        
        print(f"理论噪声功率: {theoretical_noise_power:.4f}")
        print(f"实际噪声功率: {actual_noise_power:.4f}")
        print(f"误差: {abs(actual_noise_power - theoretical_noise_power):.4f}")
        print(f"误差百分比: {abs(actual_noise_power - theoretical_noise_power)/theoretical_noise_power * 100:.2f}%")
        
        # 测试复信号
        output_complex_signal = awgn_channel.propagate(complex_signal)
        actual_complex_noise_power = np.mean(np.abs(output_complex_signal - complex_signal) ** 2)
        
        print(f"复信号理论噪声功率: {theoretical_noise_power:.4f}")
        print(f"复信号实际噪声功率: {actual_complex_noise_power:.4f}")
        print(f"复信号误差: {abs(actual_complex_noise_power - theoretical_noise_power):.4f}")


def test_different_snr():
    """测试不同SNR下的噪声叠加"""
    print("\n=== 测试不同SNR下的噪声叠加 ===")
    
    snr_values = [0, 5, 10, 15, 20]
    signal_power = 1.0
    
    for snr in snr_values:
        print(f"\n测试SNR={snr}dB")
        
        # 生成测试信号
        np.random.seed(42)
        signal = np.sqrt(signal_power) * np.random.randn(1000)
        
        # 创建AWGN信道
        awgn_channel = get_channel('awgn', snr_dB=snr)
        
        # 测试噪声叠加
        output_signal = awgn_channel.propagate(signal)
        
        # 计算噪声功率
        theoretical_noise_power = signal_power / (10 ** (snr / 10))
        actual_noise_power = np.mean(np.abs(output_signal - signal) ** 2)
        
        print(f"理论噪声功率: {theoretical_noise_power:.4f}")
        print(f"实际噪声功率: {actual_noise_power:.4f}")
        print(f"误差: {abs(actual_noise_power - theoretical_noise_power):.4f}")


def test_parameter_validation():
    """测试参数验证"""
    print("\n=== 测试参数验证 ===")
    
    # 测试负SNR
    try:
        awgn_channel = get_channel('awgn', snr_dB=-5)
        signal = np.random.randn(100)
        output = awgn_channel.propagate(signal)
        print("错误: 负SNR应该引发异常")
    except ValueError as e:
        print(f"正确: 负SNR引发异常: {e}")
    
    # 测试空信号
    try:
        awgn_channel = get_channel('awgn', snr_dB=10)
        signal = np.array([])
        output = awgn_channel.propagate(signal)
        print("错误: 空信号应该引发异常")
    except ValueError as e:
        print(f"正确: 空信号引发异常: {e}")


if __name__ == "__main__":
    test_noise_superposition()
    test_different_snr()
    test_parameter_validation()
    print("\n=== 验证完成 ===")
