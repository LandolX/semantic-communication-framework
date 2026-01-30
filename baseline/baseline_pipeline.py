#!/usr/bin/env python3
"""
传统编码baseline完整流程实现
从图像输入到JPEG编码，到信道物理层传输，再到解码恢复的完整流程
支持分块编码以提升无线传输的容错能力
"""

import os
import sys
import numpy as np
from PIL import Image

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data_input.image_loader import load_images_from_dir


class BaselinePipeline:
    """
    传统编码baseline完整流程类
    """
    
    def __init__(self, compression_type='jpeg', quality=90, modulation_type='qpsk', snr_dB=15, channel_type='awgn',
                 use_block_codec=False, use_coding=False, coding_scheme='ldpc', crc_type='crc16', 
                 ldpc_code_rate=1/2, visualize_constellation=False, debug=0, lossless=False):
        """
        初始化baseline流程
        :param compression_type: 压缩方式，如'jpeg', 'jpeg2000', 'jpeg2000bgr', 'h264'
        :param quality: 压缩质量，0-100
        :param modulation_type: 调制方式，如'qpsk', 'bpsk', '16qam', '64qam', '256qam'
        :param snr_dB: 信噪比，单位dB
        :param channel_type: 信道类型，如'awgn', 'rayleigh', 'rician'
        :param use_block_codec: 是否使用分块编码，默认False
        :param use_coding: 是否使用信道编码，默认False
        :param coding_scheme: 信道编码方案，如'crc', 'ldpc'，默认'ldpc'
        :param crc_type: CRC编码类型，如'crc8', 'crc16', 'crc32'，默认'crc16'
        :param ldpc_code_rate: LDPC编码的码率，默认1/2
        :param visualize_constellation: 是否可视化星座图，默认False
        :param debug: 调试级别，0表示关闭调试输出，1表示开启，默认0
        :param lossless: 是否使用无损压缩，默认False
        """
        self.compression_type = compression_type
        self.quality = quality
        self.use_block_codec = use_block_codec
        self.use_coding = use_coding
        self.coding_scheme = coding_scheme
        self.crc_type = crc_type
        self.ldpc_code_rate = ldpc_code_rate
        self.visualize_constellation_flag = visualize_constellation
        self.debug = debug
        self.lossless = lossless
        
        self.modulation_type = modulation_type
        self.snr_dB = snr_dB
        self.channel_type = channel_type
        
        self.encoder = None
        self.decoder = None
        self.channel_encoder = None
        self.channel_decoder = None
        self._init_encoder_decoder()
        
        self.comm_system = None
    
    def _init_encoder_decoder(self):
        """
        根据压缩方式初始化编码器和解码器
        """
        try:
            if self.compression_type == 'jpeg':
                from image_process.compression_coding.jpeg.jpeg_encoder import JPEGEncoder
                from image_recover.compression_coding.jpeg.jpeg_decoder import JPEGDecoder
                self.encoder = JPEGEncoder(quality=self.quality, use_block_codec=self.use_block_codec)
                self.decoder = JPEGDecoder(use_block_codec=self.use_block_codec)
            elif self.compression_type == 'jpeg2000':
                from image_process.compression_coding.jpeg2000.jpeg2000_encoder import JPEG2000Encoder
                from image_recover.compression_coding.jpeg2000.jpeg2000_decoder import JPEG2000Decoder
                self.encoder = JPEG2000Encoder(quality=self.quality, use_block_codec=self.use_block_codec)
                self.decoder = JPEG2000Decoder(use_block_codec=self.use_block_codec)
            elif self.compression_type == 'jpeg2000bgr':
                from image_process.compression_coding.jpeg2000bgr.jpeg2000bgr_encoder import JPEG2000BGREncoder
                from image_recover.compression_coding.jpeg2000bgr.jpeg2000bgr_decoder import JPEG2000BGRDecoder
                self.encoder = JPEG2000BGREncoder(quality=self.quality, use_block_codec=self.use_block_codec)
                self.decoder = JPEG2000BGRDecoder(use_block_codec=self.use_block_codec)
            elif self.compression_type == 'h264':
                from image_process.compression_coding.h264.h264_encoder import H264Encoder
                from image_recover.compression_coding.h264.h264_decoder import H264Decoder
                self.encoder = H264Encoder(quality=self.quality, use_block_codec=self.use_block_codec)
                self.decoder = H264Decoder(use_block_codec=self.use_block_codec)
            else:
                raise ValueError(f"不支持的压缩方式: {self.compression_type}")
            
            codec_mode = "分块编码" if self.use_block_codec else "传统编码"
            if self.debug:
                print(f"成功初始化编码器和解码器：{self.compression_type}，{codec_mode}，质量={self.quality}")
            
            # 初始化信道编码器和解码器
            if self.use_coding:
                if self.coding_scheme == 'crc':
                    from image_process.channel_coding.crc_channel_codec.crc_encoder import CRCEncoder
                    from image_recover.channel_coding.crc_channel_codec.crc_decoder import CRCDecoder
                    self.channel_encoder = CRCEncoder(crc_polynomial=self.crc_type)
                    self.channel_decoder = CRCDecoder()
                    if self.debug:
                        print(f"成功初始化CRC信道编码器和解码器：{self.crc_type}")
                elif self.coding_scheme == 'ldpc':
                    from image_process.channel_coding.ldpc_channel_codec.ldpc_channel_encoder import LDPCChannelEncoder
                    from image_recover.channel_coding.ldpc_channel_codec.ldpc_channel_decoder import LDPCChannelDecoder
                    self.channel_encoder = LDPCChannelEncoder(code_rate=self.ldpc_code_rate)
                    self.channel_decoder = LDPCChannelDecoder()
                    if self.debug:
                        print(f"成功初始化LDPC信道编码器和解码器：码率={self.ldpc_code_rate}")
                elif self.coding_scheme == 'polar':
                    from image_process.channel_coding.polar_channel_codec.polar_encoder import PolarEncoder
                    from image_recover.channel_coding.polar_channel_codec.polar_decoder import PolarDecoder
                    self.channel_encoder = PolarEncoder(code_rate=self.ldpc_code_rate, construction_SNR=2.0)
                    self.channel_decoder = PolarDecoder()
                    if self.debug:
                        print(f"成功初始化极化码信道编码器和解码器：码率={self.ldpc_code_rate}, 构造SNR=2.0")
            
        except Exception as e:
            print(f"初始化编码器和解码器失败: {e}")
            raise
    
    def _init_comm_system(self):
        """
        初始化通信系统
        """
        try:
            from digital_communication_system.py5g_phy_comm import CommunicationSystem
            
            self.comm_system = CommunicationSystem(
                modulation_type=self.modulation_type,
                channel_type=self.channel_type,
                snr_dB=self.snr_dB
            )
            
            if self.debug:
                print(f"成功初始化通信系统：{self.modulation_type}调制，{self.snr_dB}dB SNR，{self.channel_type}信道")
            
        except Exception as e:
            print(f"初始化通信系统失败: {e}")
            raise
    
    def process_image(self, image_path, output_path=None):
        """
        处理单张图像的完整流程
        :param image_path: 输入图像路径
        :param output_path: 输出图像路径，默认为None
        :return: 恢复的图像（PIL Image对象）
        """
        try:
            if self.debug:
                print(f"\n=== 开始处理图像: {os.path.basename(image_path)} ===")
            
            if self.debug:
                print("1. 加载图像...")
            image = Image.open(image_path)
            if self.debug:
                print(f"   图像信息: 模式={image.mode}, 尺寸={image.size}")
            
            if self.debug:
                print(f"2. {self.compression_type.upper()}编码...")
            encoded_data = self.encoder.encode_image(image, lossless=self.lossless)
            original_size = os.path.getsize(image_path)
            compressed_size = len(encoded_data)
            compression_ratio = original_size / compressed_size
            if self.debug:
                print(f"   编码完成: 原始大小={original_size} bytes, 压缩后大小={compressed_size} bytes, 压缩比={compression_ratio:.2f}:1, 压缩模式={'无损' if self.lossless else '有损'}")
            
            # 信道编码
            transmission_data = encoded_data
            if self.use_coding:
                if self.debug:
                    print(f"3. {self.coding_scheme.upper()}信道编码...")
                transmission_data = self.channel_encoder.encode(encoded_data)
                if self.debug:
                    print(f"   信道编码完成: 编码后大小={len(transmission_data)} bytes")
            
            if self.comm_system is None:
                self._init_comm_system()
            
            if self.debug:
                print("4. 数字通信系统传输...")
            received_data, ber = self.comm_system.transmit_receive(transmission_data)
            if self.debug:
                print(f"   传输完成: 误码率={ber:.6f}")
            
            # 信道解码
            decoded_channel_data = received_data
            channel_decode_status = True
            if self.use_coding:
                if self.debug:
                    print(f"5. {self.coding_scheme.upper()}信道解码...")
                decoded_channel_data, channel_decode_status = self.channel_decoder.decode(received_data)
                
                # 分析解码结果
                if self.debug:
                    if channel_decode_status:
                        print(f"   信道解码完成: 状态=成功")
                        print(f"   解码后数据大小: {len(decoded_channel_data)} bytes (原始编码数据大小: {len(encoded_data)} bytes)")
                        # 检查解码后数据的前几个字节
                        if len(decoded_channel_data) >= 10:
                            print(f"   解码后数据前10字节: {decoded_channel_data[:10]}")
                    else:
                        # 检查解码后的数据大小是否合理
                        original_data_size = len(encoded_data)
                        decoded_size = len(decoded_channel_data)
                        size_match = abs(decoded_size - original_data_size) < 1000  # 允许小误差
                        
                        if size_match:
                            print(f"   信道解码完成: 状态=部分成功 (数据提取成功)")
                            print(f"   解码后数据大小: {decoded_size} bytes (原始: {original_data_size} bytes)")
                            print(f"   数据大小匹配: {size_match}")
                        else:
                            print(f"   信道解码完成: 状态=失败 (数据提取失败)")
                            print(f"   警告: 解码失败，使用原始接收数据进行解码")
            
            # 可视化星座图（如果启用）
            if self.visualize_constellation_flag:
                if self.debug:
                    print("6. 可视化星座图...")
                title = f'{self.modulation_type.upper()} Constellation - {self.channel_type.upper()} Channel, SNR={self.snr_dB} dB, {self.compression_type.upper()} Compression'
                self.comm_system.visualize_constellation(title=title)
                if self.debug:
                    print("   星座图可视化完成")
            
            if self.debug:
                print(f"6. {self.compression_type.upper()}解码...")
            recovered_image, recovery_ratio = self.decoder.decode_image(decoded_channel_data, return_type='pil', default_size=image.size)
            if self.debug:
                print(f"   解码完成: 恢复图像模式={recovered_image.mode}, 尺寸={recovered_image.size}")
                print(f"   恢复比例: {recovery_ratio:.2%}（非灰色区域占总像素的比例）")
            
            if output_path:
                if self.debug:
                    print(f"5. 保存恢复的图像到: {output_path}")
                recovered_image.save(output_path)
                if self.debug:
                    print(f"   图像已成功保存")
            
            if self.debug:
                print(f"=== 图像处理完成 ===")
            
            return recovered_image
            
        except Exception as e:
            print(f"处理图像失败: {e}")
            raise
    
    def process_image_directory(self, image_dir, output_dir):
        """
        处理目录中的所有图像
        :param image_dir: 输入图像目录
        :param output_dir: 输出图像目录
        """
        try:
            if self.debug:
                print(f"\n=== 开始处理目录: {image_dir} ===")
            
            os.makedirs(output_dir, exist_ok=True)
            
            images = load_images_from_dir(image_dir)
            
            if self.comm_system is None:
                self._init_comm_system()
            
            image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            for i, (image_file, image_np) in enumerate(zip(image_files, images)):
                try:
                    image = Image.fromarray(image_np)
                    
                    output_path = os.path.join(output_dir, f"recovered_{image_file}")
                    
                    if self.debug:
                        print(f"\n--- 处理图像 {i+1}/{len(image_files)}: {image_file} ---")
                    
                    encoded_data = self.encoder.encode_image(image, lossless=self.lossless)
                    original_size = image_np.nbytes
                    compressed_size = len(encoded_data)
                    compression_ratio = original_size / compressed_size
                    if self.debug:
                        print(f"   编码完成: 原始大小={original_size} bytes, 压缩后大小={compressed_size} bytes, 压缩比={compression_ratio:.2f}:1, 压缩模式={'无损' if self.lossless else '有损'}")
                    
                    # 信道编码
                    transmission_data = encoded_data
                    if self.use_coding:
                        if self.debug:
                            print(f"   {self.coding_scheme.upper()}信道编码...")
                        transmission_data = self.channel_encoder.encode(encoded_data)
                        if self.debug:
                            print(f"   信道编码完成: 编码后大小={len(transmission_data)} bytes")
                    
                    received_data, ber = self.comm_system.transmit_receive(transmission_data)
                    if self.debug:
                        print(f"   传输完成: 误码率={ber:.6f}")
                    
                    # 信道解码
                    decoded_channel_data = received_data
                    channel_decode_status = True
                    if self.use_coding:
                        if self.debug:
                            print(f"   {self.coding_scheme.upper()}信道解码...")
                        decoded_channel_data, channel_decode_status = self.channel_decoder.decode(received_data)
                        
                        # 分析解码结果
                        if self.debug:
                            if channel_decode_status:
                                print(f"   信道解码完成: 状态=成功")
                            else:
                                # 检查解码后的数据大小是否合理
                                original_data_size = len(encoded_data)
                                decoded_size = len(decoded_channel_data)
                                size_match = abs(decoded_size - original_data_size) < 1000  # 允许小误差
                                
                                if size_match:
                                    print(f"   信道解码完成: 状态=部分成功 (数据提取成功)")
                                    print(f"   解码后数据大小: {decoded_size} bytes (原始: {original_data_size} bytes)")
                                else:
                                    print(f"   信道解码完成: 状态=失败 (数据提取失败)")
                    
                    # 可视化星座图（如果启用且是第一张图像）
                    if self.visualize_constellation_flag and i == 0:
                        if self.debug:
                            print("   可视化星座图...")
                        title = f'{self.modulation_type.upper()} Constellation - {self.channel_type.upper()} Channel, SNR={self.snr_dB} dB, {self.compression_type.upper()} Compression'
                        self.comm_system.visualize_constellation(title=title)
                        if self.debug:
                            print("   星座图可视化完成")
                    
                    recovered_image, recovery_ratio = self.decoder.decode_image(decoded_channel_data, return_type='pil', default_size=image.size)
                    if self.debug:
                        print(f"   解码完成: 恢复图像模式={recovered_image.mode}, 尺寸={recovered_image.size}")
                        print(f"   恢复比例: {recovery_ratio:.2%}（非灰色区域占总像素的比例）")
                    
                    recovered_image.save(output_path)
                    if self.debug:
                        print(f"   图像已成功保存到: {output_path}")
                    
                except Exception as e:
                    if self.debug:
                        print(f"处理图像 {image_file} 失败: {e}")
                    continue
            
            if self.debug:
                print(f"\n=== 目录处理完成，共处理 {len(image_files)} 张图像 ===")
            
        except Exception as e:
            print(f"处理目录失败: {e}")
            raise
    
    def get_system_info(self):
        """
        获取系统信息
        :return: 系统信息字典
        """
        return {
            'compression_type': self.compression_type,
            'quality': self.quality,
            'use_block_codec': self.use_block_codec,
            'use_coding': self.use_coding,
            'coding_scheme': self.coding_scheme,
            'crc_type': self.crc_type,
            'ldpc_code_rate': self.ldpc_code_rate,
            'modulation_type': self.modulation_type,
            'snr_dB': self.snr_dB,
            'channel_type': self.channel_type,
            'comm_system_initialized': self.comm_system is not None
        }


def run_baseline_pipeline(input_path=None, output_path=None, visualize_constellation=False, debug=0, image_path=None, lossless=False, **kwargs):
    """
    运行baseline流程的便捷函数
    :param input_path: 输入图像路径或目录路径
    :param output_path: 输出图像路径或目录路径
    :param visualize_constellation: 是否可视化星座图，默认False
    :param debug: 调试级别，0表示关闭调试输出，1表示开启，默认0
    :param image_path: 输入图像路径（兼容旧版本参数名）
    :param lossless: 是否使用无损压缩，默认False
    :param kwargs: 其他参数，包括use_coding、coding_scheme、crc_type和ldpc_code_rate
    :return: 处理单张图像时返回恢复的图像，处理目录时返回None
    """
    # 兼容旧版本参数名
    if input_path is None and image_path is not None:
        input_path = image_path
    
    if input_path is None:
        raise ValueError("必须提供input_path或image_path参数")
    
    if output_path is None:
        raise ValueError("必须提供output_path参数")
    
    pipeline = BaselinePipeline(visualize_constellation=visualize_constellation, debug=debug, lossless=lossless, **kwargs)
    
    # 判断输入是文件还是目录
    if os.path.isfile(input_path):
        # 处理单张图像
        return pipeline.process_image(input_path, output_path)
    elif os.path.isdir(input_path):
        # 处理目录中的所有图像
        pipeline.process_image_directory(input_path, output_path)
    else:
        raise ValueError(f"输入路径不存在: {input_path}")


if __name__ == "__main__":
    """
    baseline_pipeline使用示例
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    image_dir = os.path.join(project_root, 'data_input', 'image')
    output_dir = os.path.join(project_root, 'output')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取图像文件列表
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    
    if image_files:
        # 使用第一张图像
        image_file = image_files[0]
        image_path = os.path.join(image_dir, image_file)
        output_path = os.path.join(output_dir, f"recovered_{image_file}")
        
        print(f"=== baseline_pipeline 使用示例 ===")
        print(f"测试图像: {image_file}")
        
        # 创建baseline流程实例
        pipeline = BaselinePipeline(
            compression_type='jpeg',           # 使用JPEG编码
            quality=0,                        # 编码质量
            modulation_type='qpsk',            # 使用QPSK调制
            lossless=True,
            snr_dB=5,
            channel_type='awgn',               # 使用AWGN信道
            use_block_codec=True,             # 使用分块编码
            use_coding=True,                   # 启用信道编码
            coding_scheme='polar',             # 使用极化码编码
            visualize_constellation=False,      # 关闭星座图可视化
            debug=0
        )
        
        # 处理图像
        try:
            recovered_image = pipeline.process_image(image_path, output_path)
            print(f"\n=== 处理完成 ===")
            print(f"恢复的图像已保存到: {output_path}")
            print(f"系统信息: {pipeline.get_system_info()}")
        except Exception as e:
            print(f"处理图像失败: {e}")
    else:
        print(f"在目录 {image_dir} 中未找到图像文件")
