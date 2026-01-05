#!/usr/bin/env python3
"""
演示脚本：展示5G物理层通信系统的使用方法
"""

import sys
import os
import numpy as np
import argparse

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from py5g_phy_comm import create_system


def demo_specific_configuration(modulation_type, channel_type, snr_dB):
    """
    使用指定的配置进行通信仿真
    
    Parameters:
    -----------
    modulation_type : str
        调制类型 ('bpsk', 'qpsk', '16qam', '64qam')
    
    channel_type : str
        信道类型 ('awgn', 'rayleigh', 'rician')
    
    snr_dB : float
        信噪比 (dB)
    """
    print(f"\n=== Specific Configuration Demo ===")
    print(f"Creating communication system with {modulation_type.upper()} modulation, {channel_type.upper()} channel, and SNR = {snr_dB} dB")
    
    # 创建通信系统
    system = create_system(
        use_simple=True,  # 使用简化版本（无OFDM）
        modulation_type=modulation_type,  # 指定调制类型
        snr_dB=snr_dB,  # 指定SNR
        channel_type=channel_type  # 指定信道类型
    )
    
    # 要传输的数据
    test_data = b"This is a demo of 5G physical layer communication system with specific configuration!"
    print(f"\nSending data: {test_data}")
    
    # 发送和接收数据
    received_data, ber = system.transmit_receive(test_data)
    
    # 打印结果
    print(f"\nReceived data: {received_data}")
    print(f"Bit Error Rate (BER): {ber:.6f}")
    print(f"Data match: {test_data == received_data}")
    
    # 显示星座图
    system.visualize_constellation(title=f'{modulation_type.upper()} Constellation - {channel_type.upper()} Channel, SNR={snr_dB} dB')


def demo_basic_usage():
    """
    演示基本使用方法：创建系统并传输数据
    """
    print("\n=== Basic Usage Demo ===")
    print("Creating a simple communication system with QPSK modulation and AWGN channel")
    
    # 创建通信系统
    system = create_system(
        use_simple=True,  # 使用简化版本（无OFDM）
        modulation_type='qpsk',  # QPSK调制
        snr_dB=15,  # SNR=15dB
        channel_type='awgn'  # AWGN信道
    )
    
    # 要传输的数据
    test_data = b"This is a demo of 5G physical layer communication system!"
    print(f"\nSending data: {test_data}")
    
    # 发送和接收数据
    received_data, ber = system.transmit_receive(test_data)
    
    # 打印结果
    print(f"\nReceived data: {received_data}")
    print(f"Bit Error Rate (BER): {ber:.6f}")
    print(f"Data match: {test_data == received_data}")
    
    # 显示星座图
    system.visualize_constellation(title='Basic Usage - QPSK Constellation')


def demo_different_modulations():
    """
    演示不同调制类型的使用
    """
    print("\n=== Different Modulations Demo ===")
    print("Transmitting the same data with different modulation types")
    
    # 创建系统
    system = create_system(use_simple=True, snr_dB=20, channel_type='awgn')
    
    # 测试数据
    test_data = b"Testing different modulations"
    
    # 测试的调制类型
    modulation_types = ['bpsk', 'qpsk', '16qam', '64qam', '256qam']
    
    for mod_type in modulation_types:
        # 设置调制类型
        system.set_modulation_type(mod_type)
        
        # 发送和接收
        received_data, ber = system.transmit_receive(test_data)
        
        print(f"\n{mod_type.upper()}")
        print(f"  BER: {ber:.6f}")
        print(f"  Match: {test_data == received_data}")
        
        # 显示星座图
        system.visualize_constellation(title=f'{mod_type.upper()} Constellation - AWGN Channel, SNR=20 dB')


def demo_different_channels():
    """
    演示不同信道模型的使用
    """
    print("\n=== Different Channels Demo ===")
    print("Transmitting data over different channel models")
    
    # 创建系统
    system = create_system(use_simple=True, modulation_type='qpsk', snr_dB=25)
    
    # 测试数据
    test_data = b"Testing different channels"
    
    # 测试的信道类型
    channel_types = ['awgn', 'rayleigh', 'rician']
    
    for chan_type in channel_types:
        # 设置信道类型
        system.set_channel_type(chan_type)
        
        # 发送和接收
        received_data, ber = system.transmit_receive(test_data)
        
        print(f"\n{chan_type.upper()} Channel")
        print(f"  BER: {ber:.6f}")
        print(f"  Match: {test_data == received_data}")
        
        # 显示星座图
        system.visualize_constellation(title=f'QPSK Constellation - {chan_type.upper()} Channel, SNR=25 dB')


def demo_snr_effect():
    """
    演示不同SNR值的影响
    """
    print("\n=== SNR Impact Demo ===")
    print("Transmitting data with different SNR values")
    
    # 创建系统
    system = create_system(use_simple=True, modulation_type='qpsk', channel_type='awgn')
    
    # 测试数据
    test_data = b"Testing different SNR values"
    
    # 测试的SNR值
    snr_values = [0, 5, 10, 15, 20]
    
    for snr in snr_values:
        # 设置SNR值
        system.set_snr_dB(snr)
        
        # 发送和接收
        received_data, ber = system.transmit_receive(test_data)
        
        print(f"\nSNR = {snr} dB")
        print(f"  BER: {ber:.6f}")
        print(f"  Match: {test_data == received_data}")
        
        # 显示星座图
        system.visualize_constellation(title=f'QPSK Constellation - AWGN Channel, SNR={snr} dB')


def demo_ofdm_usage():
    """
    演示带OFDM的完整系统
    """
    print("\n=== OFDM System Demo ===")
    print("Using complete communication system with OFDM")
    
    # 创建带OFDM的系统
    system = create_system(
        use_simple=False,  # 使用完整版本（带OFDM）
        modulation_type='qpsk',
        snr_dB=15,
        channel_type='awgn',
        nfft=512,  # FFT大小
        nsc=300,   # 子载波数量
        cp_length=64  # 循环前缀长度
    )
    
    # 测试数据
    test_data = b"5G physical layer demo with OFDM"
    print(f"\n发送数据: {test_data}")
    
    # 发送和接收
    received_data, ber = system.transmit_receive(test_data)
    
    print(f"\n接收数据: {received_data}")
    print(f"误码率: {ber:.6f}")
    print(f"数据匹配: {test_data == received_data}")
    
    # 显示星座图
    system.visualize_constellation(title='OFDM System - QPSK Constellation, AWGN Channel, SNR=15 dB')


def main():
    """
    Main demo function with command line argument parsing
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='5G Physical Layer Communication System Demo')
    
    # 添加命令行参数
    parser.add_argument('--modulation', '-m', choices=['bpsk', 'qpsk', '16qam', '64qam', '256qam'],
                        help='Specify modulation type for specific configuration demo')
    parser.add_argument('--channel', '-c', choices=['awgn', 'rayleigh', 'rician'],
                        help='Specify channel type for specific configuration demo')
    parser.add_argument('--snr', '-s', type=float,
                        help='Specify SNR (dB) for specific configuration demo')
    parser.add_argument('--demo', '-d', action='store_true',
                        help='Run all demo functions instead of specific configuration')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 检查是否提供了特定配置参数
    if args.modulation and args.channel and args.snr:
        # 运行特定配置的demo
        demo_specific_configuration(args.modulation, args.channel, args.snr)
    elif args.demo:
        # 运行所有demo
        print("5G Physical Layer Communication System Demo")
        print("=" * 50)
        
        # Run all demos
        demo_basic_usage()
        demo_different_modulations()
        demo_different_channels()
        demo_snr_effect()
        demo_ofdm_usage()
        
        print("\n" + "=" * 50)
        print("Demo completed! You can modify demo.py to create your own tests.")
    else:
        # 显示帮助信息
        parser.print_help()
        print("\nExample usage:")
        print("  python demo.py --modulation 64qam --channel awgn --snr 20")
        print("  python demo.py -m 16qam -c rayleigh -s 15")
        print("  python demo.py --demo")


if __name__ == "__main__":
    main()
