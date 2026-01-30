#!/usr/bin/env python3
"""
极化码信道解码器

使用极化码（Polar Code）解码恢复原始数据，验证数据完整性
"""

import numpy as np
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('../../../../'))

# 使用本地复制的polar codes实现
from polarcodes import PolarCode
from polarcodes.Construct import Construct
from polarcodes.Decode import Decode


class PolarDecoder:
    """
    极化码信道解码器类
    
    实现极化码解码，恢复原始数据并验证数据完整性
    """
    
    def __init__(self, use_coding=True):
        """
        初始化极化码信道解码器
        
        参数:
        ----------
        use_coding : bool, optional
            是否使用信道解码，默认True
        """
        self.use_coding = use_coding
    
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
    
    def _decode_polar(self, encoded_data, info_bits, code_bits, is_soft=False):
        """
        解码极化码数据

        参数:
        ----------
        encoded_data : np.ndarray
            编码后的数据（可以是硬判决比特或软信息LLR）
        info_bits : int
            信息位长度
        code_bits : int
            编码后总长度
        is_soft : bool
            是否使用软信息输入

        返回:
        ----------
        np.ndarray
            解码后的信息位
        """
        # 创建PolarCode对象
        pc = PolarCode(code_bits, info_bits)
        # 构造码
        Construct(pc, 2.0)
        
        if is_soft:
            # 使用软信息输入（直接使用LLR）
            # 确保LLR长度正确
            if len(encoded_data) >= code_bits:
                pc.likelihoods = encoded_data[:code_bits]
            else:
                # 如果长度不足，填充
                llr = np.zeros(code_bits)
                llr[:len(encoded_data)] = encoded_data
                pc.likelihoods = llr
        else:
            # 使用硬判决输入
            # 对于硬判决，我们将0映射到正无穷，1映射到负无穷
            llr = np.zeros(code_bits)
            for i in range(min(len(encoded_data), code_bits)):
                llr[i] = 1000 if encoded_data[i] == 0 else -1000
            pc.likelihoods = llr
        
        # 解码
        Decode(pc)
        
        # 获取解码后的消息
        return pc.message_received
    
    def decode(self, encoded_data):
        """
        对数据进行极化码信道解码
        
        参数:
        ----------
        encoded_data : bytes
            编码后的数据
        
        返回:
        ----------
        tuple
            (原始数据, 解码状态)
            解码状态: True表示成功，False表示解码失败
        """
        if not self.use_coding:
            return encoded_data, True
        
        try:
            # 检查编码头
            if len(encoded_data) < 5:
                return encoded_data, False
            
            # 解析头信息
            header = encoded_data[:5]
            if header[0] != ord('P'):
                return encoded_data, False
            
            # 获取信息位长度和码率
            info_bits = (header[1] << 8) | header[2]
            rate_scaled = (header[3] << 8) | header[4]
            code_rate = rate_scaled / 1000
            
            # 计算编码后每分组的长度
            code_bits = int(info_bits / code_rate)
            
            # 分离数据和头
            data_without_header = encoded_data[5:]
            
            # 将数据转换为比特序列
            encoded_bits = self._bytes_to_bits(data_without_header)
            
            # 分组解码
            decoded_bits = []
            print(f"开始分组解码: 总比特数={len(encoded_bits)}, 每组比特数={code_bits}, 总组数={len(encoded_bits)//code_bits}")
            
            for i in range(0, len(encoded_bits), code_bits):
                # 提取当前分组
                group = encoded_bits[i:i+code_bits]
                
                # 如果分组长度不足，跳过
                if len(group) < code_bits:
                    print(f"跳过长度不足的分组: {len(group)} bits")
                    break
                
                # 进行极化码解码
                decoded_group = self._decode_polar(group, info_bits, code_bits)
                decoded_bits.extend(decoded_group.tolist())
            
            print(f"解码完成: 总解码比特数={len(decoded_bits)}")
            # 将解码后的比特序列转换为字节
            decoded_bytes = self._bits_to_bytes(np.array(decoded_bits))
            print(f"转换为字节后: 大小={len(decoded_bytes)} bytes, 前10字节={decoded_bytes[:10]}")
            
            # 确保解码后的数据大小与原始数据大小匹配
            # 计算原始数据的预期大小
            # 编码时，数据被分组为 info_bits 比特的组，最后一组不足时填充
            # 解码后，我们需要计算实际的原始数据大小
            num_groups = len(encoded_bits) // code_bits
            actual_bits = info_bits * num_groups
            expected_size = actual_bits // 8
            
            # 计算原始数据的实际大小（不包括填充）
            # 注意：这里我们假设编码前的数据长度是8的倍数
            # 在实际应用中，应该在编码时添加长度信息
            
            if len(decoded_bytes) > expected_size:
                decoded_bytes = decoded_bytes[:expected_size]
                print(f"调整解码后数据大小为: {len(decoded_bytes)} bytes")
            
            return decoded_bytes, True
            
        except Exception as e:
            print(f"极化码解码失败: {e}")
            # 如果解码失败，尝试提取数据（不含头）
            try:
                if len(encoded_data) >= 5:
                    data_without_header = encoded_data[5:]
                    # 粗略估计原始数据大小
                    info_bits = (encoded_data[1] << 8) | encoded_data[2]
                    estimated_original_size = len(data_without_header) // 2  # 码率1/2时的估计
                    if estimated_original_size > 0:
                        return data_without_header[:estimated_original_size], False
            except:
                pass
            # 如果提取失败，返回原始数据
            return encoded_data, False
    
    def decode_bits(self, encoded_data, info_bits, code_bits, is_soft=True):
        """
        直接解码比特序列或软信息

        参数:
        ----------
        encoded_data : np.ndarray
            编码后的数据（可以是硬判决比特或软信息LLR）
        info_bits : int
            信息位长度
        code_bits : int
            编码后总长度
        is_soft : bool
            是否使用软信息输入

        返回:
        ----------
        np.ndarray
            解码后的比特序列
        """
        decoded_bits = []
        
        # 对于软信息，直接使用
        if is_soft:
            # 分组解码
            for i in range(0, len(encoded_data), code_bits):
                # 提取当前分组
                group = encoded_data[i:i+code_bits]
                
                # 如果分组长度不足，跳过
                if len(group) < code_bits:
                    break
                
                # 进行极化码解码
                decoded_group = self._decode_polar(group, info_bits, code_bits, is_soft=True)
                decoded_bits.extend(decoded_group.tolist())
        else:
            # 对于硬判决比特
            for i in range(0, len(encoded_data), code_bits):
                # 提取当前分组
                group = encoded_data[i:i+code_bits]
                
                # 如果分组长度不足，跳过
                if len(group) < code_bits:
                    break
                
                # 进行极化码解码
                decoded_group = self._decode_polar(group, info_bits, code_bits, is_soft=False)
                decoded_bits.extend(decoded_group.tolist())
        
        return np.array(decoded_bits)


def get_polar_decoder(use_coding=True):
    """
    获取极化码信道解码器实例
    
    参数:
    ----------
    use_coding : bool, optional
        是否使用信道解码
    
    返回:
    ----------
    PolarDecoder
        极化码信道解码器实例
    """
    return PolarDecoder(use_coding)
