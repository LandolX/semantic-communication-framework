import numpy as np
import pytest
from py5g_phy_comm.receiver import Receiver, SimpleReceiver
from py5g_phy_comm.modulation import Modem

class TestReceiver:
    """测试接收器模块的功能"""
    
    def test_receiver_initialization(self):
        """测试接收器初始化"""
        # 测试默认参数初始化
        receiver = Receiver(modulation_type='qpsk')
        assert receiver.modulation_type == 'qpsk'
        assert receiver.nfft == 1024
        assert receiver.nsc == 600
        assert receiver.cp_length == 144
        
        # 测试自定义参数初始化
        receiver_custom = Receiver(modulation_type='16qam', nfft=512, nsc=300, cp_length=72)
        assert receiver_custom.modulation_type == '16qam'
        assert receiver_custom.nfft == 512
        assert receiver_custom.nsc == 300
        assert receiver_custom.cp_length == 72
    
    def test_simple_receiver_initialization(self):
        """测试简单接收器初始化"""
        simple_receiver = SimpleReceiver(modulation_type='qpsk')
        assert simple_receiver.modulation_type == 'qpsk'
    
    def test_equalize_function(self):
        """测试均衡功能"""
        receiver = Receiver(modulation_type='qpsk')
        
        # 生成测试符号
        test_symbols = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        
        # 生成测试信道增益
        test_channel_gains = np.array([0.9+0.1j, 0.8-0.2j, 0.7+0.3j, 0.6-0.4j], dtype=complex)
        
        # 测试均衡功能
        equalized_symbols = receiver.equalize(test_symbols, test_channel_gains)
        
        # 验证均衡后的符号长度与输入符号相同
        assert len(equalized_symbols) == len(test_symbols)
        
        # 测试无信道增益的情况
        equalized_symbols_no_gain = receiver.equalize(test_symbols, None)
        assert np.array_equal(equalized_symbols_no_gain, test_symbols)
        
        # 测试空信道增益的情况
        equalized_symbols_empty_gain = receiver.equalize(test_symbols, [])
        assert np.array_equal(equalized_symbols_empty_gain, test_symbols)
    
    def test_ofdm_demodulate(self):
        """测试OFDM解调功能"""
        receiver = Receiver(modulation_type='qpsk', nfft=16, nsc=8, cp_length=4)
        
        # 生成测试接收信号（OFDM符号 + 循环前缀）
        # 这里使用简化的测试信号，实际OFDM信号会更复杂
        test_signal = np.zeros(20, dtype=complex)  # 1个OFDM符号，长度为16+4=20
        
        # 测试OFDM解调
        demodulated_symbols = receiver.ofdm_demodulate(test_signal)
        
        # 验证解调后的符号数量
        assert len(demodulated_symbols) > 0
    
    def test_demodulate(self):
        """测试解调功能"""
        receiver = Receiver(modulation_type='qpsk')
        
        # 生成测试符号
        modem = Modem('qpsk')
        test_bits = np.array([0, 0, 1, 1, 0, 1, 1, 0], dtype=int)
        test_symbols = modem.modulate(test_bits)
        
        # 测试硬解调
        demodulated_bits = receiver.demodulate(test_symbols, 'hard')
        assert len(demodulated_bits) == len(test_bits)
        
        # 测试软解调
        llrs = receiver.demodulate(test_symbols, 'soft', noise_var=0.01)
        assert len(llrs) == len(test_bits)
    
    def test_recover_data(self):
        """测试数据恢复功能"""
        receiver = Receiver(modulation_type='qpsk')
        
        # 生成测试比特
        test_bits = np.array([0, 1, 0, 1, 1, 0, 0, 1], dtype=int)  # 8位比特，正好1字节
        
        # 测试数据恢复
        recovered_data = receiver.recover_data(test_bits)
        assert isinstance(recovered_data, bytes)
        assert len(recovered_data) == 1
        
        # 测试指定原始长度的情况
        recovered_data_with_length = receiver.recover_data(test_bits, original_length=1)
        assert isinstance(recovered_data_with_length, bytes)
        assert len(recovered_data_with_length) == 1
    
    def test_receive_function(self):
        """测试完整接收功能"""
        receiver = Receiver(modulation_type='qpsk', nfft=16, nsc=8, cp_length=4)
        
        # 生成测试接收信号
        test_signal = np.zeros(20, dtype=complex)  # 1个OFDM符号
        
        # 测试完整接收功能
        recovered_data = receiver.receive(test_signal, original_length=1)
        assert isinstance(recovered_data, bytes)
    
    def test_simple_receiver_receive(self):
        """测试简单接收器的接收功能"""
        simple_receiver = SimpleReceiver(modulation_type='qpsk')
        
        # 生成测试符号
        modem = Modem('qpsk')
        test_bits = np.array([0, 0, 1, 1, 0, 1, 1, 0], dtype=int)
        test_symbols = modem.modulate(test_bits)
        
        # 测试简单接收器的接收功能
        recovered_data = simple_receiver.receive(test_symbols, original_length=1)
        assert isinstance(recovered_data, bytes)
    
    def test_get_debug_info(self):
        """测试获取调试信息功能"""
        receiver = Receiver(modulation_type='qpsk')
        debug_info = receiver.get_debug_info()
        
        # 验证调试信息包含必要的键
        assert 'modulation_type' in debug_info
        assert 'nfft' in debug_info
        assert 'nsc' in debug_info
        assert 'cp_length' in debug_info
        assert 'bits_per_symbol' in debug_info
        
        # 测试简单接收器的调试信息
        simple_receiver = SimpleReceiver(modulation_type='qpsk')
        simple_debug_info = simple_receiver.get_debug_info()
        assert 'modulation_type' in simple_debug_info
        assert 'bits_per_symbol' in simple_debug_info
    
    def test_set_modulation_type(self):
        """测试设置调制类型功能"""
        receiver = Receiver(modulation_type='qpsk')
        
        # 测试更改调制类型
        receiver.set_modulation_type('16qam')
        assert receiver.modulation_type == '16qam'
        
        # 测试简单接收器更改调制类型
        simple_receiver = SimpleReceiver(modulation_type='qpsk')
        simple_receiver.set_modulation_type('16qam')
        assert simple_receiver.modulation_type == '16qam'
    
    def test_set_ofdm_parameters(self):
        """测试设置OFDM参数功能"""
        receiver = Receiver(modulation_type='qpsk', nfft=1024, nsc=600, cp_length=144)
        
        # 测试更改OFDM参数
        receiver.set_ofdm_parameters(nfft=512, nsc=300, cp_length=72)
        assert receiver.nfft == 512
        assert receiver.nsc == 300
        assert receiver.cp_length == 72

if __name__ == '__main__':
    pytest.main(['-v', __file__])
