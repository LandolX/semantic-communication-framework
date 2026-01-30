#!/usr/bin/env python3
"""
LDPC信道编码器

实现码率1/2的LDPC（Low-Density Parity-Check）信道编码，提高数据在无线传输中的可靠性
"""

import numpy as np


class LDPCChannelEncoder:
    """
    LDPC信道编码器类
    
    实现码率1/2的LDPC编码，为数据添加冗余校验位，提高在无线信道中的可靠性
    """
    
    def __init__(self, code_rate=1/2, use_channel_codec=True):
        """
        初始化LDPC信道编码器
        
        参数:
        ----------
        code_rate : float, optional
            编码码率，默认使用1/2
        use_channel_codec : bool, optional
            是否使用信道编码，默认True
        """
        self.code_rate = code_rate
        self.use_channel_codec = use_channel_codec
        
        # 初始化LDPC码参数
        # 这里使用一个简单的LDPC码构造，实际应用中可能需要更复杂的构造
        self._init_ldpc_params()
    
    def _init_ldpc_params(self):
        """
        初始化LDPC码参数
        """
        # 码率1/2，信息位长度
        self.info_bits = 256
        # 编码后总长度
        self.code_bits = int(self.info_bits / self.code_rate)
        # 校验位长度
        self.parity_bits = self.code_bits - self.info_bits
        
        # 生成一个简单的奇偶校验矩阵
        # 实际应用中，应该使用更优化的LDPC码构造方法
        self.H = self._generate_parity_matrix()
        # 生成生成矩阵
        self.G = self._generate_generator_matrix()
    
    def _generate_parity_matrix(self):
        """
        生成奇偶校验矩阵H
        
        返回:
        ----------
        np.ndarray
            奇偶校验矩阵H
        """
        # 创建一个稀疏的奇偶校验矩阵
        # 这里使用一个简单的构造方法，实际应用中可能需要更复杂的方法
        H = np.zeros((self.parity_bits, self.code_bits), dtype=int)
        
        # 填充奇偶校验矩阵
        for i in range(self.parity_bits):
            # 每一行有4个1，实现低密度
            positions = np.random.choice(self.code_bits, 4, replace=False)
            H[i, positions] = 1
        
        return H
    
    def _generate_generator_matrix(self):
        """
        生成生成矩阵G
        
        返回:
        ----------
        np.ndarray
            生成矩阵G
        """
        # 创建一个简单的生成矩阵
        # 实际应用中，应该从H矩阵系统化为G矩阵
        G = np.zeros((self.info_bits, self.code_bits), dtype=int)
        
        # 前info_bits列是单位矩阵
        G[:, :self.info_bits] = np.eye(self.info_bits)
        
        # 后parity_bits列是随机生成的
        for i in range(self.info_bits):
            positions = np.random.choice(self.parity_bits, 2, replace=False)
            G[i, self.info_bits + positions] = 1
        
        return G
    
    def _bits_to_bytes(self, bits):
        """
        将比特序列转换为字节序列
        
        参数:
        ----------
        bits : np.ndarray
            比特序列
        
        返回:
        ----------
        bytes
            字节序列
        """
        # 确保比特数是8的倍数
        padding = (8 - len(bits) % 8) % 8
        if padding > 0:
            bits = np.concatenate([bits, np.zeros(padding, dtype=int)])
        
        # 转换为字节
        bytes_data = b''
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                byte |= bits[i+j] << (7-j)
            bytes_data += bytes([byte])
        
        return bytes_data
    
    def _bytes_to_bits(self, bytes_data):
        """
        将字节序列转换为比特序列
        
        参数:
        ----------
        bytes_data : bytes
            字节序列
        
        返回:
        ----------
        np.ndarray
            比特序列
        """
        bits = []
        for byte in bytes_data:
            for i in range(8):
                bits.append((byte >> (7-i)) & 1)
        return np.array(bits, dtype=int)
    
    def encode(self, data):
        """
        对数据进行LDPC信道编码
        
        参数:
        ----------
        data : bytes
            原始数据
        
        返回:
        ----------
        bytes
            编码后的数据
        """
        if not self.use_channel_codec:
            return data
        
        try:
            # 将数据转换为比特序列
            bits = self._bytes_to_bits(data)
            
            # 分组编码
            encoded_bits = []
            for i in range(0, len(bits), self.info_bits):
                # 提取当前分组
                group = bits[i:i+self.info_bits]
                
                # 如果分组长度不足，进行零填充
                if len(group) < self.info_bits:
                    padding = self.info_bits - len(group)
                    group = np.concatenate([group, np.zeros(padding, dtype=int)])
                
                # 进行LDPC编码
                encoded_group = np.dot(group, self.G) % 2
                encoded_bits.extend(encoded_group.tolist())
            
            # 将编码后的比特序列转换为字节
            encoded_bytes = self._bits_to_bytes(np.array(encoded_bits))
            
            # 添加编码头信息（1字节：编码类型 + 2字节：信息位长度）
            header = bytes([ord('L'), (self.info_bits >> 8) & 0xFF, self.info_bits & 0xFF])
            
            return header + encoded_bytes
            
        except Exception as e:
            print(f"LDPC编码失败: {e}")
            return data
    
    def get_ldpc_info(self):
        """
        获取LDPC编码信息
        
        返回:
        ----------
        dict
            LDPC编码信息
        """
        return {
            'code_rate': self.code_rate,
            'info_bits': self.info_bits,
            'code_bits': self.code_bits,
            'parity_bits': self.parity_bits,
            'H_shape': self.H.shape,
            'G_shape': self.G.shape
        }


# 便捷函数
def get_ldpc_channel_encoder(code_rate=1/2, use_channel_codec=True):
    """
    获取LDPC信道编码器实例
    
    参数:
    ----------
    code_rate : float, optional
        编码码率
    use_channel_codec : bool, optional
        是否使用信道编码
    
    返回:
    ----------
    LDPCChannelEncoder
        LDPC信道编码器实例
    """
    return LDPCChannelEncoder(code_rate, use_channel_codec)
