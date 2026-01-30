import numpy as np

class PolarEncoder:
    """
    Polar码编码器
    """
    def __init__(self, n, k):
        """
        初始化Polar码编码器
        
        Args:
            n (int): 码长，必须是2的幂
            k (int): 信息比特长度
        """
        if not (n & (n - 1) == 0):
            raise ValueError("码长n必须是2的幂")
        if k > n:
            raise ValueError("信息比特长度k不能大于码长n")
        
        self.n = n
        self.k = k
        self.N = int(np.log2(n))
        self.info_bits = self._select_info_bits()
        self.frozen_bits = [i for i in range(n) if i not in self.info_bits]
    
    def _select_info_bits(self):
        """
        选择信息比特位置
        """
        if self.n == 512:
            # P(512,256) - 信息比特位置
            return [i for i in range(256, 512)]
        elif self.n == 1024:
            # P(1024,512) - 信息比特位置
            return [i for i in range(512, 1024)]
        else:
            # 对于其他码长，选择可靠性较高的位置
            reliabilities = self._compute_reliabilities()
            sorted_indices = np.argsort(reliabilities)[::-1]
            return sorted_indices[:self.k].tolist()
    
    def _compute_reliabilities(self):
        """
        计算比特位置的可靠性
        """
        reliabilities = np.zeros(self.n)
        for i in range(self.n):
            ones_count = bin(i).count('1')
            reliabilities[i] = ones_count
        return reliabilities
    
    def encode(self, info_bits):
        """
        编码
        
        Args:
            info_bits (numpy.ndarray): 信息比特
            
        Returns:
            numpy.ndarray: 编码后的码字
        """
        if len(info_bits) != self.k:
            raise ValueError(f"信息比特长度必须为{self.k}")
        
        # 构造完整的码字序列u
        u = np.zeros(self.n, dtype=np.intp)
        for i, bit in enumerate(info_bits):
            u[self.info_bits[i]] = bit
        
        # 执行Polar变换得到编码后的码字x
        x = self._polar_transform(u)
        
        return x
    
    def _polar_transform(self, u):
        """
        Polar变换
        """
        n = len(u)
        if n == 1:
            return u
        
        half = n // 2
        u1 = u[:half]
        u2 = u[half:]
        
        x1 = self._polar_transform(u1 ^ u2)
        x2 = self._polar_transform(u2)
        
        return np.concatenate([x1, x2])
    
    def get_code_parameters(self):
        """
        获取码参数
        
        Returns:
            dict: 码参数
        """
        return {
            'n': self.n,
            'k': self.k,
            'N': self.N,
            'frozen_bits': self.frozen_bits,
            'info_bits': self.info_bits
        }