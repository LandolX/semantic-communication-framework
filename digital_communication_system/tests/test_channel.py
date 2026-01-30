import numpy as np
import pytest
from py5g_phy_comm.channel import Channel, AWGNChannel, RayleighChannel, RicianChannel, FrequencySelectiveChannel, get_channel

class TestChannel:
    """测试信道模块的功能"""
    
    def test_channel_base_class(self):
        """测试信道基类"""
        channel = Channel()
        
        # 测试设置SNR的功能
        channel.set_snr_dB(10)
        assert channel.snr_dB == 10
        assert channel.snr_linear == 10 ** (10 / 10)
        
        channel.set_snr_linear(10)
        assert channel.snr_linear == 10
        assert np.isclose(channel.snr_dB, 10 * np.log10(10))
    
    def test_awgn_channel(self):
        """测试AWGN信道"""
        channel = AWGNChannel(snr_dB=10)
        
        # 生成测试信号
        test_signal = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        
        # 测试信号通过信道
        output_signal = channel.propagate(test_signal)
        
        # 验证输出信号长度与输入信号相同
        assert len(output_signal) == len(test_signal)
        
        # 测试带信道信息的传播
        output_signal_with_info, channel_info = channel.propagate_with_channel_info(test_signal)
        assert len(output_signal_with_info) == len(test_signal)
        assert isinstance(channel_info, dict)
    
    def test_rayleigh_channel(self):
        """测试瑞利衰落信道"""
        channel = RayleighChannel(snr_dB=10, doppler_frequency=0)
        
        # 生成测试信号
        test_signal = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        
        # 测试信号通过信道
        output_signal = channel.propagate(test_signal)
        
        # 验证输出信号长度与输入信号相同
        assert len(output_signal) == len(test_signal)
        
        # 验证信道增益已生成
        assert channel.channel_gains is not None
        assert len(channel.channel_gains) == len(test_signal)
        
        # 测试带信道信息的传播
        output_signal_with_info, channel_info = channel.propagate_with_channel_info(test_signal)
        assert len(output_signal_with_info) == len(test_signal)
        assert 'channel_gains' in channel_info
    
    def test_rician_channel(self):
        """测试莱斯衰落信道"""
        channel = RicianChannel(snr_dB=10, k_factor=1)
        
        # 生成测试信号
        test_signal = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        
        # 测试信号通过信道
        output_signal = channel.propagate(test_signal)
        
        # 验证输出信号长度与输入信号相同
        assert len(output_signal) == len(test_signal)
        
        # 验证信道增益已生成
        assert channel.channel_gains is not None
        assert len(channel.channel_gains) == len(test_signal)
        
        # 测试带信道信息的传播
        output_signal_with_info, channel_info = channel.propagate_with_channel_info(test_signal)
        assert len(output_signal_with_info) == len(test_signal)
        assert 'channel_gains' in channel_info
    
    def test_frequency_selective_channel(self):
        """测试频率选择性衰落信道"""
        # 使用默认抽头
        channel = FrequencySelectiveChannel(snr_dB=10)
        
        # 生成测试信号
        test_signal = np.array([1+1j, -1+1j, -1-1j, 1-1j, 1+1j, -1+1j], dtype=complex)
        
        # 测试信号通过信道
        output_signal = channel.propagate(test_signal)
        
        # 验证输出信号长度与输入信号相同
        assert len(output_signal) == len(test_signal)
        
        # 验证信道增益已生成
        assert channel.channel_gains is not None
        
        # 测试带信道信息的传播
        output_signal_with_info, channel_info = channel.propagate_with_channel_info(test_signal)
        assert len(output_signal_with_info) == len(test_signal)
        assert 'channel_gains' in channel_info
    
    def test_frequency_selective_channel_custom_taps(self):
        """测试自定义抽头的频率选择性衰落信道"""
        # 使用自定义抽头
        custom_taps = np.array([0.8, 0.4, 0.2], dtype=complex)
        custom_delays = np.array([0, 1, 2])
        
        channel = FrequencySelectiveChannel(snr_dB=10, taps=custom_taps, delays=custom_delays)
        
        # 生成测试信号
        test_signal = np.array([1+1j, -1+1j, -1-1j, 1-1j, 1+1j, -1+1j], dtype=complex)
        
        # 测试信号通过信道
        output_signal = channel.propagate(test_signal)
        
        # 验证输出信号长度与输入信号相同
        assert len(output_signal) == len(test_signal)
    
    def test_get_channel_function(self):
        """测试get_channel函数"""
        # 测试创建AWGN信道
        awgn_channel = get_channel('awgn', snr_dB=10)
        assert isinstance(awgn_channel, AWGNChannel)
        
        # 测试创建瑞利信道
        rayleigh_channel = get_channel('rayleigh', snr_dB=10, doppler_frequency=0)
        assert isinstance(rayleigh_channel, RayleighChannel)
        
        # 测试创建莱斯信道
        rician_channel = get_channel('rician', snr_dB=10, k_factor=1)
        assert isinstance(rician_channel, RicianChannel)
        
        # 测试创建频率选择性信道
        freq_selective_channel = get_channel('frequency_selective', snr_dB=10)
        assert isinstance(freq_selective_channel, FrequencySelectiveChannel)
    
    def test_invalid_channel_type(self):
        """测试无效的信道类型"""
        with pytest.raises(ValueError):
            get_channel('invalid_channel', snr_dB=10)
    
    def test_noise_calculation(self):
        """测试噪声计算"""
        channel = AWGNChannel(snr_dB=10)
        
        # 生成测试信号
        test_signal = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=complex)
        
        # 计算噪声标准差
        noise_std = channel._calculate_noise_std(test_signal)
        assert noise_std > 0
    
    def test_noise_generation(self):
        """测试噪声生成"""
        channel = AWGNChannel(snr_dB=10)
        channel.is_complex = True
        channel.noise_std = 0.1
        
        # 生成噪声
        noise = channel._generate_noise(10)
        assert len(noise) == 10
        assert np.iscomplexobj(noise)
    
    def test_real_signal_propagation(self):
        """测试实信号通过信道"""
        channel = AWGNChannel(snr_dB=10)
        
        # 生成实测试信号
        test_signal = np.array([1.0, -1.0, 0.5, -0.5], dtype=float)
        
        # 测试信号通过信道
        output_signal = channel.propagate(test_signal)
        
        # 验证输出信号长度与输入信号相同
        assert len(output_signal) == len(test_signal)
        assert not np.iscomplexobj(output_signal)

if __name__ == '__main__':
    pytest.main(['-v', __file__])
