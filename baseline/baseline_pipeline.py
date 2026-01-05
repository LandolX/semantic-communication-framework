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
                 use_block_codec=False, visualize_constellation=False):
        """
        初始化baseline流程
        :param compression_type: 压缩方式，如'jpeg', 'jpeg2000', 'jpeg2000bgr'
        :param quality: 压缩质量，0-100
        :param modulation_type: 调制方式，如'qpsk', 'bpsk', '16qam', '64qam'
        :param snr_dB: 信噪比，单位dB
        :param channel_type: 信道类型，如'awgn', 'rayleigh', 'rician'
        :param use_block_codec: 是否使用分块编码，默认False
        :param visualize_constellation: 是否可视化星座图，默认False
        """
        self.compression_type = compression_type
        self.quality = quality
        self.use_block_codec = use_block_codec
        self.visualize_constellation_flag = visualize_constellation
        
        self.modulation_type = modulation_type
        self.snr_dB = snr_dB
        self.channel_type = channel_type
        
        self.encoder = None
        self.decoder = None
        self._init_encoder_decoder()
        
        self.comm_system = None
    
    def _init_encoder_decoder(self):
        """
        根据压缩方式初始化编码器和解码器
        """
        try:
            if self.compression_type == 'jpeg':
                from image_process.baseline.jpeg.jpeg_encoder import JPEGEncoder
                from image_recover.baseline.jpeg.jpeg_decoder import JPEGDecoder
                self.encoder = JPEGEncoder(quality=self.quality, use_block_codec=self.use_block_codec)
                self.decoder = JPEGDecoder(use_block_codec=self.use_block_codec)
            elif self.compression_type == 'jpeg2000':
                from image_process.baseline.jpeg2000.jpeg2000_encoder import JPEG2000Encoder
                from image_recover.baseline.jpeg2000.jpeg2000_decoder import JPEG2000Decoder
                self.encoder = JPEG2000Encoder(quality=self.quality, use_block_codec=self.use_block_codec)
                self.decoder = JPEG2000Decoder(use_block_codec=self.use_block_codec)
            elif self.compression_type == 'jpeg2000bgr':
                from image_process.baseline.jpeg2000bgr.jpeg2000bgr_encoder import JPEG2000BGREncoder
                from image_recover.baseline.jpeg2000bgr.jpeg2000bgr_decoder import JPEG2000BGRDecoder
                self.encoder = JPEG2000BGREncoder(quality=self.quality, use_block_codec=self.use_block_codec)
                self.decoder = JPEG2000BGRDecoder(use_block_codec=self.use_block_codec)
            else:
                raise ValueError(f"不支持的压缩方式: {self.compression_type}")
            
            codec_mode = "分块编码" if self.use_block_codec else "传统编码"
            print(f"成功初始化编码器和解码器：{self.compression_type}，{codec_mode}，质量={self.quality}")
            
        except Exception as e:
            print(f"初始化编码器和解码器失败: {e}")
            raise
    
    def _init_comm_system(self):
        """
        初始化通信系统
        """
        try:
            from digital_communication_system.py5g_phy_comm import create_system
            
            self.comm_system = create_system(
                use_simple=True,
                modulation_type=self.modulation_type,
                snr_dB=self.snr_dB,
                channel_type=self.channel_type
            )
            
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
            print(f"\n=== 开始处理图像: {os.path.basename(image_path)} ===")
            
            print("1. 加载图像...")
            image = Image.open(image_path)
            print(f"   图像信息: 模式={image.mode}, 尺寸={image.size}")
            
            print("2. JPEG编码...")
            jpeg_data = self.encoder.encode_image(image)
            original_size = os.path.getsize(image_path)
            compressed_size = len(jpeg_data)
            compression_ratio = original_size / compressed_size
            print(f"   编码完成: 原始大小={original_size} bytes, 压缩后大小={compressed_size} bytes, 压缩比={compression_ratio:.2f}:1")
            
            if self.comm_system is None:
                self._init_comm_system()
            
            print("3. 数字通信系统传输...")
            received_data, ber = self.comm_system.transmit_receive(jpeg_data)
            print(f"   传输完成: 误码率={ber:.6f}")
            
            # 可视化星座图（如果启用）
            if self.visualize_constellation_flag:
                print("4. 可视化星座图...")
                title = f'{self.modulation_type.upper()} Constellation - {self.channel_type.upper()} Channel, SNR={self.snr_dB} dB, {self.compression_type.upper()} Compression'
                self.comm_system.visualize_constellation(title=title)
                print("   星座图可视化完成")
            
            print("4. JPEG解码...")
            recovered_image, recovery_ratio = self.decoder.decode_image(received_data, return_type='pil', default_size=image.size)
            print(f"   解码完成: 恢复图像模式={recovered_image.mode}, 尺寸={recovered_image.size}")
            
            print(f"   恢复比例: {recovery_ratio:.2%}（非灰色区域占总像素的比例）")
            
            if output_path:
                print(f"5. 保存恢复的图像到: {output_path}")
                recovered_image.save(output_path)
                print(f"   图像已成功保存")
            
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
                    
                    print(f"\n--- 处理图像 {i+1}/{len(image_files)}: {image_file} ---")
                    
                    jpeg_data = self.encoder.encode_image(image)
                    original_size = image_np.nbytes
                    compressed_size = len(jpeg_data)
                    compression_ratio = original_size / compressed_size
                    print(f"   编码完成: 原始大小={original_size} bytes, 压缩后大小={compressed_size} bytes, 压缩比={compression_ratio:.2f}:1")
                    
                    received_data, ber = self.comm_system.transmit_receive(jpeg_data)
                    print(f"   传输完成: 误码率={ber:.6f}")
                    
                    # 可视化星座图（如果启用且是第一张图像）
                    if self.visualize_constellation_flag and i == 0:
                        print("   可视化星座图...")
                        title = f'{self.modulation_type.upper()} Constellation - {self.channel_type.upper()} Channel, SNR={self.snr_dB} dB, {self.compression_type.upper()} Compression'
                        self.comm_system.visualize_constellation(title=title)
                        print("   星座图可视化完成")
                    
                    recovered_image, recovery_ratio = self.decoder.decode_image(received_data, return_type='pil', default_size=image.size)
                    print(f"   解码完成: 恢复图像模式={recovered_image.mode}, 尺寸={recovered_image.size}")
                    
                    print(f"   恢复比例: {recovery_ratio:.2%}（非灰色区域占总像素的比例）")
                    
                    recovered_image.save(output_path)
                    print(f"   图像已成功保存到: {output_path}")
                    
                except Exception as e:
                    print(f"处理图像 {image_file} 失败: {e}")
                    continue
            
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
            'modulation_type': self.modulation_type,
            'snr_dB': self.snr_dB,
            'channel_type': self.channel_type,
            'comm_system_initialized': self.comm_system is not None
        }


def run_baseline_pipeline(image_path, output_path, visualize_constellation=False, **kwargs):
    """
    运行baseline流程的便捷函数
    :param image_path: 输入图像路径
    :param output_path: 输出图像路径
    :param visualize_constellation: 是否可视化星座图，默认False
    :param kwargs: 其他参数
    :return: 恢复的图像
    """
    pipeline = BaselinePipeline(visualize_constellation=visualize_constellation, **kwargs)
    return pipeline.process_image(image_path, output_path)


def run_baseline_pipeline_directory(image_dir, output_dir, visualize_constellation=False, **kwargs):
    """
    运行baseline流程处理目录的便捷函数
    :param image_dir: 输入图像目录
    :param output_dir: 输出图像目录
    :param visualize_constellation: 是否可视化星座图，默认False
    :param kwargs: 其他参数
    """
    pipeline = BaselinePipeline(visualize_constellation=visualize_constellation, **kwargs)
    pipeline.process_image_directory(image_dir, output_dir)


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    image_dir = os.path.join(project_root, 'data_input', 'image')
    output_dir = os.path.join(project_root, 'output')
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    pipeline = BaselinePipeline(
        compression_type='jpeg2000',
        quality=90,
        modulation_type='qpsk',
        snr_dB=13,
        channel_type='awgn',
        use_block_codec=False,
        visualize_constellation=True  # 启用星座图可视化
    )
    
    # 获取图像文件列表
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][:1]
    
    if image_files:
        image_file = image_files[0]
        image_path = os.path.join(image_dir, image_file)
        output_path = os.path.join(output_dir, f"recovered_{image_file}")
        
        try:
            print(f"\n处理图像用于星座图可视化测试: {image_file}")
            pipeline.process_image(image_path, output_path)
        except Exception as e:
            print(f"处理图像 {image_file} 失败: {e}")
    else:   
        print(f"在目录 {image_dir} 中未找到图像文件")
    
    print("\n=== 所有测试完成 ===")
