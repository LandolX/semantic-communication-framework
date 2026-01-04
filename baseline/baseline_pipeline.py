#!/usr/bin/env python3
"""
传统编码baseline完整流程实现
从图像输入到JPEG编码，到信道物理层传输，再到解码恢复的完整流程
"""

import os
import sys
import numpy as np
from PIL import Image

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到系统路径
sys.path.insert(0, project_root)

# 导入JPEG编码模块
from image_process.baseline.jpeg_encoder import JPEGEncoder
# 导入JPEG解码模块
from image_recover.baseline.jpeg_decoder import JPEGDecoder
# 导入数据输入模块
from data_input.image_loader import load_images_from_dir


class BaselinePipeline:
    """
    传统编码baseline完整流程类
    """
    
    def __init__(self, jpeg_quality=90, modulation_type='qpsk', snr_dB=15, channel_type='awgn'):
        """
        初始化baseline流程
        :param jpeg_quality: JPEG压缩质量，0-100
        :param modulation_type: 调制方式，如'qpsk', 'bpsk', '16qam', '64qam'
        :param snr_dB: 信噪比，单位dB
        :param channel_type: 信道类型，如'awgn', 'rayleigh', 'rician'
        """
        # 初始化JPEG编码器和解码器
        self.encoder = JPEGEncoder(quality=jpeg_quality)
        self.decoder = JPEGDecoder()
        
        # 通信系统参数
        self.modulation_type = modulation_type
        self.snr_dB = snr_dB
        self.channel_type = channel_type
        
        # 初始化通信系统
        self.comm_system = None
    
    def _init_comm_system(self):
        """
        初始化通信系统
        """
        try:
            # 导入通信系统创建函数
            from digital_communication_system.py5g_phy_comm import create_system
            
            # 创建通信系统
            self.comm_system = create_system(
                use_simple=True,        # 使用简化版本
                modulation_type=self.modulation_type,  # 调制方式
                snr_dB=self.snr_dB,               # SNR
                channel_type=self.channel_type      # 信道类型
            )
            
            print(f"成功初始化通信系统：{self.modulation_type}调制，{self.snr_dB}dB SNR，{self.channel_type}信道")
            
        except Exception as e:
            print(f"初始化通信系统失败: {e}")
            raise
    
    def calculate_recovery_ratio(self, recovered_image):
        """
        计算恢复图像中非灰色区域的比例
        注意：如果原始图像本身包含灰色像素，这些像素不应被视为恢复失败
        :param recovered_image: 恢复的图像（PIL Image对象）
        :return: 非灰色区域的比例，范围0.0-1.0
        """
        import numpy as np
        
        # 将图像转换为numpy数组
        image_np = np.array(recovered_image)
        
        # 计算图像的平均亮度
        avg_brightness = np.mean(image_np)
        
        # 如果图像平均亮度正常，说明解码成功，恢复比例应为100%
        # 只有当图像极暗或出现异常情况时，才计算灰色区域
        if avg_brightness > 50:  # 正常亮度阈值
            return 1.0
        
        # 对于异常图像，计算非灰色区域比例
        # 定义灰色颜色（RGB值）
        gray_color = np.array([128, 128, 128])
        
        # 计算非灰色像素的数量
        non_gray_mask = np.any(image_np != gray_color, axis=2)
        non_gray_pixels = np.sum(non_gray_mask)
        
        # 计算总像素数量
        total_pixels = image_np.shape[0] * image_np.shape[1]
        
        # 计算恢复比例
        recovery_ratio = non_gray_pixels / total_pixels
        
        return recovery_ratio
    
    def process_image(self, image_path, output_path=None):
        """
        处理单张图像的完整流程
        :param image_path: 输入图像路径
        :param output_path: 输出图像路径，默认为None
        :return: 恢复的图像（PIL Image对象）
        """
        try:
            print(f"\n=== 开始处理图像: {os.path.basename(image_path)} ===")
            
            # 1. 加载图像
            print("1. 加载图像...")
            image = Image.open(image_path)
            print(f"   图像信息: 模式={image.mode}, 尺寸={image.size}")
            
            # 2. JPEG编码
            print("2. JPEG编码...")
            jpeg_data = self.encoder.encode_image(image)
            original_size = os.path.getsize(image_path)
            compressed_size = len(jpeg_data)
            compression_ratio = original_size / compressed_size
            print(f"   编码完成: 原始大小={original_size} bytes, 压缩后大小={compressed_size} bytes, 压缩比={compression_ratio:.2f}:1")
            
            # 3. 初始化通信系统（如果未初始化）
            if self.comm_system is None:
                self._init_comm_system()
            
            # 4. 数字通信系统传输
            print("3. 数字通信系统传输...")
            received_data, ber = self.comm_system.transmit_receive(jpeg_data)
            print(f"   传输完成: 误码率={ber:.6f}")
            
            # 5. JPEG解码 - 传递原始图像尺寸作为默认值，用于容错
            print("4. JPEG解码...")
            recovered_image = self.decoder.decode_image(received_data, return_type='pil', default_size=image.size)
            print(f"   解码完成: 恢复图像模式={recovered_image.mode}, 尺寸={recovered_image.size}")
            
            # 6. 计算恢复比例
            recovery_ratio = self.calculate_recovery_ratio(recovered_image)
            print(f"   恢复比例: {recovery_ratio:.2%}（非灰色区域占总像素的比例）")
            
            # 7. 保存恢复的图像
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
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 加载图像
            images = load_images_from_dir(image_dir)
            
            # 初始化通信系统
            if self.comm_system is None:
                self._init_comm_system()
            
            # 处理每张图像
            image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            for i, (image_file, image_np) in enumerate(zip(image_files, images)):
                try:
                    # 转换为PIL Image对象
                    image = Image.fromarray(image_np)
                    
                    # 生成输出路径
                    output_path = os.path.join(output_dir, f"recovered_{image_file}")
                    
                    # 处理图像
                    print(f"\n--- 处理图像 {i+1}/{len(image_files)}: {image_file} ---")
                    
                    # JPEG编码
                    jpeg_data = self.encoder.encode_image(image)
                    original_size = image_np.nbytes
                    compressed_size = len(jpeg_data)
                    compression_ratio = original_size / compressed_size
                    print(f"   编码完成: 原始大小={original_size} bytes, 压缩后大小={compressed_size} bytes, 压缩比={compression_ratio:.2f}:1")
                    
                    # 通信系统传输
                    received_data, ber = self.comm_system.transmit_receive(jpeg_data)
                    print(f"   传输完成: 误码率={ber:.6f}")
                    
                    # JPEG解码
                    recovered_image = self.decoder.decode_image(received_data, return_type='pil')
                    print(f"   解码完成: 恢复图像模式={recovered_image.mode}, 尺寸={recovered_image.size}")
                    
                    # 计算恢复比例
                    recovery_ratio = self.calculate_recovery_ratio(recovered_image)
                    print(f"   恢复比例: {recovery_ratio:.2%}（非灰色区域占总像素的比例）")
                    
                    # 保存图像
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
            'jpeg_quality': self.encoder.quality,
            'modulation_type': self.modulation_type,
            'snr_dB': self.snr_dB,
            'channel_type': self.channel_type,
            'comm_system_initialized': self.comm_system is not None
        }


# 便捷函数
def run_baseline_pipeline(image_path, output_path, **kwargs):
    """
    运行baseline流程的便捷函数
    :param image_path: 输入图像路径
    :param output_path: 输出图像路径
    :param kwargs: 其他参数
    :return: 恢复的图像
    """
    pipeline = BaselinePipeline(**kwargs)
    return pipeline.process_image(image_path, output_path)


def run_baseline_pipeline_directory(image_dir, output_dir, **kwargs):
    """
    运行baseline流程处理目录的便捷函数
    :param image_dir: 输入图像目录
    :param output_dir: 输出图像目录
    :param kwargs: 其他参数
    """
    pipeline = BaselinePipeline(**kwargs)
    pipeline.process_image_directory(image_dir, output_dir)


if __name__ == "__main__":
    """
    测试baseline流程
    """
    # # 测试单张图像
    # print("=== 测试单张图像处理 ===")
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # # 测试图像路径
    # test_image_path = os.path.join(project_root, 'data_input', 'image', '1-img-00000-00000_00002.png')
    # output_path = os.path.join(project_root, 'output', 'recovered_test.jpg')
    
    # # 运行baseline流程
    # pipeline = BaselinePipeline(
    #     jpeg_quality=90,          # JPEG压缩质量，0-100，值越高质量越好
    #     modulation_type='qpsk',   # 调制方式：'qpsk', 'bpsk', '16qam', '64qam'
    #     snr_dB=13,               # 信噪比，单位dB，测试分块抗干扰机制
    #     channel_type='awgn'      # 信道类型：'awgn', 'rayleigh', 'rician', 'frequency_selective'
    # )
    
    # # 处理单张图像
    # recovered_image = pipeline.process_image(test_image_path, output_path)
    # print(f"恢复图像尺寸: {recovered_image.size}")
    
    # # 测试目录处理
    # print("\n=== 测试目录图像处理 ===")
    image_dir = os.path.join(project_root, 'data_input', 'image')
    output_dir = os.path.join(project_root, 'output')
    
    # 处理所有图像 - 创建新的pipeline实例，避免复用可能有问题的实例
    pipeline2 = BaselinePipeline(
        jpeg_quality=90,          # JPEG压缩质量，0-100，值越高质量越好
        modulation_type='qpsk',   # 调制方式：'qpsk', 'bpsk', '16qam', '64qam'
        snr_dB=14,               # 信噪比，单位dB，值越高通信质量越好
        channel_type='awgn'      # 信道类型：'awgn', 'rayleigh', 'rician', 'frequency_selective'
    )
    
    # 获取图像文件列表
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))][:]
    
    # 处理所有图像
    for i, image_file in enumerate(image_files):
        image_path = os.path.join(image_dir, image_file)
        output_path = os.path.join(output_dir, f"recovered_{image_file}.jpg")
        try:
            pipeline2.process_image(image_path, output_path)
        except Exception as e:
            print(f"处理图像 {image_file} 失败: {e}")
            continue
    
    print("\n=== 测试完成 ===")