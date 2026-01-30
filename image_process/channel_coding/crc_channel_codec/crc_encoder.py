#!/usr/bin/env python3
"""
CRC信道编码器

使用CRC（循环冗余校验）编码提高数据可靠性，为数据添加冗余校验位
"""

import numpy as np


class CRCEncoder:
    """
    CRC信道编码器类
    
    实现CRC编码，为数据添加冗余校验位，提高数据传输的可靠性
    """
    
    def __init__(self, crc_polynomial='crc16', use_coding=True):
        """
        初始化CRC信道编码器
        
        参数:
        ----------
        crc_polynomial : str, optional
            CRC多项式类型，默认使用'crc16'
        use_coding : bool, optional
            是否使用信道编码，默认True
        """
        self.crc_polynomial = crc_polynomial
        self.use_coding = use_coding
        
        self.crc_polynomials = {
            'crc8': 0x1D,      # x^8 + x^4 + x^3 + x^2 + 1
            'crc16': 0x8005,    # x^16 + x^15 + x^2 + 1 (CRC-16-IBM)
            'crc32': 0x04C11DB7  # x^32 + x^26 + x^23 + x^22 + x^16 + x^12 + x^11 + x^10 + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1
        }
        
        self.polynomial = self.crc_polynomials.get(crc_polynomial, 0x8005)
        self.crc_bits = {'crc8': 8, 'crc16': 16, 'crc32': 32}.get(crc_polynomial, 16)
    
    def encode(self, data):
        """
        对数据进行CRC信道编码
        
        参数:
        ----------
        data : bytes
            原始数据
        
        返回:
        ----------
        bytes
            编码后的数据，包含CRC校验位
        """
        if not self.use_coding:
            return data
        
        crc_value = self._calculate_crc(data)
        
        crc_bytes = crc_value.to_bytes((self.crc_bits + 7) // 8, byteorder='big')
        
        encoded_data = data + crc_bytes
        
        header = bytes([ord('C'), self.crc_bits // 8])
        
        return header + encoded_data
    
    def _calculate_crc(self, data):
        """
        计算CRC校验值
        
        参数:
        ----------
        data : bytes
            要计算CRC的数据
        
        返回:
        ----------
        int
            CRC校验值
        """
        crc = 0
        
        for byte in data:
            crc ^= (byte << (self.crc_bits - 8))
            
            for _ in range(8):
                if crc & (1 << (self.crc_bits - 1)):
                    crc = (crc << 1) ^ self.polynomial
                else:
                    crc <<= 1
                crc &= (1 << self.crc_bits) - 1
        
        return crc
    
    def get_crc_info(self):
        """
        获取CRC编码信息
        
        返回:
        ----------
        dict
            CRC编码信息
        """
        return {
            'crc_polynomial': self.crc_polynomial,
            'polynomial_value': self.polynomial,
            'crc_bits': self.crc_bits,
            'crc_bytes': (self.crc_bits + 7) // 8
        }


def get_crc_encoder(crc_polynomial='crc16', use_coding=True):
    """
    获取CRC信道编码器实例
    
    参数:
    ----------
    crc_polynomial : str, optional
        CRC多项式类型
    use_coding : bool, optional
        是否使用信道编码
    
    返回:
    ----------
    CRCEncoder
        CRC信道编码器实例
    """
    return CRCEncoder(crc_polynomial, use_coding)
