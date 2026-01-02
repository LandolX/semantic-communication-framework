import numpy as np

# 直接复制调制函数
# 38.211 5.1 Modulation mapper

def nrSymbolModulate(databits, modulation):
    int_modtype = modulation.lower()

    assert int_modtype in ["pi/2-bpsk", "bpsk", "qpsk", "16qam", "64qam", "256qam"], "modulation type is incorrect"
    assert len(databits) > 0, "length of databits must be greater 0"

    if int_modtype == "bpsk":
        res_arr = np.zeros(len(databits), dtype=(complex))
        for idx, sample in enumerate(databits):
            res_arr[idx] = (1-2*sample) + 1j*(1-2*sample)
        res_arr = [x/np.sqrt(2) for x in res_arr]

    elif int_modtype == "pi/2-bpsk":
        res_arr = np.zeros(len(databits), dtype=(complex))
        for idx, sample in enumerate(databits):
            if idx%2:
                res_arr[idx] = (2*sample-1) + 1j*(1-2*sample)
            else:
                res_arr[idx] = (1-2*sample) + 1j*(1-2*sample)
        res_arr = [x/np.sqrt(2) for x in res_arr]

    elif int_modtype == "qpsk":
        assert not (len(databits) % 2), "length of databits must be multiple of 2"
        res_arr = np.zeros((len(databits)//2), dtype=(complex))
        chunks = np.array_split(databits, len(databits)//2)
        for idx, sample in enumerate(chunks):
            res_arr[idx] = (1-2*sample[0]) + 1j*(1-2*sample[1])
        res_arr = [x/np.sqrt(2) for x in res_arr]

    elif int_modtype == "16qam":
        assert not (len(databits) % 4), "length of databits must be multiple of 4"
        res_arr = np.zeros((len(databits)//4), dtype=(complex))
        chunks = np.array_split(databits, len(databits)//4)
        for idx, sample in enumerate(chunks):
            res_arr[idx] = ( (1-2*sample[0]) * (2-(1-2*sample[2])) ) + 1j*( (1-2*sample[1]) * (2-(1-2*sample[3])) )
        res_arr = [x/np.sqrt(10) for x in res_arr]

    elif int_modtype == "64qam":
        assert not (len(databits) % 6), "length of databits must be multiple of 6"
        res_arr = np.zeros((len(databits)//6), dtype=(complex))
        chunks = np.array_split(databits, len(databits)//6)
        for idx, sample in enumerate(chunks):
            res_arr[idx] = ( (1-2*sample[0]) * (4-(1-2*sample[2]) * (2-(1-2*sample[4]))) ) + 1j*( (1-2*sample[1]) * (4-(1-2*sample[3]) * (2-(1-2*sample[5]))) )
        res_arr = [x/np.sqrt(42) for x in res_arr]

    elif int_modtype == "256qam":
        assert not (len(databits) % 8), "length of databits must be multiple of 8"
        res_arr = np.zeros((len(databits)//8), dtype=(complex))
        chunks = np.array_split(databits, len(databits)//8)
        for idx, sample in enumerate(chunks):
            res_arr[idx] = ( (1-2*sample[0]) * (8-(1-2*sample[2]) * (4-(1-2*sample[4]) * (2-(1-2*sample[6])))) ) + 1j*( (1-2*sample[1]) * (8-(1-2*sample[3]) * (4-(1-2*sample[5]) * (2-(1-2*sample[7])))) )
        res_arr = [x/np.sqrt(170) for x in res_arr]

    return np.array(res_arr)

# 直接复制修复后的解调函数
def nrSymbolDemodulate(input, mod, nVar=1e-10, DecisionType="soft"):
    output = np.empty(0, "float")
    # 将调制方式转换为小写，确保大小写不敏感
    mod_lower = mod.lower()

    for symbol in input:
        if mod_lower == "bpsk":
            output = np.append(output, np.real(symbol) + np.imag(symbol))
        elif mod_lower == "qpsk":
            output = np.append(output, np.real(symbol))
            output = np.append(output, np.imag(symbol))
        elif mod_lower == "16qam":
            output = np.append(output, np.real(symbol))
            output = np.append(output, np.imag(symbol))
            output = np.append(output, -(np.abs(np.real(symbol)) - 2 / np.sqrt(10)))
            output = np.append(output, -(np.abs(np.imag(symbol)) - 2 / np.sqrt(10)))
        elif mod_lower == "64qam":
            # 64QAM解调：每符号6个比特
            # 解调逻辑必须与调制逻辑完全匹配
            # 调制时的公式：( (1-2*b0) * (4-(1-2*b2) * (2-(1-2*b4))) ) + 1j*( (1-2*b1) * (4-(1-2*b3) * (2-(1-2*b5))) )
            # 然后除以sqrt(42)
            
            # 首先，将接收符号乘以归一化因子，恢复原始值
            i_org = np.real(symbol) * np.sqrt(42)
            q_org = np.imag(symbol) * np.sqrt(42)
            
            # 第1个比特：b0，I分量符号位
            # (1-2*b0) 决定符号，所以b0=0时i_org为正，b0=1时i_org为负
            # 软判决值：i_org，正数表示b0=0，负数表示b0=1
            output = np.append(output, i_org)
            
            # 第2个比特：b1，Q分量符号位
            # 软判决值：q_org，正数表示b1=0，负数表示b1=1
            output = np.append(output, q_org)
            
            # 计算I和Q分量的绝对值
            abs_i = np.abs(i_org)
            abs_q = np.abs(q_org)
            
            # 第3个比特：b2，I分量幅度位
            # 调制时I幅度 = 4 - (1-2*b2)*(2 - (1-2*b4))
            # 当b2=0时，(1-2*b2)=1，幅度 = 4 - (2 - (1-2*b4)) = 3 + 2*b4 → 3或1
            # 当b2=1时，(1-2*b2)=-1，幅度 = 4 + (2 - (1-2*b4)) = 5 + 2*b4 → 5或7
            # 软判决值：abs_i - 4，正数表示b2=0，负数表示b2=1
            output = np.append(output, -(abs_i - 4))
            
            # 第4个比特：b3，Q分量幅度位
            # 软判决值：abs_q - 4，正数表示b3=0，负数表示b3=1
            output = np.append(output, -(abs_q - 4))
            
            # 第5个比特：b4，I分量幅度位
            # 当b2=0时，幅度 = 4 - (2 - (1-2*b4)) = 3 - 2*b4 → 3或1
            # 当b2=1时，幅度 = 4 + (2 - (1-2*b4)) = 5 + 2*b4 → 5或7
            # 软判决值：基于b2的判决结果，选择不同的阈值
            if abs_i <= 4:  # b2=0的情况
                # 幅度 = 3 - 2*b4 → 3或1
                # 当b4=0时，幅度=3；当b4=1时，幅度=1
                # 软判决值：abs_i - 2，正数表示b4=0，负数表示b4=1
                output = np.append(output, abs_i - 2)
            else:  # b2=1的情况
                # 幅度 = 5 + 2*b4 → 5或7
                # 当b4=0时，幅度=5；当b4=1时，幅度=7
                # 软判决值：6 - abs_i，正数表示b4=0，负数表示b4=1
                output = np.append(output, 6 - abs_i)
            
            # 第6个比特：b5，Q分量幅度位
            # 与b4类似，基于b3的判决结果，选择不同的阈值
            if abs_q <= 4:  # b3=0的情况
                # 幅度 = 3 - 2*b5 → 3或1
                # 软判决值：abs_q - 2，正数表示b5=0，负数表示b5=1
                output = np.append(output, abs_q - 2)
            else:  # b3=1的情况
                # 幅度 = 5 + 2*b5 → 5或7
                # 软判决值：6 - abs_q，正数表示b5=0，负数表示b5=1
                output = np.append(output, 6 - abs_q)
        elif mod_lower == "256qam":
            # 256QAM解调：每符号8个比特
            I = np.real(symbol) * np.sqrt(170)  # 先乘以归一化因子，恢复原始值
            Q = np.imag(symbol) * np.sqrt(170)
            
            output = np.append(output, I)  # 第1个比特：符号位
            output = np.append(output, Q)  # 第2个比特：符号位
            output = np.append(output, -(np.abs(I) - 6))  # 第3个比特：幅度位
            output = np.append(output, -(np.abs(Q) - 6))  # 第4个比特：幅度位
            output = np.append(output, -(np.abs(np.abs(I) - 2) - 4))  # 第5个比特：幅度位
            output = np.append(output, -(np.abs(np.abs(Q) - 2) - 4))  # 第6个比特：幅度位
            output = np.append(output, -(np.abs(np.abs(np.abs(I) - 4) - 2)))  # 第7个比特：幅度位
            output = np.append(output, -(np.abs(np.abs(np.abs(Q) - 4) - 2)))  # 第8个比特：幅度位

    if DecisionType == "soft":
        output /= nVar / np.exp(1)
        if mod_lower in ["16qam", "64qam", "256qam"]:
            output /= 2
    else:
        output = (output < 0).astype(int)
    return output

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
    
    # 无噪声测试
    print("\n无噪声测试：")
    demodulated_bits_soft_no_noise = nrSymbolDemodulate(modulated_symbols, "64QAM", 1e-20)
    demodulated_bits_hard_no_noise = (demodulated_bits_soft_no_noise < 0).astype(int)
    error_count_no_noise = np.sum(databits != demodulated_bits_hard_no_noise)
    ber_no_noise = error_count_no_noise / num_bits
    print(f"生成比特数: {num_bits}")
    print(f"误码数: {error_count_no_noise}")
    print(f"误码率: {ber_no_noise:.6f}")
    
    if ber_no_noise == 0:
        print("✓ 无噪声测试通过，误码率为0")
    else:
        print("✗ 无噪声测试失败，误码率不为0")
    
    # 添加高斯噪声
    snr_db = 20  # 信噪比20dB
    snr_linear = 10 ** (snr_db / 10)
    signal_power = np.mean(np.abs(modulated_symbols) ** 2)
    noise_power = signal_power / snr_linear
    noise = np.sqrt(noise_power / 2) * (np.random.randn(modulated_symbols.size) + 1j * np.random.randn(modulated_symbols.size))
    noisy_symbols = modulated_symbols + noise
    
    # 64QAM解调
    print(f"\nSNR={snr_db}dB测试：")
    demodulated_bits_soft = nrSymbolDemodulate(noisy_symbols, "64QAM", noise_power)
    demodulated_bits_hard = (demodulated_bits_soft < 0).astype(int)
    
    # 计算误码率
    error_count = np.sum(databits != demodulated_bits_hard)
    ber = error_count / num_bits
    
    print(f"生成比特数: {num_bits}")
    print(f"误码数: {error_count}")
    print(f"误码率: {ber:.6f}")
    
    # 验证误码率是否合理
    if ber < 1e-2:  # 对于20dB SNR，64QAM的误码率应该远低于1e-2
        print("✓ 64QAM调制解调测试通过，误码率在合理范围内")
        return True
    else:
        print("✗ 64QAM调制解调测试失败，误码率过高")
        return False

# 测试不同信噪比下的64QAM误码率
def test_64qam_snr_performance():
    print("\n测试不同信噪比下的64QAM误码率...")
    
    snr_dbs = [15, 20, 25]
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
