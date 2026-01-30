#!/usr/bin/env python3
"""
H.264解码器 - 传统编码baseline实现
将H.264格式的bytes数据解码为图像，与数字通信系统对齐
支持分块解码以提升无线传输的容错能力
"""

from PIL import Image
import io
import numpy as np
import struct
import os
import sys
import cv2

# 导入通用分块编码和工具模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from image_process.block_coding.block_codec.block_codec import BlockCodec
from image_process.common.utils import simple_repeat_decode


class H264Decoder:
    """
    H.264解码器类
    """
    
    def __init__(self, use_block_codec=False):
        """
        初始化H.264解码器
        :param use_block_codec: 是否使用分块解码，默认False（兼容旧模式）
        """
        self.use_block_codec = use_block_codec
        # 初始化通用分块解码器
        self.block_codec = BlockCodec()
    

    
    def _detect_frame_type(self, data):
        """
        检测帧标记类型
        :param data: 输入数据
        :return: (帧类型, 原始数据长度, 数据部分)
        """
        if data.startswith(b'BLKH'):
            return 'block_h264', struct.unpack('>I', data[4:8])[0], data[8:]
        elif data.startswith(b'H264'):
            return 'legacy_h264', struct.unpack('>I', data[4:8])[0], data[8:]
        return 'unknown', 0, data
    
    def _decode_block_data(self, data, expected_size):
        """
        分块解码 - 使用通用分块解码器
        :param data: 分块编码的数据
        :param expected_size: 期望的原始数据大小
        :return: 解码后的H.264数据
        """
        try:
            # 使用通用分块解码器进行解码
            # 重新组装完整的编码数据（包括帧标记）
            full_data = b'BLKH' + struct.pack('>I', expected_size) + data
            h264_data = self.block_codec.decode(full_data, 'h264')
            
            if h264_data and len(h264_data) <= expected_size:
                return h264_data
            elif h264_data:
                return h264_data[:expected_size]
            else:
                # 回退到简单的重复解码
                if expected_size > 100:
                    header_size = 100
                    body_size = expected_size - 100
                else:
                    header_size = expected_size
                    body_size = 0
                
                encoded_header_size = header_size * 4
                encoded_body_size = body_size * 2 if body_size > 0 else 0
                
                if len(data) >= encoded_header_size + encoded_body_size:
                    encoded_header = data[:encoded_header_size]
                    remaining = data[encoded_header_size:]
                    
                    if encoded_body_size > 0 and len(remaining) >= encoded_body_size:
                        encoded_body = remaining[:encoded_body_size]
                        header_decoded = simple_repeat_decode(encoded_header, 4)
                        body_decoded = simple_repeat_decode(encoded_body, 2)
                        result = header_decoded + body_decoded
                    else:
                        header_decoded = simple_repeat_decode(encoded_header, 4)
                        body_decoded = remaining
                        result = header_decoded + body_decoded
                else:
                    result = simple_repeat_decode(data, 3)
                    
                    if expected_size and len(result) > expected_size:
                        result = result[:expected_size]
                
                return result
            
        except Exception as e:
            print(f"分块解码失败: {e}")
            return b''
    
    def _decode_legacy_data(self, data, expected_size):
        """
        传统FEC解码
        编码器使用: header * 2 + body * 1
        所以需要: header_decoded + body
        """
        try:
            if expected_size > 100:
                header_size = 100
                body_size = expected_size - 100
            else:
                header_size = expected_size
                body_size = 0
            
            encoded_header_size = header_size * 2
            encoded_body_size = body_size if body_size > 0 else 0
            
            if len(data) >= encoded_header_size + encoded_body_size:
                encoded_header = data[:encoded_header_size]
                remaining = data[encoded_header_size:]
                
                if encoded_body_size > 0 and len(remaining) >= encoded_body_size:
                    encoded_body = remaining[:encoded_body_size]
                    header_decoded = self._simple_repeat_decode(encoded_header, 2)
                    result = header_decoded + encoded_body
                else:
                    header_decoded = self._simple_repeat_decode(encoded_header, 2)
                    body_decoded = remaining
                    result = header_decoded + body_decoded
            else:
                result = data
            
            if expected_size and len(result) > expected_size:
                result = result[:expected_size]
            
            return result
            
        except Exception as e:
            print(f"传统FEC解码失败: {e}")
            return data
    
    def _parse_h264_data(self, data):
        """
        解析H.264编码数据，提取切片信息
        :param data: H.264编码数据
        :return: 解析后的图像数据
        """
        try:
            # 检查是否包含H.264帧头
            if not data.startswith(b'H264'):
                return b''
            
            # 解析帧头信息
            total_size = struct.unpack('>I', data[4:8])[0]
            num_slices = struct.unpack('>I', data[8:12])[0]
            width = struct.unpack('>I', data[12:16])[0]
            height = struct.unpack('>I', data[16:20])[0]
            
            # 解析切片数据
            slice_data = data[20:]
            reconstructed_data = b''
            
            current_pos = 0
            for i in range(num_slices):
                if current_pos + 8 > len(slice_data):
                    break
                
                # 解析切片头
                slice_idx = struct.unpack('>I', slice_data[current_pos:current_pos+4])[0]
                slice_len = struct.unpack('>I', slice_data[current_pos+4:current_pos+8])[0]
                current_pos += 8
                
                # 提取切片数据
                if current_pos + slice_len <= len(slice_data):
                    reconstructed_data += slice_data[current_pos:current_pos+slice_len]
                    current_pos += slice_len
            
            return reconstructed_data
            
        except Exception as e:
            print(f"解析H.264数据失败: {e}")
            return b''
    
    def _try_open_h264(self, data):
        """
        尝试以H.264格式打开数据
        :param data: H.264格式的bytes数据
        :return: 打开的Image对象或None
        """
        # 首先检查数据是否为空
        if not data:
            return None
        
        # 尝试使用OpenCV进行H.264解码
        try:
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.264', delete=False) as f:
                f.write(data)
                temp_filename = f.name
            
            # 抑制OpenCV的错误输出
            import cv2
            cv2.setLogLevel(cv2.LOG_LEVEL_ERROR)
            
            cap = cv2.VideoCapture(temp_filename)
            ret, frame = cap.read()
            cap.release()
            
            # 清理临时文件
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            
            if ret:
                # 将BGR格式转换为RGB格式
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # 转换为PIL Image对象
                image = Image.fromarray(frame_rgb)
                return image
        except Exception:
            # 静默处理OpenCV解码失败
            pass
        
        # 如果OpenCV解码失败，尝试使用JPEG解码作为后备方案
        try:
            # 检查数据是否可能是JPEG格式
            if data.startswith(b'\xff\xd8'):
                buffer = io.BytesIO(data)
                image = Image.open(buffer)
                # 尝试加载图像数据
                image.load()
                buffer.close()
                return image
        except Exception:
            # 静默处理JPEG解码失败
            pass
        
        # 所有解码尝试都失败，返回None
        return None
    
    def decode_image(self, framed_data, return_type='pil', default_size=(776, 776)):
        """
        解码包含FEC和交织的H.264数据为图像，带有容错机制
        :param framed_data: 包含FEC和交织的H.264数据
        :param return_type: 返回类型，'pil'返回PIL Image对象，'numpy'返回numpy数组
        :param default_size: 当解码失败时，生成的默认图像尺寸
        :return: tuple (decoded_image, recovery_ratio)，解码后的图像和恢复比例
        """
        def calculate_recovery_ratio(image, expected_size):
            if image.size != expected_size:
                valid_pixels = image.size[0] * image.size[1]
                total_pixels = expected_size[0] * expected_size[1]
                return valid_pixels / total_pixels
            
            image_np = np.array(image)
            avg_brightness = np.mean(image_np)
            
            if avg_brightness > 50:
                return 1.0
            
            black_low = np.array([0, 0, 0])
            black_high = np.array([10, 10, 10])
            black_mask = np.all((image_np >= black_low) & (image_np <= black_high), axis=2)
            non_black_pixels = np.sum(~black_mask)
            total_pixels = image_np.shape[0] * image_np.shape[1]
            
            return non_black_pixels / total_pixels
        
        def fix_image(image, expected_size):
            if image.size != expected_size:
                fixed_image = Image.new('RGB', expected_size, (128, 128, 128))
                paste_x = (expected_size[0] - image.size[0]) // 2
                paste_y = (expected_size[1] - image.size[1]) // 2
                fixed_image.paste(image, (paste_x, paste_y))
                return fixed_image
            
            image_np = np.array(image)
            avg_brightness = np.mean(image_np)
            
            if avg_brightness < 10:
                black_low = np.array([0, 0, 0])
                black_high = np.array([10, 10, 10])
                black_mask = np.all((image_np >= black_low) & (image_np <= black_high), axis=2)
                if np.any(black_mask):
                    image_np[black_mask] = [128, 128, 128]
                    return Image.fromarray(image_np)
            
            return image
        
        frame_type, original_size, frame_data = self._detect_frame_type(framed_data)
        
        if frame_type == 'block_h264' and self.use_block_codec:
            print(f"检测到分块H.264编码，原始大小: {original_size} bytes")
            # 使用完整的framed_data进行解码，而不是分离后的frame_data
            h264_data = self.block_codec.decode(framed_data, 'h264')
            
            if h264_data:
                print(f"通用分块解码成功，解码后数据大小: {len(h264_data)} bytes")
                # 解析H.264数据
                jpeg_data = self._parse_h264_data(h264_data)
                if jpeg_data:
                    image = self._try_open_h264(jpeg_data)
                    if image is not None:
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        recovery_ratio = calculate_recovery_ratio(image, default_size)
                        image = fix_image(image, default_size)
                        
                        print(f"H.264分块解码成功，恢复图像尺寸: {image.size}")
                        
                        if return_type == 'numpy':
                            return np.array(image), recovery_ratio
                        else:
                            return image, recovery_ratio
                    else:
                        print(f"H.264分块解码失败：无法识别图像格式")
                        # 尝试直接使用解码后的数据
                        image = self._try_open_h264(h264_data)
                        if image is not None:
                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                            
                            recovery_ratio = calculate_recovery_ratio(image, default_size)
                            image = fix_image(image, default_size)
                            
                            print(f"H.264分块解码成功（直接使用解码后数据），恢复图像尺寸: {image.size}")
                            
                            if return_type == 'numpy':
                                return np.array(image), recovery_ratio
                            else:
                                return image, recovery_ratio
                else:
                    print(f"H.264分块解码失败：无法解析H.264数据")
                    # 尝试直接使用解码后的数据
                    image = self._try_open_h264(h264_data)
                    if image is not None:
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        recovery_ratio = calculate_recovery_ratio(image, default_size)
                        image = fix_image(image, default_size)
                        
                        print(f"H.264分块解码成功（直接使用解码后数据），恢复图像尺寸: {image.size}")
                        
                        if return_type == 'numpy':
                            return np.array(image), recovery_ratio
                        else:
                            return image, recovery_ratio
        elif frame_type == 'legacy_h264':
            print(f"检测到传统H.264编码，原始大小: {original_size} bytes")
            h264_data = self._decode_legacy_data(frame_data, original_size)
            
            if h264_data:
                # 解析H.264数据
                jpeg_data = self._parse_h264_data(h264_data)
                if jpeg_data:
                    image = self._try_open_h264(jpeg_data)
                    if image is not None:
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        recovery_ratio = calculate_recovery_ratio(image, default_size)
                        image = fix_image(image, default_size)
                        
                        print(f"H.264传统解码成功，恢复图像尺寸: {image.size}")
                        
                        if return_type == 'numpy':
                            return np.array(image), recovery_ratio
                        else:
                            return image, recovery_ratio
                    else:
                        print(f"H.264传统解码失败：无法识别图像格式")
                else:
                    print(f"H.264传统解码失败：无法解析H.264数据")
        
        # 最终策略：返回灰色替代图像
        print(f"所有解码策略失败，创建灰色替代图像，尺寸: {default_size}")
        gray_color = (128, 128, 128)
        recovery_ratio = 0.0
        
        if return_type == 'numpy':
            gray_image = np.full((default_size[1], default_size[0], 3), gray_color, dtype=np.uint8)
            return gray_image, recovery_ratio
        else:
            gray_image = Image.new('RGB', default_size, gray_color)
            return gray_image, recovery_ratio
    
    def decode_to_file(self, h264_data, output_path):
        """
        将H.264格式的bytes数据解码并保存到文件
        :param h264_data: H.264格式的bytes数据
        :param output_path: 输出文件路径
        :return: None
        """
        try:
            image, _ = self.decode_image(h264_data, return_type='pil')
            image.save(output_path)
            print(f"图像已成功保存到: {output_path}")
        except Exception as e:
            print(f"解码并保存图像失败: {e}")
            raise
    
    def verify_h264_data(self, h264_data):
        """
        验证H.264数据是否有效
        :param h264_data: H.264格式的bytes数据
        :return: 布尔值，True表示有效，False表示无效
        """
        try:
            # 解析H.264数据
            jpeg_data = self._parse_h264_data(h264_data)
            if not jpeg_data:
                return False
            
            # 尝试打开图像
            buffer = io.BytesIO(jpeg_data)
            image = Image.open(buffer)
            image.load()
            buffer.close()
            return True
        except Exception as e:
            print(f"H.264数据验证失败: {e}")
            return False


def h264_decode(h264_data, return_type='pil'):
    """
    便捷的H.264解码函数
    :param h264_data: H.264格式的bytes数据
    :param return_type: 返回类型，'pil'返回PIL Image对象，'numpy'返回numpy数组
    :return: 解码后的图像
    """
    decoder = H264Decoder()
    return decoder.decode_image(h264_data, return_type)


def h264_decode_to_file(h264_data, output_path):
    """
    便捷的H.264解码并保存到文件函数
    :param h264_data: H.264格式的bytes数据
    :param output_path: 输出文件路径
    :return: None
    """
    decoder = H264Decoder()
    decoder.decode_to_file(h264_data, output_path)


def h264_verify(h264_data):
    """
    便捷的H.264数据验证函数
    :param h264_data: H.264格式的bytes数据
    :return: 布尔值，True表示有效，False表示无效
    """
    decoder = H264Decoder()
    return decoder.verify_h264_data(h264_data)


if __name__ == "__main__":
    import sys
    import os
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from image_process.baseline.h264.h264_encoder import h264_encode_from_file
    
    test_image_path = os.path.join(project_root, 'data_input', 'image', '1-img-00000-00000_00002.png')
    
    if os.path.exists(test_image_path):
        # 使用从外部导入的h264_encode_from_file函数进行编码
        h264_data = h264_encode_from_file(test_image_path, quality=90, use_block_codec=False)
        print(f"传统编码: H.264数据大小: {len(h264_data)} bytes")
        
        h264_data_block = h264_encode_from_file(test_image_path, quality=90, use_block_codec=True)
        print(f"分块编码: H.264数据大小: {len(h264_data_block)} bytes")
        
        decoder = H264Decoder()
        image, ratio = decoder.decode_image(h264_data)
        print(f"传统解码恢复比例: {ratio:.2%}")
        
        decoder_block = H264Decoder(use_block_codec=True)
        image_block, ratio_block = decoder_block.decode_image(h264_data_block)
        print(f"分块解码恢复比例: {ratio_block:.2%}")
        
    else:
        print(f"测试图像不存在: {test_image_path}")
