#!/usr/bin/env python3
"""
极化码信道编码器

使用极化码（Polar Code）编码提高数据可靠性，为数据添加冗余校验位
"""

import numpy as np
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('../../../../'))

# 使用本地复制的polar codes实现
from polarcodes import PolarCode
from polarcodes.Construct import Construct
from polarcodes.Encode import Encode


class PolarEncoder:
    """
    极化码信道编码器类
    
    实现极化码编码，为数据添加冗余校验位，提高数据传输的可靠性
    """
    
    def __init__(self, code_rate=0.5, use_coding=True, construction_SNR=2.0):
        """
        初始化极化码信道编码器
        
        参数:
        ----------
        code_rate : float, optional
            编码码率，默认0.5
        use_coding : bool, optional
            是否使用信道编码，默认True
        construction_SNR : float, optional
            构造时使用的SNR，默认2.0
        """
        self.code_rate = code_rate
        self.use_coding = use_coding
        self.construction_SNR = construction_SNR
        
        # 信息位长度
        self.info_bits = 256
        # 计算最小的2的幂次code_bits，满足码率要求
        min_code_bits = int(self.info_bits / code_rate)
        # 找到大于等于min_code_bits的最小2的幂次
        self.code_bits = 1
        while self.code_bits < min_code_bits:
            self.code_bits *= 2
        # 重新计算实际码率
        self.actual_code_rate = self.info_bits / self.code_bits
        # 校验位长度
        self.parity_bits = self.code_bits - self.info_bits
        
        print(f"初始化极化码编码器: 码率={code_rate}, 信息位={self.info_bits}, 码长={self.code_bits}, 实际码率={self.actual_code_rate:.3f}, 构造SNR={construction_SNR}")
        
        # 创建PolarCode对象
        self.pc = PolarCode(self.code_bits, self.info_bits)
        # 构造码
        Construct(self.pc, construction_SNR)
    
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
    
    def encode(self, data):
        """
        对数据进行极化码信道编码
        
        参数:
        ----------
        data : bytes
            原始数据
        
        返回:
        ----------
        bytes
            编码后的数据，包含极化码冗余位
        """
        if not self.use_coding:
            return data
        
        try:
            # 将数据转换为比特序列
            bits = self._bytes_to_bits(data)
            print(f"原始数据前10字节: {data[:10]}")
            print(f"原始数据大小: {len(data)} bytes")
            print(f"转换为比特序列后: {len(bits)} bits")
            
            # 分组编码
            encoded_bits = []
            print(f"开始分组编码: 总比特数={len(bits)}, 每组比特数={self.info_bits}, 总组数={len(bits)//self.info_bits}")
            
            for i in range(0, len(bits), self.info_bits):
                # 提取当前分组
                group = bits[i:i+self.info_bits]
                
                # 如果分组长度不足，进行零填充
                if len(group) < self.info_bits:
                    padding = self.info_bits - len(group)
                    group = np.concatenate([group, np.zeros(padding, dtype=int)])
                
                # 设置消息
                self.pc.set_message(group)
                
                # 编码
                Encode(self.pc)
                
                # 获取码word
                codeword = self.pc.get_codeword()
                encoded_bits.extend(codeword.tolist())
            
            # 将编码后的比特序列转换为字节
            encoded_bytes = self._bits_to_bytes(np.array(encoded_bits))
            
            # 添加编码头信息（1字节：编码类型 + 2字节：信息位长度 + 2字节：实际码率*1000）
            rate_scaled = int(self.actual_code_rate * 1000)
            header = bytes([ord('P'), 
                          (self.info_bits >> 8) & 0xFF, 
                          self.info_bits & 0xFF, 
                          (rate_scaled >> 8) & 0xFF, 
                          rate_scaled & 0xFF])
            print(f"头部信息: 编码类型='P', 信息位长度={self.info_bits}, 实际码率={self.actual_code_rate:.3f}, 缩放码率={rate_scaled}")
            
            # 调试信息
            print(f"编码完成: 原始数据大小={len(data)} bytes, 编码后大小={len(header + encoded_bytes)} bytes")
            print(f"编码后数据前10字节: {(header + encoded_bytes)[:10]}")
            
            return header + encoded_bytes
            
        except Exception as e:
            print(f"极化码编码失败: {e}")
            return data
    
    def get_polar_info(self):
        """
        获取极化码编码信息

        返回:
        ----------
        dict
            极化码编码信息
        """
        return {
            'code_rate': self.code_rate,
            'info_bits': self.info_bits,
            'code_bits': self.code_bits,
            'parity_bits': self.parity_bits,
            'frozen_positions': self.pc.frozen.tolist()
        }
    
    def encode_bits(self, bits):
        """
        直接编码比特序列

        参数:
        ----------
        bits : np.ndarray
            比特序列

        返回:
        ----------
        np.ndarray
            编码后的比特序列
        """
        encoded_bits = []
        
        for i in range(0, len(bits), self.info_bits):
            # 提取当前分组
            group = bits[i:i+self.info_bits]
            
            # 如果分组长度不足，进行零填充
            if len(group) < self.info_bits:
                padding = self.info_bits - len(group)
                group = np.concatenate([group, np.zeros(padding, dtype=int)])
            
            # 设置消息
            self.pc.set_message(group)
            
            # 编码
            Encode(self.pc)
            
            # 获取码word
            codeword = self.pc.get_codeword()
            encoded_bits.extend(codeword.tolist())
        
        return np.array(encoded_bits)


def get_polar_encoder(code_rate=0.5, use_coding=True, construction_SNR=2.0):
    """
    获取极化码信道编码器实例
    
    参数:
    ----------
    code_rate : float, optional
        编码码率
    use_coding : bool, optional
        是否使用信道编码
    construction_SNR : float, optional
        构造时使用的SNR，默认2.0
    
    返回:
    ----------
    PolarEncoder
        极化码信道编码器实例
    """
    return PolarEncoder(code_rate, use_coding, construction_SNR)
