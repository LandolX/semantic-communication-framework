import numpy as np
import pytest
from py5g_phy_comm.utils import (
    bitarray2bytes,
    bytes2bitarray,
    calculate_ber,
    calculate_ser,
    generate_random_bits,
    generate_random_bytes,
    normalize_signal,
    add_awgn_noise,
    calculate_power,
    calculate_evm,
    hex_to_bytes,
    bytes_to_hex,
    get_modulation_order
)

class TestUtils:
    """测试工具模块的功能"""
    
    def test_bitarray2bytes(self):
        """测试比特数组转字节功能"""
        # 测试正常情况
        test_bits = np.array([0, 1, 0, 1, 1, 0, 0, 1], dtype=int)  # 8位比特，正好1字节
        bytes_data = bitarray2bytes(test_bits)
        assert isinstance(bytes_data, bytes)
        assert len(bytes_data) == 1
        
        # 测试需要填充的情况
        test_bits_short = np.array([0, 1, 0, 1], dtype=int)  # 4位比特，需要填充到8位
        bytes_data_short = bitarray2bytes(test_bits_short)
        assert isinstance(bytes_data_short, bytes)
        assert len(bytes_data_short) == 1
    
    def test_bytes2bitarray(self):
        """测试字节转比特数组功能"""
        # 测试正常情况
        test_bytes = b'Hello'
        bit_array = bytes2bitarray(test_bytes)
        assert isinstance(bit_array, np.ndarray)
        assert len(bit_array) == len(test_bytes) * 8
        assert all(bit in [0, 1] for bit in bit_array)
    
    def test_calculate_ber(self):
        """测试误码率计算功能"""
        # 测试完全相同的数据
        test_data1 = b'Hello'
        test_data2 = b'Hello'
        ber = calculate_ber(test_data1, test_data2)
        assert ber == 0.0
        
        # 测试完全不同的数据
        test_data3 = b'World'
        ber_diff = calculate_ber(test_data1, test_data3)
        assert ber_diff > 0.0
        assert ber_diff <= 1.0
        
        # 测试不同长度的数据
        test_data_short = b'Hel'
        ber_short = calculate_ber(test_data1, test_data_short)
        assert isinstance(ber_short, float)
    
    def test_calculate_ser(self):
        """测试符号误码率计算功能"""
        # 测试完全相同的符号
        test_symbols1 = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        test_symbols2 = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        ser = calculate_ser(test_symbols1, test_symbols2)
        assert ser == 0.0
        
        # 测试完全不同的符号
        test_symbols3 = np.array([-1-1j, 1-1j, 1+1j, -1+1j], dtype=complex)
        ser_diff = calculate_ser(test_symbols1, test_symbols3)
        assert ser_diff > 0.0
        assert ser_diff <= 1.0
        
        # 测试不同长度的符号
        test_symbols_short = np.array([1+1j, -1+1j], dtype=complex)
        ser_short = calculate_ser(test_symbols1, test_symbols_short)
        assert isinstance(ser_short, float)
    
    def test_generate_random_bits(self):
        """测试生成随机比特功能"""
        # 测试生成指定长度的随机比特
        length = 10
        random_bits = generate_random_bits(length)
        assert len(random_bits) == length
        assert all(bit in [0, 1] for bit in random_bits)
    
    def test_generate_random_bytes(self):
        """测试生成随机字节功能"""
        # 测试生成指定长度的随机字节
        length = 5
        random_bytes = generate_random_bytes(length)
        assert isinstance(random_bytes, bytes)
        assert len(random_bytes) == length
    
    def test_normalize_signal(self):
        """测试信号归一化功能"""
        # 生成测试信号
        test_signal = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        
        # 测试归一化到默认功率（1.0）
        normalized_signal = normalize_signal(test_signal)
        assert len(normalized_signal) == len(test_signal)
        
        # 计算归一化后的功率
        power = np.mean(np.abs(normalized_signal) ** 2)
        assert np.isclose(power, 1.0)
        
        # 测试归一化到自定义功率
        target_power = 0.5
        normalized_signal_custom = normalize_signal(test_signal, target_power=target_power)
        power_custom = np.mean(np.abs(normalized_signal_custom) ** 2)
        assert np.isclose(power_custom, target_power)
    
    def test_add_awgn_noise(self):
        """测试添加AWGN噪声功能"""
        # 生成测试信号
        test_signal = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        
        # 测试添加噪声
        snr_dB = 10
        noisy_signal, noise = add_awgn_noise(test_signal, snr_dB)
        
        # 验证带噪声的信号长度与输入信号相同
        assert len(noisy_signal) == len(test_signal)
        
        # 验证噪声长度与输入信号相同
        assert len(noise) == len(test_signal)
        
        # 测试实信号添加噪声
        test_signal_real = np.array([1.0, -1.0, 0.5, -0.5], dtype=float)
        noisy_signal_real, noise_real = add_awgn_noise(test_signal_real, snr_dB)
        assert len(noisy_signal_real) == len(test_signal_real)
        assert len(noise_real) == len(test_signal_real)
    
    def test_calculate_power(self):
        """测试功率计算功能"""
        # 测试复数信号功率计算
        test_signal_complex = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        power_complex = calculate_power(test_signal_complex)
        assert isinstance(power_complex, float)
        assert power_complex > 0
        
        # 测试实信号功率计算
        test_signal_real = np.array([1.0, -1.0, 0.5, -0.5], dtype=float)
        power_real = calculate_power(test_signal_real)
        assert isinstance(power_real, float)
        assert power_real > 0
    
    def test_calculate_evm(self):
        """测试误差向量幅度计算功能"""
        # 测试完全相同的符号
        test_symbols1 = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        test_symbols2 = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        evm = calculate_evm(test_symbols1, test_symbols2)
        assert evm == 0.0
        
        # 测试有误差的符号
        test_symbols3 = np.array([1.1+1.1j, -0.9+0.9j, -0.9-0.9j, 0.9-0.9j], dtype=complex)
        evm_error = calculate_evm(test_symbols1, test_symbols3)
        assert evm_error > 0.0
    
    def test_hex_to_bytes(self):
        """测试十六进制字符串转字节功能"""
        test_hex = '48656c6c6f'  # 'Hello'的十六进制表示
        bytes_data = hex_to_bytes(test_hex)
        assert isinstance(bytes_data, bytes)
        assert bytes_data == b'Hello'
    
    def test_bytes_to_hex(self):
        """测试字节转十六进制字符串功能"""
        test_bytes = b'Hello'
        hex_string = bytes_to_hex(test_bytes)
        assert isinstance(hex_string, str)
        assert hex_string == '48656c6c6f'
    
    def test_get_modulation_order(self):
        """测试获取调制阶数功能"""
        # 测试各种调制类型的阶数
        modulation_types = {
            'bpsk': 1,
            'pi/2-bpsk': 1,
            'qpsk': 2,
            '16qam': 4,
            '64qam': 6,
            '256qam': 8
        }
        
        for mod_type, expected_order in modulation_types.items():
            order = get_modulation_order(mod_type)
            assert order == expected_order
        
        # 测试未知调制类型的默认值
        order_default = get_modulation_order('unknown_modulation')
        assert order_default == 2  # 默认应该是QPSK的阶数

if __name__ == '__main__':
    pytest.main(['-v', __file__])
