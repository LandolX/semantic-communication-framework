import numpy as np
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('..'))

# 导入polar-codes库
from polarcodes import PolarCode
from polarcodes.Construct import Construct
from polarcodes.Encode import Encode
from polarcodes.Decode import Decode
from polarcodes.AWGN import AWGN

# 导入项目中的模块
from digital_communication_system.py5g_phy_comm.channel import AWGNChannel
from digital_communication_system.py5g_phy_comm.modulation import get_modem

class ChannelComparator:
    """
    比较项目自带信道和GitHub库信道的性能差异
    """
    def __init__(self):
        """
        初始化比较器
        """
        # 创建BPSK调制解调器
        self.modem = get_modem('bpsk')
    
    def evaluate_with_project_channel(self, M, K, snr_range, num_bits=100000):
        """
        使用项目自带的AWGNChannel评估性能
        
        Args:
            M (int): 码长
            K (int): 信息比特长度
            snr_range (numpy.ndarray): SNR范围
            num_bits (int): 测试的总比特数
            
        Returns:
            numpy.ndarray: BER结果
        """
        # 创建PolarCode对象
        pc = PolarCode(M, K)
        
        # 构造码
        Construct(pc, 2.0)
        
        print(f"\n=== 使用项目自带信道评估 P({M},{K}) ===")
        
        ber_results = []
        
        for snr_db in snr_range:
            print(f"测试 P({M},{K}) at SNR: {snr_db:.2f} dB")
            
            total_bits = 0
            error_bits = 0
            
            while total_bits < num_bits:
                # 生成随机信息比特
                message = np.random.randint(2, size=K)
                
                # 设置消息
                pc.set_message(message)
                
                # 编码
                Encode(pc)
                
                # 获取码word
                codeword = pc.get_codeword()
                
                # 调制（BPSK）
                modulated_symbols = self.modem.modulate(codeword)
                
                # 创建AWGN信道并传输
                channel = AWGNChannel(snr_dB=snr_db)
                received_symbols = channel.propagate(modulated_symbols)
                
                # 计算LLR
                Eb_No = 10 ** (snr_db / 10)
                noise_variance = 1 / (2 * Eb_No)
                llr = 2 * received_symbols.real / noise_variance
                
                # 设置接收的LLR
                pc.likelihoods = llr
                
                # 解码
                Decode(pc)
                
                # 计算误码数
                errors = np.sum(message != pc.message_received)
                error_bits += errors
                total_bits += K
            
            # 计算BER
            ber = error_bits / total_bits
            ber_results.append(ber)
            print(f"  BER: {ber:.6f}")
        
        return np.array(ber_results)
    
    def evaluate_with_github_channel(self, M, K, snr_range, num_bits=100000):
        """
        使用GitHub库的AWGN评估性能
        
        Args:
            M (int): 码长
            K (int): 信息比特长度
            snr_range (numpy.ndarray): SNR范围
            num_bits (int): 测试的总比特数
            
        Returns:
            numpy.ndarray: BER结果
        """
        # 创建PolarCode对象
        pc = PolarCode(M, K)
        
        # 构造码
        Construct(pc, 2.0)
        
        print(f"\n=== 使用GitHub库信道评估 P({M},{K}) ===")
        
        ber_results = []
        
        for snr_db in snr_range:
            print(f"测试 P({M},{K}) at SNR: {snr_db:.2f} dB")
            
            total_bits = 0
            error_bits = 0
            
            while total_bits < num_bits:
                # 生成随机信息比特
                message = np.random.randint(2, size=K)
                
                # 设置消息
                pc.set_message(message)
                
                # 编码
                Encode(pc)
                
                # 使用GitHub库的AWGN信道
                # 注意：GitHub库的AWGN会自动处理调制和噪声添加
                Eb_No = 10 ** (snr_db / 10)
                
                # 创建AWGN对象
                awgn = AWGN(pc, snr_db)
                
                # 解码
                Decode(pc)
                
                # 计算误码数
                errors = np.sum(message != pc.message_received)
                error_bits += errors
                total_bits += K
            
            # 计算BER
            ber = error_bits / total_bits
            ber_results.append(ber)
            print(f"  BER: {ber:.6f}")
        
        return np.array(ber_results)
    
    def plot_comparison(self, snr_range, project_ber, github_ber, code_name):
        """
        绘制两种信道实现的性能对比图
        
        Args:
            snr_range (numpy.ndarray): SNR范围
            project_ber (numpy.ndarray): 项目信道的BER结果
            github_ber (numpy.ndarray): GitHub信道的BER结果
            code_name (str): 码名称
        """
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        
        plt.semilogy(snr_range, project_ber, '-o', label=f'{code_name} (Project Channel)')
        plt.semilogy(snr_range, github_ber, '-s', label=f'{code_name} (GitHub Channel)')
        
        plt.xlabel('SNR (dB)')
        plt.ylabel('BER')
        plt.title(f'Channel Implementation Comparison for {code_name}')
        plt.grid(True, which='both')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'channel_comparison_{code_name.replace("(", "").replace(")", "").replace(",", "_")}.png')
        plt.show()

if __name__ == "__main__":
    comparator = ChannelComparator()
    
    # 测试参数
    snr_range = np.arange(0.0, 3.1, 1.0)  # 使用更大的步长以加快测试
    
    # 测试的码型
    code_params_list = [
        (512, 256),  # P(512,256)
    ]
    
    for M, K in code_params_list:
        code_name = f'P({M},{K})'
        
        # 使用项目自带信道评估
        project_ber = comparator.evaluate_with_project_channel(M, K, snr_range, num_bits=50000)  # 减少测试比特数以加快速度
        
        # 使用GitHub库信道评估
        github_ber = comparator.evaluate_with_github_channel(M, K, snr_range, num_bits=50000)
        
        # 绘制对比图
        comparator.plot_comparison(snr_range, project_ber, github_ber, code_name)
        
        # 计算差异
        print(f"\n=== 信道实现差异分析 ({code_name}) ===")
        for i, snr in enumerate(snr_range):
            diff = abs(project_ber[i] - github_ber[i])
            print(f"SNR: {snr:.1f} dB - 差异: {diff:.6f} (Project: {project_ber[i]:.6f}, GitHub: {github_ber[i]:.6f})")
    
    print("\n信道对比评估完成")
