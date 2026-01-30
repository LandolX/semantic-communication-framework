import numpy as np
import pytest
from py5g_phy_comm.transmitter import Transmitter, SimpleTransmitter

class TestTransmitter:
    """测试发送器模块的功能"""
    
    def test_transmitter_initialization(self):
        """测试发送器初始化"""
        # 测试默认参数初始化
        transmitter = Transmitter(modulation_type='qpsk')
        assert transmitter.modulation_type == 'qpsk'
        assert transmitter.nfft == 1024
        assert transmitter.nsc == 600
        assert transmitter.cp_length == 144
        
        # 测试自定义参数初始化
        transmitter_custom = Transmitter(modulation_type='16qam', nfft=512, nsc=300, cp_length=72)
        assert transmitter_custom.modulation_type == '16qam'
        assert transmitter_custom.nfft == 512
        assert transmitter_custom.nsc == 300
        assert transmitter_custom.cp_length == 72
    
    def test_simple_transmitter_initialization(self):
        """测试简单发送器初始化"""
        simple_transmitter = SimpleTransmitter(modulation_type='qpsk')
        assert simple_transmitter.modulation_type == 'qpsk'
    
    def test_process_data(self):
        """测试数据处理功能"""
        transmitter = Transmitter(modulation_type='qpsk')
        
        # 测试数据处理
        test_data = b'Hello, World!'
        processed_bits = transmitter.process_data(test_data)
        
        # 验证处理后的比特长度是数据长度的8倍（每个字节8位）
        assert len(processed_bits) == len(test_data) * 8
        
        # 验证处理后的比特是整数类型（包括NumPy整数类型）
        assert all(np.issubdtype(type(bit), np.integer) for bit in processed_bits)
        
        # 验证处理后的比特值只能是0或1
        assert all(bit in [0, 1] for bit in processed_bits)
    
    def test_modulate(self):
        """测试调制功能"""
        transmitter = Transmitter(modulation_type='qpsk')
        
        # 生成测试比特
        test_bits = np.array([0, 0, 1, 1, 0, 1, 1, 0], dtype=int)
        
        # 测试调制功能
        modulated_symbols = transmitter.modulate(test_bits)
        
        # 验证调制后的符号长度是比特长度除以每个符号的比特数
        assert len(modulated_symbols) == len(test_bits) // transmitter.modem.bits_per_symbol
        
        # 验证调制后的符号是复数类型
        assert np.iscomplexobj(modulated_symbols)
    
    def test_ofdm_modulate(self):
        """测试OFDM调制功能"""
        transmitter = Transmitter(modulation_type='qpsk', nfft=16, nsc=8, cp_length=4)
        
        # 生成测试符号
        test_symbols = np.array([1+1j, -1+1j, -1-1j, 1-1j, 1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        
        # 测试OFDM调制功能
        ofdm_signal = transmitter.ofdm_modulate(test_symbols)
        
        # 验证OFDM信号长度大于输入符号长度
        assert len(ofdm_signal) > len(test_symbols)
    
    def test_transmit(self):
        """测试完整发送功能"""
        transmitter = Transmitter(modulation_type='qpsk', nfft=16, nsc=8, cp_length=4)
        
        # 测试数据
        test_data = b'Hello'
        
        # 测试完整发送功能
        tx_signal = transmitter.transmit(test_data)
        
        # 验证发送信号是复数类型
        assert np.iscomplexobj(tx_signal)
        
        # 验证发送信号长度大于0
        assert len(tx_signal) > 0
    
    def test_simple_transmitter_transmit(self):
        """测试简单发送器的发送功能"""
        simple_transmitter = SimpleTransmitter(modulation_type='qpsk')
        
        # 测试数据
        test_data = b'Hello'
        
        # 测试简单发送器的发送功能
        symbols = simple_transmitter.transmit(test_data)
        
        # 验证发送的符号是复数类型
        assert np.iscomplexobj(symbols)
        
        # 验证发送的符号长度大于0
        assert len(symbols) > 0
    
    def test_get_debug_info(self):
        """测试获取调试信息功能"""
        transmitter = Transmitter(modulation_type='qpsk')
        
        # 发送一些数据以填充调试信息
        test_data = b'Hello'
        transmitter.transmit(test_data)
        
        # 获取调试信息
        debug_info = transmitter.get_debug_info()
        
        # 验证调试信息包含必要的键
        assert 'modulation_type' in debug_info
        assert 'nfft' in debug_info
        assert 'nsc' in debug_info
        assert 'cp_length' in debug_info
        assert 'input_bits' in debug_info
        assert 'modulated_symbols' in debug_info
        assert 'tx_signal' in debug_info
        assert 'bits_per_symbol' in debug_info
        
        # 测试简单发送器的调试信息
        simple_transmitter = SimpleTransmitter(modulation_type='qpsk')
        simple_transmitter.transmit(test_data)
        simple_debug_info = simple_transmitter.get_debug_info()
        assert 'modulation_type' in simple_debug_info
        assert 'input_bits' in simple_debug_info
        assert 'modulated_symbols' in simple_debug_info
        assert 'bits_per_symbol' in simple_debug_info
    
    def test_set_modulation_type(self):
        """测试设置调制类型功能"""
        transmitter = Transmitter(modulation_type='qpsk')
        
        # 测试更改调制类型
        transmitter.set_modulation_type('16qam')
        assert transmitter.modulation_type == '16qam'
        
        # 测试简单发送器更改调制类型
        simple_transmitter = SimpleTransmitter(modulation_type='qpsk')
        simple_transmitter.set_modulation_type('16qam')
        assert simple_transmitter.modulation_type == '16qam'
    
    def test_set_ofdm_parameters(self):
        """测试设置OFDM参数功能"""
        transmitter = Transmitter(modulation_type='qpsk', nfft=1024, nsc=600, cp_length=144)
        
        # 测试更改OFDM参数
        transmitter.set_ofdm_parameters(nfft=512, nsc=300, cp_length=72)
        assert transmitter.nfft == 512
        assert transmitter.nsc == 300
        assert transmitter.cp_length == 72

if __name__ == '__main__':
    pytest.main(['-v', __file__])
