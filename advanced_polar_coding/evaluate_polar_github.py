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

class PolarCodeGitHubEvaluator:
    """
    使用GitHub上的polar-codes库评估Polar码性能
    """
    def __init__(self):
        """
        初始化评估器
        """
        pass
    
    def evaluate(self, M, K, snr_range, construction_SNR=2.0, num_bits=100000):
        """
        评估Polar码性能
        
        Args:
            M (int): 码长
            K (int): 信息比特长度
            snr_range (numpy.ndarray): SNR范围
            construction_SNR (float): 构造时使用的SNR
            num_bits (int): 测试的总比特数
            
        Returns:
            numpy.ndarray: BER结果
        """
        # 创建PolarCode对象
        pc = PolarCode(M, K)
        
        # 构造码
        Construct(pc, construction_SNR)
        
        print(f"构造 P({M},{K}) 完成")
        print(f"冻结比特位置: {pc.frozen}")
        print(f"可靠性顺序: {pc.reliabilities}")
        
        # 创建BPSK调制解调器
        modem = get_modem('bpsk')
        
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
                modulated_symbols = modem.modulate(codeword)
                
                # 创建AWGN信道并传输
                channel = AWGNChannel(snr_dB=snr_db)
                received_symbols = channel.propagate(modulated_symbols)
                
                # 计算LLR
                # 对于BPSK，LLR = 2 * received_symbols.real / noise_variance
                # 但我们可以直接使用接收符号的实部，因为BPSK是实数调制
                
                # 使用库的AWGN方法获取LLR
                # 首先计算Eb/No
                Eb_No = 10 ** (snr_db / 10)
                
                # 计算噪声方差
                # 对于BPSK，每个符号携带1比特信息
                # Es = Eb * 1
                noise_variance = 1 / (2 * Eb_No)
                
                # 计算LLR
                llr = 2 * received_symbols.real / noise_variance
                
                # 设置接收的LLR - 注意：GitHub库使用likelihoods属性
                pc.likelihoods = llr
                
                # 解码
                Decode(pc)
                
                # 计算误码数
                errors = np.sum(message != pc.message_received)
                error_bits += errors
                total_bits += K
                
                # 每处理100个码字打印一次进度
                if total_bits % (K * 100) == 0:
                    print(f"  已处理 {total_bits} 比特, 误码数: {error_bits}")
            
            # 计算BER
            ber = error_bits / total_bits
            ber_results.append(ber)
            print(f"  BER: {ber:.6f}")
        
        return np.array(ber_results)
    
    def plot_results(self, snr_range, ber_results, code_names):
        """
        Plot BER vs SNR curves
        
        Args:
            snr_range (numpy.ndarray): SNR range
            ber_results (list): BER results list
            code_names (list): Code names list
        """
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        
        for i, (ber, name) in enumerate(zip(ber_results, code_names)):
            plt.semilogy(snr_range, ber, '-o', label=name)
        
        plt.xlabel('SNR (dB)')
        plt.ylabel('BER')
        plt.title('Polar Code Performance Evaluation (GitHub Library)')
        plt.grid(True, which='both')
        plt.legend()
        plt.tight_layout()
        plt.savefig('polar_code_performance_github.png')
        plt.show()

if __name__ == "__main__":
    evaluator = PolarCodeGitHubEvaluator()
    
    # Test parameters
    snr_range = np.arange(0.0, 5.1, 0.5)
    
    # Test codes
    code_params_list = [
        (512, 256),  # P(512,256)
        (1024, 512)   # P(1024,512)
    ]
    
    code_names = [
        'P(512,256) (GitHub Library)',
        'P(1024,512) (GitHub Library)'
    ]
    
    # Evaluate performance
    ber_results = []
    for M, K in code_params_list:
        ber = evaluator.evaluate(M, K, snr_range, construction_SNR=2.0)
        ber_results.append(ber)
    
    # Plot results
    evaluator.plot_results(snr_range, ber_results, code_names)
    
    # Save results
    with open('polar_code_evaluation_results_github.txt', 'w') as f:
        f.write('SNR (dB)\tP(512,256) BER\tP(1024,512) BER\n')
        for i, snr in enumerate(snr_range):
            f.write(f"{snr:.2f}")
            for ber in ber_results:
                f.write(f"\t{ber[i]:.6f}")
            f.write("\n")
    
    print("Evaluation completed, results saved")