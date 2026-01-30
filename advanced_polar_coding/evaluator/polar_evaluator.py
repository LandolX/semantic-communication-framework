import numpy as np
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from advanced_polar_coding.encoder.polar_encoder import PolarEncoder
from advanced_polar_coding.decoder.polar_decoder import SCDecoder, SCLDecoder
from digital_communication_system.py5g_phy_comm.channel import AWGNChannel

class PolarCodeEvaluator:
    """
    Polar码评估器
    """
    def __init__(self):
        """
        初始化评估器
        """
        pass
    
    def evaluate(self, n, k, snr_range, decoder_type='SCL', L=8, num_bits=100000):
        """
        评估Polar码性能
        
        Args:
            n (int): 码长
            k (int): 信息比特长度
            snr_range (numpy.ndarray): SNR范围
            decoder_type (str): 解码器类型，'SC'或'SCL'
            L (int): SCL解码器的列表大小
            num_bits (int): 测试的总比特数
            
        Returns:
            numpy.ndarray: BER结果
        """
        # 创建编码器
        encoder = PolarEncoder(n, k)
        frozen_bits = encoder.frozen_bits
        
        # 创建解码器
        if decoder_type == 'SC':
            decoder = SCDecoder(n, k, frozen_bits)
        else:
            decoder = SCLDecoder(n, k, frozen_bits, L)
        
        ber_results = []
        
        for snr_db in snr_range:
            print(f"测试 P({n},{k}) at SNR: {snr_db:.2f} dB ({decoder_type}, L={L})")
            
            # 创建AWGN信道
            channel = AWGNChannel(snr_dB=snr_db)
            
            total_bits = 0
            error_bits = 0
            
            while total_bits < num_bits:
                # 生成随机信息比特
                info_bits = np.random.randint(0, 2, k, dtype=np.intp)
                
                # 编码
                encoded_bits = encoder.encode(info_bits)
                
                # 调制（BPSK）
                modulated_symbols = 1 - 2 * encoded_bits
                
                # 通过信道
                received_symbols = channel.propagate(modulated_symbols)
                
                # 解码
                decoded_info_bits = decoder.decode(received_symbols)
                
                # 计算误码数
                errors = np.sum(info_bits != decoded_info_bits)
                error_bits += errors
                total_bits += k
                
                # 每处理100个码字打印一次进度
                if total_bits % (k * 100) == 0:
                    print(f"  已处理 {total_bits} 比特, 误码数: {error_bits}")
            
            # 计算BER
            ber = error_bits / total_bits
            ber_results.append(ber)
            print(f"  BER: {ber:.6f}")
        
        return np.array(ber_results)
    
    def plot_results(self, snr_range, ber_results, code_names):
        """
        绘制BER vs SNR曲线
        
        Args:
            snr_range (numpy.ndarray): SNR范围
            ber_results (list): BER结果列表
            code_names (list): 码名称列表
        """
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        
        for i, (ber, name) in enumerate(zip(ber_results, code_names)):
            plt.semilogy(snr_range, ber, '-o', label=name)
        
        plt.xlabel('SNR (dB)')
        plt.ylabel('BER')
        plt.title('Polar码性能评估')
        plt.grid(True, which='both')
        plt.legend()
        plt.tight_layout()
        plt.savefig('polar_code_performance.png')
        plt.show()

if __name__ == "__main__":
    evaluator = PolarCodeEvaluator()
    
    # 测试参数
    snr_range = np.arange(1.0, 3.1, 0.5)
    
    # 测试的码型
    code_params_list = [
        (512, 256),  # P(512,256)
        (1024, 512)   # P(1024,512)
    ]
    
    code_names = [
        'P(512,256) SCL (L=8)',
        'P(1024,512) SCL (L=8)'
    ]
    
    # 评估性能
    ber_results = []
    for n, k in code_params_list:
        ber = evaluator.evaluate(n, k, snr_range, decoder_type='SCL', L=8)
        ber_results.append(ber)
    
    # 绘制结果
    evaluator.plot_results(snr_range, ber_results, code_names)
    
    # 保存结果
    with open('polar_code_evaluation_results.txt', 'w') as f:
        f.write('SNR (dB)\tP(512,256) BER\tP(1024,512) BER\n')
        for i, snr in enumerate(snr_range):
            f.write(f"{snr:.2f}")
            for ber in ber_results:
                f.write(f"\t{ber[i]:.6f}")
            f.write("\n")
    
    print("评估完成，结果已保存")