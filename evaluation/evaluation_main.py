#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信道编码性能评估脚本

该脚本用于测试不同信道编码（特别是极化码）在经过调制、信道、解调、解码后的误码率性能。
"""

import os
import sys
import numpy as np
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入必要的模块
from digital_communication_system.py5g_phy_comm import (
    CommunicationSystem,
    Modem, get_modem,
    Channel, get_channel,
    Transmitter, Receiver,
    calculate_ber
)
from image_process.channel_coding.crc_channel_codec.crc_encoder import CRCEncoder
from image_process.channel_coding.ldpc_channel_codec.ldpc_channel_encoder import LDPCChannelEncoder
from image_process.channel_coding.polar_channel_codec.polar_encoder import PolarEncoder
from image_recover.channel_coding.crc_channel_codec.crc_decoder import CRCDecoder
from image_recover.channel_coding.ldpc_channel_codec.ldpc_channel_decoder import LDPCChannelDecoder
from image_recover.channel_coding.polar_channel_codec.polar_decoder import PolarDecoder

class ChannelCodingEvaluator:
    """
    信道编码性能评估器
    """
    
    def __init__(self, debug=False):
        """
        初始化评估器
        
        Args:
            debug: 是否开启调试输出
        """
        self.debug = debug
        self.results = {}
    
    def generate_test_data(self, size=1024):
        """
        生成测试数据

        Args:
            size: 数据大小（字节）

        Returns:
            bytes: 随机测试数据
        """
        return os.urandom(size)
    
    def _bytes_to_bits(self, bytes_data):
        """
        将字节序列转换为比特序列

        Args:
            bytes_data: 字节序列

        Returns:
            np.ndarray: 比特序列
        """
        bits = []
        for byte in bytes_data:
            for i in range(8):
                bits.append((byte >> (7-i)) & 1)
        return np.array(bits, dtype=int)
    
    def _bits_to_bytes(self, bits):
        """
        将比特序列转换为字节序列

        Args:
            bits: 比特序列

        Returns:
            bytes: 字节序列
        """
        # 确保比特数是8的倍数
        padding = (8 - len(bits) % 8) % 8
        if padding > 0:
            bits = np.concatenate([bits, np.zeros(padding, dtype=int)])
        
        # 转换为字节
        bytes_data = b''
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                byte |= bits[i+j] << (7-j)
            bytes_data += bytes([byte])
        
        return bytes_data
    
    def setup_communication_system(self, modulation_type='qpsk', channel_type='awgn', snr_dB=10):
        """
        设置通信系统
        
        Args:
            modulation_type: 调制类型
            channel_type: 信道类型
            snr_dB: 信噪比（dB）
            
        Returns:
            CommunicationSystem: 完整的通信系统
        """
        # 创建完整的通信系统
        from digital_communication_system.py5g_phy_comm import CommunicationSystem
        system = CommunicationSystem(
            use_simple=True,        # 使用简化版本（无OFDM）
            modulation_type=modulation_type,
            channel_type=channel_type,
            snr_dB=snr_dB
        )
        return system
    
    def test_channel_coding(self, coding_scheme, test_data, snr_dB=10, modulation_type='qpsk', channel_type='awgn'):
        """
        测试特定信道编码的性能
        
        Args:
            coding_scheme: 信道编码方案（'crc', 'ldpc', 'polar'）
            test_data: 测试数据
            snr_dB: 信噪比（dB）
            modulation_type: 调制类型
            channel_type: 信道类型
            
        Returns:
            dict: 测试结果
        """
        if self.debug:
            print(f"\n=== 测试 {coding_scheme.upper()} 编码，SNR={snr_dB}dB ===")
        
        start_time = time.time()
        
        # 设置通信系统
        system = self.setup_communication_system(
            modulation_type=modulation_type,
            channel_type=channel_type,
            snr_dB=snr_dB
        )
        
        # 初始化编码器和解码器
        if coding_scheme == 'crc':
            encoder = CRCEncoder(crc_polynomial='crc16')
            decoder = CRCDecoder()
        elif coding_scheme == 'ldpc':
            encoder = LDPCChannelEncoder(code_rate=0.5)
            decoder = LDPCChannelDecoder()
        elif coding_scheme == 'polar':
            encoder = PolarEncoder(code_rate=0.5, construction_SNR=2.0)
            decoder = PolarDecoder()
        else:
            raise ValueError(f"不支持的编码方案: {coding_scheme}")
        
        # 1. 信道编码
        encoded_data = encoder.encode(test_data)
        if self.debug:
            print(f"编码完成: 原始数据大小={len(test_data)} bytes, 编码后大小={len(encoded_data)} bytes")
        
        # 2. 传输和接收（包括调制、信道、解调）
        received_data, system_ber = system.transmit_receive(encoded_data)
        if self.debug:
            print(f"传输完成: 接收数据大小={len(received_data)} bytes")
        
        # 3. 信道解码
        decoded_data_tuple = decoder.decode(received_data)
        # 提取原始数据（解码器返回的是元组：(原始数据, 解码状态)）
        decoded_data = decoded_data_tuple[0]
        if self.debug:
            print(f"解码完成: 解码数据大小={len(decoded_data)} bytes, 解码状态={decoded_data_tuple[1]}")
        
        # 4. 计算误码率
        # 确保比较的数据长度相同
        min_len = min(len(test_data), len(decoded_data))
        
        if min_len == 0:
            # 解码数据为空，认为完全失败
            ber = 0.5  # 完全随机猜测的误码率
        else:
            ber = calculate_ber(test_data[:min_len], decoded_data[:min_len])
        
        end_time = time.time()
        
        result = {
            'coding_scheme': coding_scheme,
            'snr_dB': snr_dB,
            'modulation_type': modulation_type,
            'channel_type': channel_type,
            'test_data_size': len(test_data),
            'ber': ber,
            'encoding_time': end_time - start_time,
            'encoded_data_size': len(encoded_data),
            'decoded_data_size': len(decoded_data),
            'system_ber': system_ber
        }
        
        if self.debug:
            print(f"测试结果: BER={ber:.6f}, 系统BER={system_ber:.6f}, 耗时={end_time - start_time:.3f}s")
        
        return result
    
    def evaluate_coding_schemes(self, snr_values=None, modulation_type='qpsk', channel_type='awgn', test_data_size=1024):
        """
        评估不同信道编码方案的性能
        
        Args:
            snr_values: 信噪比列表（dB）
            modulation_type: 调制类型
            channel_type: 信道类型
            test_data_size: 测试数据大小（字节）
            
        Returns:
            dict: 评估结果
        """
        if snr_values is None:
            snr_values = [0, 5, 10, 15, 20]
        
        # 生成测试数据
        test_data = self.generate_test_data(test_data_size)
        
        # 测试不同编码方案
        coding_schemes = ['crc', 'ldpc', 'polar']
        results = {}
        
        for coding_scheme in coding_schemes:
            results[coding_scheme] = []
            for snr in snr_values:
                result = self.test_channel_coding(
                    coding_scheme=coding_scheme,
                    test_data=test_data,
                    snr_dB=snr,
                    modulation_type=modulation_type,
                    channel_type=channel_type
                )
                results[coding_scheme].append(result)
        
        self.results = results
        return results
    
    def evaluate_polar_codes(self, snr_values=None, code_rates=None, modulation_type='qpsk', channel_type='awgn', test_data_size=1024):
        """
        评估极化码在不同码率下的性能
        
        Args:
            snr_values: 信噪比列表（dB）
            code_rates: 码率列表
            modulation_type: 调制类型
            channel_type: 信道类型
            test_data_size: 测试数据大小（字节）
            
        Returns:
            dict: 评估结果
        """
        if snr_values is None:
            snr_values = [0, 5, 10, 15, 20]
        
        if code_rates is None:
            code_rates = [0.3, 0.5, 0.7]
        
        # 生成测试数据
        test_data = self.generate_test_data(test_data_size)
        
        results = {}
        
        for rate in code_rates:
            results[rate] = []
            
            for snr in snr_values:
                if self.debug:
                    print(f"\n=== 测试极化码，码率={rate}, SNR={snr}dB ===")
                
                start_time = time.time()
                
                # 初始化极化码编码器和解码器
                encoder = PolarEncoder(code_rate=rate, construction_SNR=2.0)
                decoder = PolarDecoder()
                
                # 设置通信系统
                system = self.setup_communication_system(
                    modulation_type=modulation_type,
                    channel_type=channel_type,
                    snr_dB=snr
                )
                
                # 1. 信道编码
                encoded_data = encoder.encode(test_data)
                if self.debug:
                    print(f"编码完成: 原始数据大小={len(test_data)} bytes, 编码后大小={len(encoded_data)} bytes")
                
                # 2. 直接测试极化码性能（绕过通信系统的硬判决）
                # 生成测试比特序列
                test_bits = self._bytes_to_bits(test_data)
                
                # 直接测试极化码编码器和解码器
                # 编码
                encoded_bits = encoder.encode_bits(test_bits)
                
                # 添加AWGN噪声（直接在比特级添加噪声，模拟软信息）
                noise_std = np.sqrt(0.5 / (10 ** (snr / 10)))
                noisy_llr = np.zeros(len(encoded_bits))
                for i in range(len(encoded_bits)):
                    # 对于编码比特，计算LLR
                    if encoded_bits[i] == 0:
                        noisy_llr[i] = 1.0 + np.random.normal(0, noise_std)
                    else:
                        noisy_llr[i] = -1.0 + np.random.normal(0, noise_std)
                
                # 软解码
                decoded_bits = decoder.decode_bits(noisy_llr, encoder.info_bits, encoder.code_bits)
                
                # 转换回字节
                decoded_data = self._bits_to_bytes(decoded_bits)
                system_ber = 0.0  # 直接测试模式，不计算系统BER
                if self.debug:
                    print(f"软解码完成: 解码数据大小={len(decoded_data)} bytes")
                
                # 4. 计算误码率
                min_len = min(len(test_data), len(decoded_data))
                
                if min_len == 0:
                    # 解码数据为空，认为完全失败
                    ber = 0.5  # 完全随机猜测的误码率
                else:
                    ber = calculate_ber(test_data[:min_len], decoded_data[:min_len])
                
                end_time = time.time()
                
                result = {
                    'code_rate': rate,
                    'snr_dB': snr,
                    'modulation_type': modulation_type,
                    'channel_type': channel_type,
                    'test_data_size': len(test_data),
                    'ber': ber,
                    'encoding_time': end_time - start_time,
                    'encoded_data_size': len(encoded_data),
                    'decoded_data_size': len(decoded_data),
                    'system_ber': system_ber
                }
                
                results[rate].append(result)
                
                if self.debug:
                    print(f"测试结果: BER={ber:.6f}, 系统BER={system_ber:.6f}, 耗时={end_time - start_time:.3f}s")
        
        return results
    
    def print_results(self, results=None):
        """
        打印评估结果
        
        Args:
            results: 评估结果，默认使用self.results
        """
        if results is None:
            results = self.results
        
        print("\n=== 信道编码性能评估结果 ===")
        print("-" * 80)
        print(f"{'编码方案':<10} {'SNR(dB)':<10} {'调制类型':<10} {'信道类型':<10} {'BER':<15} {'耗时(s)':<10}")
        print("-" * 80)
        
        for coding_scheme, scheme_results in results.items():
            for result in scheme_results:
                print(f"{coding_scheme.upper():<10} {result['snr_dB']:<10} {result['modulation_type']:<10} {result['channel_type']:<10} {result['ber']:<15.6f} {result['encoding_time']:<10.3f}")
        
        print("-" * 80)
    
    def print_polar_results(self, results):
        """
        打印极化码评估结果
        
        Args:
            results: 极化码评估结果
        """
        print("\n=== 极化码性能评估结果 ===")
        print("-" * 80)
        print(f"{'码率':<10} {'SNR(dB)':<10} {'调制类型':<10} {'信道类型':<10} {'BER':<15} {'耗时(s)':<10}")
        print("-" * 80)
        
        for code_rate, rate_results in results.items():
            for result in rate_results:
                print(f"{code_rate:<10.2f} {result['snr_dB']:<10} {result['modulation_type']:<10} {result['channel_type']:<10} {result['ber']:<15.6f} {result['encoding_time']:<10.3f}")
        
        print("-" * 80)
    
    def save_results(self, results, filename=None):
        """
        保存评估结果
        
        Args:
            results: 评估结果
            filename: 保存文件名，默认自动生成
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_results_{timestamp}.txt"
        
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=== 信道编码性能评估结果 ===\n")
            f.write(f"评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 检查是否是极化码结果（键是浮点数类型）
            is_polar_result = False
            for key in results.keys():
                if isinstance(key, float):
                    is_polar_result = True
                    break
            
            if is_polar_result:
                # 极化码结果
                f.write("=== 极化码性能评估 ===\n")
                f.write(f"{'码率':<10} {'SNR(dB)':<10} {'调制类型':<10} {'信道类型':<10} {'BER':<15} {'耗时(s)':<10}\n")
                f.write("-" * 80 + "\n")
                
                for code_rate, rate_results in results.items():
                    for result in rate_results:
                        f.write(f"{code_rate:<10.2f} {result['snr_dB']:<10} {result['modulation_type']:<10} {result['channel_type']:<10} {result['ber']:<15.6f} {result['encoding_time']:<10.3f}\n")
            else:
                # 一般编码结果
                f.write("=== 不同编码方案性能评估 ===\n")
                f.write(f"{'编码方案':<10} {'SNR(dB)':<10} {'调制类型':<10} {'信道类型':<10} {'BER':<15} {'耗时(s)':<10}\n")
                f.write("-" * 80 + "\n")
                
                for coding_scheme, scheme_results in results.items():
                    for result in scheme_results:
                        f.write(f"{coding_scheme.upper():<10} {result['snr_dB']:<10} {result['modulation_type']:<10} {result['channel_type']:<10} {result['ber']:<15.6f} {result['encoding_time']:<10.3f}\n")
        
        print(f"\n评估结果已保存到: {filepath}")

def main():
    """
    主函数
    """
    # 初始化评估器
    evaluator = ChannelCodingEvaluator(debug=True)
    
    # 评估不同信道编码方案（进一步缩小步长，聚焦临界区域）
    print("=== 开始评估不同信道编码方案 ===")
    print("使用超精细的SNR步长：11.0-12.0dB，步长0.05dB；其他范围步长1dB")
    # 生成SNR值：0-10dB（2dB步长），11.0-12.0dB（0.05dB步长），12.5-20dB（2dB步长）
    snr_values = []
    # 0-10dB，步长2dB
    snr_values.extend([0, 2, 4, 6, 8, 10])
    # 11.0-12.0dB，步长0.05dB（临界区域）
    snr_values.extend([11.0, 11.05, 11.1, 11.15, 11.2, 11.25, 11.3, 11.35, 11.4, 11.45, 11.5, 11.55, 11.6, 11.65, 11.7, 11.75, 11.8, 11.85, 11.9, 11.95, 12.0])
    # 12.5-20dB，步长2dB
    snr_values.extend([12.5, 14, 16, 18, 20])
    
    coding_results = evaluator.evaluate_coding_schemes(
        snr_values=snr_values,
        modulation_type='qpsk',
        channel_type='awgn',
        test_data_size=1024
    )
    
    # 打印结果
    evaluator.print_results(coding_results)
    
    # 保存结果
    evaluator.save_results(coding_results, "coding_schemes_evaluation.txt")
    
    # 评估极化码性能
    print("\n=== 开始评估极化码性能 ===")
    polar_results = evaluator.evaluate_polar_codes(
        snr_values=[0, 5, 10, 15, 20],
        code_rates=[0.3, 0.5, 0.7],
        modulation_type='qpsk',
        channel_type='awgn',
        test_data_size=1024
    )
    
    # 打印极化码结果
    evaluator.print_polar_results(polar_results)
    
    # 保存极化码结果
    evaluator.save_results(polar_results, "polar_code_evaluation.txt")
    
    print("\n=== 评估完成 ===")

if __name__ == "__main__":
    main()
