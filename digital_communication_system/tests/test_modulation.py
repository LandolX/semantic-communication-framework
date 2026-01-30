import numpy as np
import pytest
from py5g_phy_comm.modulation import Modem, get_modem

class TestModulation:
    """测试调制模块的功能"""
    
    def test_modem_initialization(self):
        """测试调制解调器初始化"""
        # 测试各种调制类型的初始化
        modulation_types = ['bpsk', 'qpsk', '16qam', '64qam', '256qam', 'pi/2-bpsk']
        
        for mod_type in modulation_types:
            modem = Modem(mod_type)
            assert modem.modulation_type == mod_type
            assert hasattr(modem, 'bits_per_symbol')
            assert hasattr(modem, 'normalization')
    
    def test_invalid_modulation_type(self):
        """测试无效调制类型"""
        with pytest.raises(ValueError):
            Modem('invalid_modulation')
    
    def test_modulate_demodulate_bpsk(self):
        """测试BPSK调制解调"""
        modem = Modem('bpsk')
        
        # 测试不同长度的比特流
        test_bits = np.array([0, 1, 0, 1, 1, 0], dtype=int)
        symbols = modem.modulate(test_bits)
        
        # 验证符号数量
        assert len(symbols) == len(test_bits) // modem.bits_per_symbol
        
        # 验证解调功能
        demodulated_bits = modem.demodulate(symbols, 'hard')
        
        # 验证解调后的比特与原始比特相同
        assert np.array_equal(demodulated_bits, test_bits)
    
    def test_modulate_demodulate_qpsk(self):
        """测试QPSK调制解调"""
        modem = Modem('qpsk')
        
        test_bits = np.array([0, 0, 1, 1, 0, 1, 1, 0], dtype=int)
        symbols = modem.modulate(test_bits)
        
        assert len(symbols) == len(test_bits) // modem.bits_per_symbol
        
        demodulated_bits = modem.demodulate(symbols, 'hard')
        assert np.array_equal(demodulated_bits, test_bits)
    
    def test_modulate_demodulate_16qam(self):
        """测试16QAM调制解调"""
        modem = Modem('16qam')
        
        test_bits = np.array([0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0], dtype=int)
        symbols = modem.modulate(test_bits)
        
        assert len(symbols) == len(test_bits) // modem.bits_per_symbol
        
        demodulated_bits = modem.demodulate(symbols, 'hard')
        assert np.array_equal(demodulated_bits, test_bits)
    
    def test_modulate_demodulate_64qam(self):
        """测试64QAM调制解调"""
        modem = Modem('64qam')
        
        # 64QAM需要6位比特 per symbol
        test_bits = np.array([0]*12 + [1]*12, dtype=int)
        symbols = modem.modulate(test_bits)
        
        assert len(symbols) == len(test_bits) // modem.bits_per_symbol
        
        demodulated_bits = modem.demodulate(symbols, 'hard')
        assert np.array_equal(demodulated_bits, test_bits)
    
    def test_modulate_demodulate_256qam(self):
        """测试256QAM调制解调"""
        modem = Modem('256qam')
        
        # 256QAM需要8位比特 per symbol
        test_bits = np.array([0]*16 + [1]*16, dtype=int)
        symbols = modem.modulate(test_bits)
        
        assert len(symbols) == len(test_bits) // modem.bits_per_symbol
        
        demodulated_bits = modem.demodulate(symbols, 'hard')
        assert np.array_equal(demodulated_bits, test_bits)
    
    def test_soft_demodulation(self):
        """测试软解调功能"""
        modem = Modem('qpsk')
        
        test_bits = np.array([0, 0, 1, 1, 0, 1, 1, 0], dtype=int)
        symbols = modem.modulate(test_bits)
        
        # 添加少量噪声以测试软解调
        noise = (np.random.randn(len(symbols)) + 1j * np.random.randn(len(symbols))) * 0.1
        noisy_symbols = symbols + noise
        
        # 测试软解调
        llrs = modem.demodulate(noisy_symbols, 'soft', noise_var=0.01)
        assert len(llrs) == len(test_bits)
    
    def test_soft_demodulation_noise_var(self):
        """测试软解调的噪声方差参数"""
        modem = Modem('qpsk')
        
        test_bits = np.array([0, 0, 1, 1], dtype=int)
        symbols = modem.modulate(test_bits)
        
        # 测试噪声方差为0的情况
        with pytest.raises(ValueError):
            modem.demodulate(symbols, 'soft', noise_var=0)
    
    def test_invalid_demod_type(self):
        """测试无效的解调类型"""
        modem = Modem('qpsk')
        
        test_bits = np.array([0, 0, 1, 1], dtype=int)
        symbols = modem.modulate(test_bits)
        
        with pytest.raises(ValueError):
            modem.demodulate(symbols, 'invalid_type')
    
    def test_get_modem_function(self):
        """测试get_modem函数"""
        modem = get_modem('qpsk')
        assert isinstance(modem, Modem)
        assert modem.modulation_type == 'qpsk'
    
    def test_bit_length_validation(self):
        """测试比特长度验证"""
        modem = Modem('qpsk')  # QPSK需要2位比特 per symbol
        
        # 测试比特长度不是调制符号长度倍数的情况
        test_bits = np.array([0, 1, 0], dtype=int)  # 长度为3，不是2的倍数
        
        with pytest.raises(ValueError):
            modem.modulate(test_bits)
    
    def test_constellation_generation(self):
        """测试星座图生成"""
        modem = Modem('qpsk')
        constellation, constellation_bits = modem._generate_constellation()
        
        # 验证星座点数量
        assert len(constellation) == 2 ** modem.bits_per_symbol
        assert constellation_bits.shape == (len(constellation), modem.bits_per_symbol)
    
    def test_signal_power_calculation(self):
        """测试信号功率计算"""
        from py5g_phy_comm.modulation import signal_power
        
        test_signal = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        power = signal_power(test_signal)
        assert isinstance(power, float)
        assert power > 0

if __name__ == '__main__':
    pytest.main(['-v', __file__])
