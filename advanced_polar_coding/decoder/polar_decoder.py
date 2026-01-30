import numpy as np

class PolarDecoder:
    """
    Polar码解码器基类
    """
    def __init__(self, n, k, frozen_bits):
        """
        初始化Polar码解码器
        
        Args:
            n (int): 码长
            k (int): 信息比特长度
            frozen_bits (list): 冻结比特位置列表
        """
        self.n = n
        self.k = k
        self.frozen_bits = frozen_bits
        self.info_bits = [i for i in range(n) if i not in frozen_bits]
        self.N = int(np.log2(n))
    
    def decode(self, received_symbols):
        """
        解码接口
        
        Args:
            received_symbols (numpy.ndarray): 接收的符号
            
        Returns:
            numpy.ndarray: 解码后的信息比特
        """
        raise NotImplementedError("子类必须实现decode方法")
    
    def get_info_bits(self, decoded_bits):
        """
        从解码结果中提取信息比特
        
        Args:
            decoded_bits (numpy.ndarray): 解码后的所有比特
            
        Returns:
            numpy.ndarray: 提取的信息比特
        """
        return np.array([decoded_bits[i] for i in self.info_bits])
    
    def _bit_reverse(self, index, n_bits):
        """
        比特反转
        
        Args:
            index (int): 原始索引
            n_bits (int): 比特位数
            
        Returns:
            int: 反转后的索引
        """
        binary = bin(index)[2:].zfill(n_bits)
        reversed_binary = binary[::-1]
        return int(reversed_binary, 2)

class SCDecoder(PolarDecoder):
    """
    SC解码器
    """
    def __init__(self, n, k, frozen_bits):
        """
        初始化SC解码器
        
        Args:
            n (int): 码长
            k (int): 信息比特长度
            frozen_bits (list): 冻结比特位置列表
        """
        super().__init__(n, k, frozen_bits)
    
    def decode(self, received_symbols):
        """
        使用SC算法解码
        
        Args:
            received_symbols (numpy.ndarray): 接收的符号
            
        Returns:
            numpy.ndarray: 解码后的信息比特
        """
        # 计算LLR
        llrs = 2 * received_symbols  # BPSK调制
        
        # 执行SC解码
        decoded_bits = self._sc_decode(llrs)
        
        # 提取信息比特
        return self.get_info_bits(decoded_bits)
    
    def _sc_decode(self, llrs):
        """
        SC解码核心算法
        
        Args:
            llrs (numpy.ndarray): 接收符号的LLR
            
        Returns:
            numpy.ndarray: 解码后的比特
        """
        n = len(llrs)
        decoded_bits = np.zeros(n, dtype=np.intp)
        
        # 按照比特反转顺序处理每个比特位置
        for i in range(n):
            # 计算比特反转后的位置
            bit_rev_pos = self._bit_reverse(i, self.N)
            
            # 判决
            if bit_rev_pos in self.frozen_bits:
                decoded_bits[bit_rev_pos] = 0
            else:
                decoded_bits[bit_rev_pos] = 0 if llrs[bit_rev_pos] >= 0 else 1
        
        return decoded_bits

class SCLDecoder(PolarDecoder):
    """
    SCL解码器
    """
    def __init__(self, n, k, frozen_bits, L=8):
        """
        初始化SCL解码器
        
        Args:
            n (int): 码长
            k (int): 信息比特长度
            frozen_bits (list): 冻结比特位置列表
            L (int): 列表大小
        """
        super().__init__(n, k, frozen_bits)
        self.L = L
    
    def decode(self, received_symbols):
        """
        使用SCL算法解码
        
        Args:
            received_symbols (numpy.ndarray): 接收的符号
            
        Returns:
            numpy.ndarray: 解码后的信息比特
        """
        # 计算LLR
        llrs = 2 * received_symbols  # BPSK调制
        
        # 执行SCL解码
        decoded_bits = self._scl_decode(llrs)
        
        # 提取信息比特
        return self.get_info_bits(decoded_bits)
    
    def _scl_decode(self, llrs):
        """
        SCL解码核心算法
        
        Args:
            llrs (numpy.ndarray): 接收符号的LLR
            
        Returns:
            numpy.ndarray: 解码后的比特
        """
        n = len(llrs)
        
        # 初始化路径列表
        paths = [{'bits': np.zeros(n, dtype=np.intp), 'metric': 0.0}]
        
        # 按照比特反转顺序处理每个比特位置
        for i in range(n):
            # 计算比特反转后的位置
            bit_rev_pos = self._bit_reverse(i, self.N)
            
            # 扩展路径
            new_paths = []
            
            for path in paths:
                # 计算当前比特的LLR
                current_llr = llrs[bit_rev_pos]
                
                if bit_rev_pos in self.frozen_bits:
                    # 冻结比特固定为0
                    new_bit = 0
                    new_metric = path['metric'] + (0 if current_llr >= 0 else abs(current_llr))
                    new_bits = path['bits'].copy()
                    new_bits[bit_rev_pos] = new_bit
                    new_paths.append({'bits': new_bits, 'metric': new_metric})
                else:
                    # 信息比特，尝试0和1两种可能
                    for bit in [0, 1]:
                        new_metric = path['metric'] + (0 if (bit == 0 and current_llr >= 0) or (bit == 1 and current_llr < 0) else abs(current_llr))
                        new_bits = path['bits'].copy()
                        new_bits[bit_rev_pos] = bit
                        new_paths.append({'bits': new_bits, 'metric': new_metric})
            
            # 按度量值排序并保留前L条路径
            new_paths.sort(key=lambda x: x['metric'])
            paths = new_paths[:self.L]
        
        # 选择度量值最小的路径
        best_path = min(paths, key=lambda x: x['metric'])
        
        return best_path['bits']