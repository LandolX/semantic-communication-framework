#!/usr/bin/env python3
"""
通用分块编码实现
为三种图像编码方式（JPEG、JPEG2000、JPEG2000BGR）提供统一的分块编码功能
"""

import struct
import numpy as np


class BlockCodec:
    """
    通用分块编码器类
    实现真实的分块编码，支持不同的分块大小和FEC编码方式
    """
    
    def __init__(self, block_size=1024, fec_strategy='repetition', fec_level=2):
        """
        初始化分块编码器
        :param block_size: 分块大小，单位为字节
        :param fec_strategy: FEC编码策略，支持'repetition'（重复编码）、'xor'（异或编码）
        :param fec_level: FEC编码级别，对于repetition表示重复次数，对于xor表示校验块数量
        """
        self.block_size = block_size
        self.fec_strategy = fec_strategy
        self.fec_level = fec_level
    
    def encode(self, data, codec_type):
        """
        对数据进行分块编码
        :param data: 原始数据（bytes）
        :param codec_type: 编解码器类型，用于生成帧标记，如'jpeg'、'jpeg2000'、'jpeg2000bgr'
        :return: 编码后的数据（bytes）
        """
        original_size = len(data)
        
        # 生成帧标记
        frame_marker = self._generate_frame_marker(codec_type, original_size)
        
        # 分块处理
        blocks = self._split_into_blocks(data)
        
        # FEC编码
        encoded_blocks = self._apply_fec(blocks)
        
        # 组装编码后的数据
        encoded_data = self._assemble_encoded_data(frame_marker, encoded_blocks)
        
        return encoded_data
    
    def decode(self, encoded_data, codec_type):
        """
        对编码数据进行解码
        :param encoded_data: 编码后的数据（bytes）
        :param codec_type: 编解码器类型，用于验证帧标记
        :return: 解码后的数据（bytes），如果解码失败返回None
        """
        try:
            # 解析帧标记
            original_size, frame_end = self._parse_frame_marker(encoded_data, codec_type)
            
            if original_size is None:
                return None
            
            # 解析编码块
            encoded_blocks = self._parse_encoded_blocks(encoded_data[frame_end:])
            
            # FEC解码
            blocks = self._recover_from_fec(encoded_blocks)
            
            # 重组数据
            data = self._assemble_from_blocks(blocks, original_size)
            
            return data
            
        except Exception as e:
            print(f"分块解码失败: {e}")
            return None
    
    def _generate_frame_marker(self, codec_type, original_size):
        """
        生成帧标记
        :param codec_type: 编解码器类型
        :param original_size: 原始数据大小
        :return: 帧标记（bytes）
        """
        # 根据编解码器类型选择帧标记
        marker_dict = {
            'jpeg': b'BLKJ',
            'jpeg2000': b'BLK2',
            'jpeg2000bgr': b'BLKB'
        }
        
        marker = marker_dict.get(codec_type, b'BLKX')
        
        # 帧标记格式：[4字节标记] + [4字节原始大小] + [4字节分块大小] + [1字节FEC策略] + [1字节FEC级别]
        # FEC策略：0 - repetition, 1 - xor
        fec_strategy_code = 0 if self.fec_strategy == 'repetition' else 1
        
        return marker + struct.pack('>III BB', original_size, self.block_size, 0, fec_strategy_code, self.fec_level)
    
    def _parse_frame_marker(self, encoded_data, codec_type):
        """
        解析帧标记
        :param encoded_data: 编码后的数据
        :param codec_type: 编解码器类型
        :return: (原始大小, 有效载荷起始位置)，如果解析失败返回(None, None)
        """
        # 帧标记长度：4字节标记 + 3个I(4字节) + 2个B(1字节) = 4 + 12 + 2 = 18字节
        if len(encoded_data) < 18:
            return None, None
        
        # 验证标记
        expected_markers = {
            'jpeg': b'BLKJ',
            'jpeg2000': b'BLK2',
            'jpeg2000bgr': b'BLKB'
        }
        
        expected_marker = expected_markers.get(codec_type, b'BLKX')
        actual_marker = encoded_data[:4]
        
        if actual_marker != expected_marker:
            return None, None
        
        # 解析帧标记字段
        original_size = struct.unpack('>I', encoded_data[4:8])[0]
        
        # 帧标记结束位置是18字节，后面跟着block_count和block_size
        return original_size, 18
    
    def _split_into_blocks(self, data):
        """
        将数据分割成块
        :param data: 原始数据
        :return: 块列表
        """
        blocks = []
        data_len = len(data)
        
        for i in range(0, data_len, self.block_size):
            block = data[i:i+self.block_size]
            # 填充块到固定大小
            if len(block) < self.block_size:
                block = block.ljust(self.block_size, b'\x00')
            blocks.append(block)
        
        return blocks
    
    def _apply_fec(self, blocks):
        """
        对块应用FEC编码
        :param blocks: 原始块列表
        :return: 编码后的块列表
        """
        if self.fec_strategy == 'repetition':
            return self._repetition_encode(blocks)
        elif self.fec_strategy == 'xor':
            return self._xor_encode(blocks)
        else:
            return blocks
    
    def _repetition_encode(self, blocks):
        """
        重复编码
        :param blocks: 原始块列表
        :return: 编码后的块列表
        """
        encoded_blocks = []
        
        for block in blocks:
            # 为每个块添加重复编码
            for _ in range(self.fec_level):
                encoded_blocks.append(block)
        
        return encoded_blocks
    
    def _xor_encode(self, blocks):
        """
        XOR编码
        :param blocks: 原始块列表
        :return: 编码后的块列表（包含原始块和校验块）
        """
        if not blocks:
            return []
        
        encoded_blocks = blocks.copy()
        block_count = len(blocks)
        
        # 生成校验块
        for i in range(self.fec_level):
            parity_block = bytearray(self.block_size)
            
            for j in range(block_count):
                block = blocks[j]
                for k in range(self.block_size):
                    parity_block[k] ^= block[k]
            
            encoded_blocks.append(bytes(parity_block))
        
        return encoded_blocks
    
    def _assemble_encoded_data(self, frame_marker, encoded_blocks):
        """
        组装编码后的数据
        :param frame_marker: 帧标记
        :param encoded_blocks: 编码后的块列表
        :return: 组装后的数据
        """
        # 编码数据格式：[帧标记] + [块数量(4字节)] + [块大小(4字节)] + [块1] + [块2] + ...
        block_count = len(encoded_blocks)
        
        data = frame_marker
        data += struct.pack('>II', block_count, self.block_size)
        
        for block in encoded_blocks:
            data += block
        
        return data
    
    def _parse_encoded_blocks(self, payload_data):
        """
        解析编码块
        :param payload_data: 有效载荷数据
        :return: 编码块列表
        """
        if len(payload_data) < 8:
            return []
        
        block_count = struct.unpack('>I', payload_data[:4])[0]
        block_size = struct.unpack('>I', payload_data[4:8])[0]
        
        blocks = []
        payload_start = 8
        total_payload_size = len(payload_data)
        
        for i in range(block_count):
            block_start = payload_start + i * block_size
            block_end = block_start + block_size
            
            if block_end > total_payload_size:
                break
            
            block = payload_data[block_start:block_end]
            blocks.append(block)
        
        return blocks
    
    def _recover_from_fec(self, encoded_blocks):
        """
        从FEC编码中恢复原始块
        :param encoded_blocks: 编码块列表
        :return: 恢复的原始块列表
        """
        if self.fec_strategy == 'repetition':
            return self._repetition_decode(encoded_blocks)
        elif self.fec_strategy == 'xor':
            return self._xor_decode(encoded_blocks)
        else:
            return encoded_blocks
    
    def _repetition_decode(self, encoded_blocks):
        """
        重复解码
        :param encoded_blocks: 编码块列表
        :return: 恢复的原始块列表
        """
        if not encoded_blocks:
            return []
        
        # 每self.fec_level个块为一组，每组对应一个原始块
        original_blocks = []
        group_size = self.fec_level
        
        for i in range(0, len(encoded_blocks), group_size):
            group = encoded_blocks[i:i+group_size]
            if group:
                # 使用多数表决恢复原始块
                original_block = self._majority_vote(group)
                original_blocks.append(original_block)
        
        return original_blocks
    
    def _majority_vote(self, blocks):
        """
        多数表决恢复原始块
        :param blocks: 同一原始块的多个副本
        :return: 恢复的原始块
        """
        if not blocks:
            return b''
        
        block_size = len(blocks[0])
        result = bytearray(block_size)
        
        for i in range(block_size):
            # 统计每个字节值的出现次数
            byte_counts = {}
            for block in blocks:
                if i < len(block):
                    byte_val = block[i]
                    byte_counts[byte_val] = byte_counts.get(byte_val, 0) + 1
            
            # 选择出现次数最多的字节值
            if byte_counts:
                result[i] = max(byte_counts, key=byte_counts.get)
            else:
                result[i] = 0
        
        return bytes(result)
    
    def _xor_decode(self, encoded_blocks):
        """
        XOR解码
        :param encoded_blocks: 编码块列表（包含原始块和校验块）
        :return: 恢复的原始块列表
        """
        if not encoded_blocks:
            return []
        
        block_count = len(encoded_blocks) - self.fec_level
        
        if block_count <= 0:
            return []
        
        # 只返回原始块，忽略校验块
        return encoded_blocks[:block_count]
    
    def _assemble_from_blocks(self, blocks, original_size):
        """
        从块中重组数据
        :param blocks: 块列表
        :param original_size: 原始数据大小
        :return: 重组后的数据
        """
        data = b''.join(blocks)
        return data[:original_size]


# 便捷函数
def block_encode(data, codec_type, block_size=1024, fec_strategy='repetition', fec_level=2):
    """
    便捷的分块编码函数
    :param data: 原始数据（bytes）
    :param codec_type: 编解码器类型
    :param block_size: 分块大小
    :param fec_strategy: FEC编码策略
    :param fec_level: FEC编码级别
    :return: 编码后的数据（bytes）
    """
    codec = BlockCodec(block_size=block_size, fec_strategy=fec_strategy, fec_level=fec_level)
    return codec.encode(data, codec_type)


def block_decode(encoded_data, codec_type):
    """
    便捷的分块解码函数
    :param encoded_data: 编码后的数据（bytes）
    :param codec_type: 编解码器类型
    :return: 解码后的数据（bytes），如果解码失败返回None
    """
    codec = BlockCodec()
    return codec.decode(encoded_data, codec_type)
