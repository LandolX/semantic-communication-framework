import numpy as np
import pytest
from py5g_phy_comm.system import CommunicationSystem

class TestCommunicationSystem:
    """测试通信系统模块的功能"""
    
    def test_system_initialization(self):
        """测试通信系统初始化"""
        # 测试默认参数初始化
        system = CommunicationSystem()
        assert system.modulation_type == 'qpsk'
        assert system.snr_dB == 10
        assert system.channel_type == 'awgn'
        assert system.nfft == 1024
        assert system.nsc == 600
        assert system.cp_length == 144
        
        # 测试自定义参数初始化
        system_custom = CommunicationSystem(
            modulation_type='16qam',
            snr_dB=15,
            channel_type='rayleigh',
            nfft=512,
            nsc=300,
            cp_length=72
        )
        assert system_custom.modulation_type == '16qam'
        assert system_custom.snr_dB == 15
        assert system_custom.channel_type == 'rayleigh'
        assert system_custom.nfft == 512
        assert system_custom.nsc == 300
        assert system_custom.cp_length == 72
    
    def test_simple_system_initialization(self):
        """测试简单通信系统初始化"""
        simple_system = CommunicationSystem(use_simple=True)
        assert simple_system.use_simple == True
    
    def test_set_modulation_type(self):
        """测试设置调制类型功能"""
        system = CommunicationSystem()
        
        # 测试更改调制类型
        system.set_modulation_type('16qam')
        assert system.modulation_type == '16qam'
    
    def test_set_snr_dB(self):
        """测试设置SNR功能"""
        system = CommunicationSystem()
        
        # 测试更改SNR
        system.set_snr_dB(15)
        assert system.snr_dB == 15
    
    def test_set_channel_type(self):
        """测试设置信道类型功能"""
        system = CommunicationSystem()
        
        # 测试更改信道类型
        system.set_channel_type('rayleigh')
        assert system.channel_type == 'rayleigh'
        
        # 测试带有参数的信道类型更改
        system.set_channel_type('rician', k_factor=2)
        assert system.channel_type == 'rician'
    
    def test_transmit_receive(self):
        """测试完整的发送接收功能"""
        system = CommunicationSystem(use_simple=True, snr_dB=30)  # 使用高SNR以减少误码
        
        # 测试数据
        test_data = b'Hello, Communication System!'
        
        # 测试完整的发送接收功能
        received_data, error_rate = system.transmit_receive(test_data)
        
        # 验证接收到的数据长度与发送的数据长度相同
        assert len(received_data) == len(test_data)
        
        # 验证误码率是一个浮点数
        assert isinstance(error_rate, float)
        assert 0 <= error_rate <= 1
    
    def test_get_debug_info(self):
        """测试获取调试信息功能"""
        system = CommunicationSystem(use_simple=True)
        
        # 发送一些数据以填充调试信息
        test_data = b'Hello'
        system.transmit_receive(test_data)
        
        # 获取调试信息
        debug_info = system.get_debug_info()
        
        # 验证调试信息包含必要的键
        assert 'system_params' in debug_info
        assert 'transmitter' in debug_info
        assert 'channel' in debug_info
        assert 'receiver' in debug_info
        assert 'results' in debug_info
    
    def test_reset(self):
        """测试系统重置功能"""
        system = CommunicationSystem(modulation_type='16qam', snr_dB=15)
        
        # 发送一些数据
        test_data = b'Hello'
        system.transmit_receive(test_data)
        
        # 重置系统
        system.reset()
        
        # 验证系统参数保持不变
        assert system.modulation_type == '16qam'
        assert system.snr_dB == 15
        
        # 验证结果被重置
        assert system.tx_signal is None
        assert system.channel_output is None
        assert system.rx_signal is None
        assert system.transmitted_data is None
        assert system.received_data is None
        assert system.error_rate is None
    
    
    def test_ber_simulation(self):
        """测试BER仿真功能"""
        system = CommunicationSystem(use_simple=True)
        
        # 运行简短的BER仿真
        snr_range = np.arange(10, 15, 2)  # 只测试几个点以加快测试速度
        snr_values, ber_values = system.run_ber_simulation(
            data_length=10,  # 使用短数据以加快测试速度
            snr_range=snr_range,
            num_trials=2  # 使用少量试验以加快测试速度
        )
        
        # 验证返回的SNR值与输入的SNR范围相同
        assert len(snr_values) == len(snr_range)
        
        # 验证返回的BER值数量与SNR值数量相同
        assert len(ber_values) == len(snr_values)
        
        # 验证所有BER值都是有效的
        assert all(0 <= ber <= 1 for ber in ber_values)

if __name__ == '__main__':
    pytest.main(['-v', __file__])
