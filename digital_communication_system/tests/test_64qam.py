import numpy as np
import sys
import os

# 添加项目路径到系统路径
sys.path.append('/Users/landolx/project/programming/python/py3gpp-master')
# 直接导入调制解调函数，避免导入scipy依赖
from py3gpp.nrSymbolModulate import nrSymbolModulate
from py3gpp.nrSymbolDemodulate import nrSymbolDemodulate

# 测试64QAM调制解调
def test_64qam_modulation_demodulation():
    print("测试64QAM调制解调...")
    
    # 生成随机比特流
    num_bits = 100000  # 10万比特
    databits = np.random.randint(0, 2, num_bits, dtype=int)
    
    # 确保比特数是6的倍数
    num_bits = num_bits - (num_bits % 6)
    databits = databits[:num_bits]
    
    # 64QAM调制
    modulated_symbols = nrSymbolModulate(databits, "64QAM")
    
    # 添加高斯噪声
    snr_db = 20  # 信噪比20dB
    snr_linear = 10 ** (snr_db / 10)
    signal_power = np.mean(np.abs(modulated_symbols) ** 2)
    noise_power = signal_power / snr_linear
    noise = np.sqrt(noise_power / 2) * (np.random.randn(modulated_symbols.size) + 1j * np.random.randn(modulated_symbols.size))
    noisy_symbols = modulated_symbols + noise
    
    # 64QAM解调
    demodulated_bits_soft = nrSymbolDemodulate(noisy_symbols, "64QAM", noise_power)
    demodulated_bits_hard = (demodulated_bits_soft < 0).astype(int)
    
    # 计算误码率
    error_count = np.sum(databits != demodulated_bits_hard)
    ber = error_count / num_bits
    
    print(f"生成比特数: {num_bits}")
    print(f"误码数: {error_count}")
    print(f"误码率: {ber:.6f}")
    
    # 验证误码率是否合理
    if ber < 1e-3:  # 对于20dB SNR，64QAM的误码率应该远低于1e-3
        print("✓ 64QAM调制解调测试通过，误码率在合理范围内")
        return True
    else:
        print("✗ 64QAM调制解调测试失败，误码率过高")
        return False

# 测试不同信噪比下的64QAM误码率
def test_64qam_snr_performance():
    print("\n测试不同信噪比下的64QAM误码率...")
    
    snr_dbs = [10, 15, 20, 25]
    num_bits = 50000
    
    for snr_db in snr_dbs:
        # 生成随机比特流
        databits = np.random.randint(0, 2, num_bits, dtype=int)
        num_bits_adjusted = num_bits - (num_bits % 6)
        databits = databits[:num_bits_adjusted]
        
        # 调制
        modulated_symbols = nrSymbolModulate(databits, "64QAM")
        
        # 添加噪声
        snr_linear = 10 ** (snr_db / 10)
        signal_power = np.mean(np.abs(modulated_symbols) ** 2)
        noise_power = signal_power / snr_linear
        noise = np.sqrt(noise_power / 2) * (np.random.randn(modulated_symbols.size) + 1j * np.random.randn(modulated_symbols.size))
        noisy_symbols = modulated_symbols + noise
        
        # 解调
        demodulated_bits_soft = nrSymbolDemodulate(noisy_symbols, "64QAM", noise_power)
        demodulated_bits_hard = (demodulated_bits_soft < 0).astype(int)
        
        # 计算误码率
        error_count = np.sum(databits != demodulated_bits_hard)
        ber = error_count / num_bits_adjusted
        
        print(f"SNR: {snr_db}dB, 误码率: {ber:.6f}")

if __name__ == "__main__":
    test_64qam_modulation_demodulation()
    test_64qam_snr_performance()
