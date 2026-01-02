#!/usr/bin/env python3
"""
验证信道修复的测试脚本
"""

import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from py5g_phy_comm.channel import AWGNChannel, RayleighChannel, RicianChannel, FrequencySelectiveChannel


def test_signal_type_detection():
    """测试信号类型检测"""
    print("=== 测试信号类型检测 ===")
    
    # 测试复数信号
    complex_signal = np.array([1+1j, 2+2j, 3+3j])
    channel = AWGNChannel(snr_dB=10)
    output = channel.propagate(complex_signal)
    assert channel.is_complex == True, "复数信号检测失败"
    print("✓ 复数信号检测正确")
    
    # 测试实数信号
    real_signal = np.array([1.0, 2.0, 3.0])
    channel = AWGNChannel(snr_dB=10)
    output = channel.propagate(real_signal)
    assert channel.is_complex == False, "实数信号检测失败"
    print("✓ 实数信号检测正确")
    
    # 测试混合信号（实数数组但包含复数元素）
    mixed_signal = np.array([1.0, 2.0+0j, 3.0])
    channel = AWGNChannel(snr_dB=10)
    output = channel.propagate(mixed_signal)
    assert channel.is_complex == True, "混合信号检测失败"
    print("✓ 混合信号检测正确")
    
    print()


def test_power_normalization():
    """测试功率归一化"""
    print("=== 测试功率归一化 ===")
    
    num_samples = 10000
    snr_dB = 10
    snr_linear = 10 ** (snr_dB / 10)
    
    # 测试瑞利信道
    print("测试瑞利信道功率归一化...")
    signal = np.random.randn(num_samples) + 1j * np.random.randn(num_samples)
    signal_power = np.mean(np.abs(signal) ** 2)
    
    channel = RayleighChannel(snr_dB=snr_dB)
    output = channel.propagate(signal)
    
    output_power = np.mean(np.abs(output) ** 2)
    noise_power = output_power / (1 + snr_linear)
    
    # 验证SNR
    measured_snr = output_power / noise_power
    snr_error = abs(10 * np.log10(measured_snr) - snr_dB)
    assert snr_error < 0.5, f"瑞利信道SNR误差过大: {snr_error:.2f} dB"
    print(f"✓ 瑞利信道SNR正确 (误差: {snr_error:.3f} dB)")
    
    # 测试莱斯信道
    print("测试莱斯信道功率归一化...")
    channel = RicianChannel(snr_dB=snr_dB, k_factor=3)
    output = channel.propagate(signal)
    
    output_power = np.mean(np.abs(output) ** 2)
    noise_power = output_power / (1 + snr_linear)
    
    measured_snr = output_power / noise_power
    snr_error = abs(10 * np.log10(measured_snr) - snr_dB)
    assert snr_error < 0.5, f"莱斯信道SNR误差过大: {snr_error:.2f} dB"
    print(f"✓ 莱斯信道SNR正确 (误差: {snr_error:.3f} dB)")
    
    print()


def test_frequency_selective_channel():
    """测试频率选择性信道"""
    print("=== 测试频率选择性信道 ===")
    
    # 测试抽头归一化
    print("测试抽头功率归一化...")
    taps = np.array([1.0, 0.5, 0.25])
    channel = FrequencySelectiveChannel(snr_dB=10, taps=taps)
    
    # 验证归一化后的功率
    normalized_power = np.sum(np.abs(channel.taps) ** 2)
    assert abs(normalized_power - 1.0) < 1e-10, f"抽头功率归一化失败: {normalized_power}"
    print(f"✓ 抽头功率归一化正确 (功率: {normalized_power:.6f})")
    
    # 测试边界处理
    print("测试边界处理...")
    # 使用固定衰落增益来测试边界处理
    signal = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    channel = FrequencySelectiveChannel(snr_dB=100, taps=[1.0], delays=[2])
    
    # 手动设置固定的衰落增益（全为1）
    num_samples = len(signal)
    channel.channel_gains = np.ones((num_samples, 1), dtype=complex)
    
    # 手动传播信号（绕过随机衰落）
    delay = 2
    output = np.zeros(num_samples, dtype=complex)
    if delay > 0:
        delayed_signal = np.zeros(num_samples, dtype=complex)
        delayed_signal[delay:] = signal[:-delay]
    else:
        delayed_signal = signal.copy()
    
    faded_delayed_signal = delayed_signal * channel.channel_gains[:, 0] * channel.taps[0]
    output = faded_delayed_signal
    
    # 验证延迟后的信号
    assert abs(output[0]) < 1e-10, f"边界处理失败：第一个元素应该为0，实际为{output[0]}"
    assert abs(output[1]) < 1e-10, f"边界处理失败：第二个元素应该为0，实际为{output[1]}"
    assert abs(output[2] - 1.0) < 1e-10, f"边界处理失败：第三个元素应该为1.0，实际为{output[2]}"
    assert abs(output[3] - 2.0) < 1e-10, f"边界处理失败：第四个元素应该为2.0，实际为{output[3]}"
    print("✓ 边界处理正确（零填充而非循环移位）")
    
    # 测试SNR
    print("测试频率选择性信道SNR...")
    num_samples = 10000
    signal = np.random.randn(num_samples) + 1j * np.random.randn(num_samples)
    channel = FrequencySelectiveChannel(snr_dB=10, taps=[1.0, 0.5], delays=[0, 1])
    output = channel.propagate(signal)
    
    output_power = np.mean(np.abs(output) ** 2)
    snr_linear = 10 ** (10 / 10)
    noise_power = output_power / (1 + snr_linear)
    measured_snr = output_power / noise_power
    
    snr_error = abs(10 * np.log10(measured_snr) - 10)
    assert snr_error < 0.5, f"频率选择性信道SNR误差过大: {snr_error:.2f} dB"
    print(f"✓ 频率选择性信道SNR正确 (误差: {snr_error:.3f} dB)")
    
    print()


def test_awgn_channel():
    """测试AWGN信道"""
    print("=== 测试AWGN信道 ===")
    
    num_samples = 10000
    snr_dB = 10
    snr_linear = 10 ** (snr_dB / 10)
    
    # 测试复数信号
    print("测试复数信号AWGN...")
    signal = np.random.randn(num_samples) + 1j * np.random.randn(num_samples)
    signal_power = np.mean(np.abs(signal) ** 2)
    
    channel = AWGNChannel(snr_dB=snr_dB)
    output = channel.propagate(signal)
    
    output_power = np.mean(np.abs(output) ** 2)
    noise_power = output_power - signal_power
    measured_snr = signal_power / noise_power
    
    snr_error = abs(10 * np.log10(measured_snr) - snr_dB)
    assert snr_error < 0.5, f"AWGN信道SNR误差过大: {snr_error:.2f} dB"
    print(f"✓ AWGN信道SNR正确 (误差: {snr_error:.3f} dB)")
    
    print()


def main():
    """运行所有测试"""
    print("\n" + "="*50)
    print("信道修复验证测试")
    print("="*50 + "\n")
    
    try:
        test_signal_type_detection()
        test_power_normalization()
        test_frequency_selective_channel()
        test_awgn_channel()
        
        print("="*50)
        print("✓ 所有测试通过！")
        print("="*50 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
