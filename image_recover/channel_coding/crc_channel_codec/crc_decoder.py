#!/usr/bin/env python3
"""
CRC信道解码器

使用CRC（循环冗余校验）解码验证数据完整性并恢复原始数据
"""

import numpy as np


class CRCDecoder:
    """
    CRC信道解码器类
    
    实现CRC解码，验证数据完整性并恢复原始数据
    """
    
    def __init__(self, use_coding=True):
        """
        初始化CRC信道解码器
        
        参数:
        ----------
        use_coding : bool, optional
            是否使用信道解码，默认True
        """
        self.use_coding = use_coding
        
        self.crc_polynomials = {
            'crc8': 0x1D,      # x^8 + x^4 + x^3 + x^2 + 1
            'crc16': 0x8005,    # x^16 + x^15 + x^2 + 1 (CRC-16-IBM)
            'crc32': 0x04C11DB7  # x^32 + x^26 + x^23 + x^22 + x^16 + x^12 + x^11 + x^10 + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1
        }
        
        self.crc_bits_map = {'crc8': 8, 'crc16': 16, 'crc32': 32}
    
    def decode(self, encoded_data):
        """
        对数据进行CRC信道解码
        
        参数:
        ----------
        encoded_data : bytes
            编码后的数据
        
        返回:
        ----------
        tuple
            (原始数据, 解码状态)
            解码状态: True表示成功，False表示CRC校验失败
        """
        if not self.use_coding:
            return encoded_data, True
        
        try:
            if len(encoded_data) < 2:
                return encoded_data, False
            
            header = encoded_data[:2]
            if header[0] != ord('C'):
                return encoded_data, False
            
            crc_bytes_length = header[1]
            
            crc_type = self._get_crc_type(crc_bytes_length)
            if crc_type is None:
                return encoded_data, False
            
            data_without_header = encoded_data[2:]
            if len(data_without_header) <= crc_bytes_length:
                return encoded_data, False
            
            data = data_without_header[:-crc_bytes_length]
            crc_bytes = data_without_header[-crc_bytes_length:]
            
            crc_value = int.from_bytes(crc_bytes, byteorder='big')
            
            polynomial = self.crc_polynomials[crc_type]
            crc_bits = self.crc_bits_map[crc_type]
            
            calculated_crc = self._calculate_crc(data, polynomial, crc_bits)
            
            if calculated_crc == crc_value:
                return data, True
            else:
                return data, False
                
        except Exception as e:
            try:
                if len(encoded_data) >= 2:
                    crc_bytes_length = encoded_data[1]
                    if len(encoded_data) > 2 + crc_bytes_length:
                        data = encoded_data[2:-crc_bytes_length]
                        return data, False
            except:
                pass
            return encoded_data, False
    
    def _calculate_crc(self, data, polynomial, crc_bits):
        """
        计算CRC校验值
        
        参数:
        ----------
        data : bytes
            要计算CRC的数据
        polynomial : int
            CRC多项式
        crc_bits : int
            CRC位数
        
        返回:
        ----------
        int
            CRC校验值
        """
        crc = 0
        
        for byte in data:
            crc ^= (byte << (crc_bits - 8))
            
            for _ in range(8):
                if crc & (1 << (crc_bits - 1)):
                    crc = (crc << 1) ^ polynomial
                else:
                    crc <<= 1
                crc &= (1 << crc_bits) - 1
        
        return crc
    
    def _get_crc_type(self, crc_bytes_length):
        """
        根据CRC字节数确定CRC类型
        
        参数:
        ----------
        crc_bytes_length : int
            CRC字节数
        
        返回:
        ----------
        str or None
            CRC类型，如果无法确定则返回None
        """
        crc_type_map = {1: 'crc8', 2: 'crc16', 4: 'crc32'}
        return crc_type_map.get(crc_bytes_length)
    
    def verify_crc(self, data, crc_value, crc_type='crc16'):
        """
        验证CRC值
        
        参数:
        ----------
        data : bytes
            要验证的数据
        crc_value : int
            CRC校验值
        crc_type : str, optional
            CRC类型
        
        返回:
        ----------
        bool
            验证结果
        """
        if crc_type not in self.crc_polynomials:
            return False
        
        polynomial = self.crc_polynomials[crc_type]
        crc_bits = self.crc_bits_map[crc_type]
        
        calculated_crc = self._calculate_crc(data, polynomial, crc_bits)
        
        return calculated_crc == crc_value


def get_crc_decoder(use_coding=True):
    """
    获取CRC信道解码器实例
    
    参数:
    ----------
    use_coding : bool, optional
        是否使用信道解码
    
    返回:
    ----------
    CRCDecoder
        CRC信道解码器实例
    """
    return CRCDecoder(use_coding)
