#!/usr/bin/env python3
"""
JPEG2000BGR解码器 - 传统编码baseline实现
将JPEG2000BGR格式的bytes数据解码为图像，与数字通信系统对齐
支持分块解码以提升无线传输的容错能力
"""

from PIL import Image
import io
import numpy as np
import struct
import os
import sys

# 导入通用分块编码
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from image_process.block_codec.block_codec import BlockCodec

# 添加common模块到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
baseline_dir = os.path.dirname(current_dir)
if baseline_dir not in sys.path:
    sys.path.insert(0, baseline_dir)


class JPEG2000BGRDecoder:
    """
    JPEG2000BGR解码器类
    """
    
    def __init__(self, use_block_codec=False):
        """
        初始化JPEG2000BGR解码器
        :param use_block_codec: 是否使用分块解码，默认False（兼容旧模式）
        """
        self.use_block_codec = use_block_codec
        # 初始化通用分块解码器
        self.block_codec = BlockCodec()
    
    def _simple_repeat_decode(self, data, repeat):
        """
        简单的重复解码（多数投票）
        兼容旧版本的解码逻辑
        """
        if repeat <= 1:
            return data
        
        decoded = b''
        total_len = len(data)
        for i in range(0, total_len, repeat):
            if i + repeat <= total_len:
                block = data[i:i+repeat]
                byte = max(set(block), key=block.count)
                decoded += bytes([byte])
            else:
                remaining = total_len - i
                if remaining > 0:
                    decoded += data[i:i+remaining]
        return decoded
    
    def _detect_frame_type(self, data):
        """
        检测帧标记类型
        :param data: 输入数据
        :return: (帧类型, 原始数据长度, 数据部分)
        """
        if data.startswith(b'BLKB'):
            return 'block_jpeg2000bgr', struct.unpack('>I', data[4:8])[0], data[8:]
        elif data.startswith(b'JP2B'):
            return 'legacy_jpeg2000bgr', struct.unpack('>I', data[4:8])[0], data[8:]
        return 'unknown', 0, data
    
    def _decode_block_data(self, data, expected_size):
        """
        分块解码 - 使用通用分块解码器
        :param data: 分块编码的数据
        :param expected_size: 期望的原始数据大小
        :return: 解码后的JPEG2000BGR数据
        """
        try:
            # 直接使用传入的完整编码数据进行解码
            # 注意：这里的data已经包含了完整的编码数据（包括帧标记）
            # 所以不需要重新组装，直接调用block_codec.decode即可
            jpeg_data = self.block_codec.decode(data, 'jpeg2000bgr')
            
            if jpeg_data:
                print(f"通用分块解码成功，解码后数据大小: {len(jpeg_data)} bytes")
                return jpeg_data
            else:
                # 回退到简单的重复解码
                print("通用分块解码失败，回退到简单重复解码")
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
                        header_decoded = self._simple_repeat_decode(encoded_header, 4)
                        body_decoded = self._simple_repeat_decode(encoded_body, 2)
                        result = header_decoded + body_decoded
                    else:
                        header_decoded = self._simple_repeat_decode(encoded_header, 4)
                        body_decoded = remaining
                        result = header_decoded + body_decoded
                else:
                    result = self._simple_repeat_decode(data, 3)
                
                if expected_size and len(result) > expected_size:
                    result = result[:expected_size]
                
                return result
            
        except Exception as e:
            print(f"分块解码失败: {e}")
            import traceback
            traceback.print_exc()
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
                    result = header_decoded + remaining
            else:
                result = data
            
            if expected_size and len(result) > expected_size:
                result = result[:expected_size]
            
            return result
            
        except Exception as e:
            print(f"传统FEC解码失败: {e}")
            return data
    
    def _try_open_jpeg2000(self, data):
        """
        尝试以JPEG2000格式打开数据
        :param data: JPEG2000格式的bytes数据
        :return: 打开的Image对象或None
        """
        try:
            buffer = io.BytesIO(data)
            image = Image.open(buffer)
            image.load()
            buffer.close()
            return image
        except Exception:
            return None
    
    def decode_image(self, framed_data, return_type='pil', default_size=(776, 776)):
        """
        解码包含FEC和交织的JPEG2000BGR数据为图像，带有容错机制
        :param framed_data: 包含FEC和交织的JPEG2000BGR数据
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
        
        if frame_type == 'block_jpeg2000bgr' and self.use_block_codec:
            print(f"检测到分块JPEG2000BGR编码，原始大小: {original_size} bytes")
            # 使用完整的framed_data进行解码，而不是分离后的frame_data
            jpeg_data = self.block_codec.decode(framed_data, 'jpeg2000bgr')
            
            if jpeg_data:
                print(f"通用分块解码成功，解码后数据大小: {len(jpeg_data)} bytes")
                image = self._try_open_jpeg2000(jpeg_data)
                if image is not None:
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    recovery_ratio = calculate_recovery_ratio(image, default_size)
                    image = fix_image(image, default_size)
                    
                    print(f"JPEG2000BGR分块解码成功，恢复图像尺寸: {image.size}")
                    
                    if return_type == 'numpy':
                        return np.array(image)[:, :, ::-1], recovery_ratio
                    else:
                        return image, recovery_ratio
                else:
                    print(f"JPEG2000BGR分块解码失败：无法识别图像格式")
                    # 回退到简单的重复解码
                    jpeg_data = self._decode_block_data(frame_data, original_size)
                    if jpeg_data:
                        image = self._try_open_jpeg2000(jpeg_data)
                        if image is not None:
                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                            
                            recovery_ratio = calculate_recovery_ratio(image, default_size)
                            image = fix_image(image, default_size)
                            
                            print(f"JPEG2000BGR分块解码成功（回退），恢复图像尺寸: {image.size}")
                            
                            if return_type == 'numpy':
                                return np.array(image)[:, :, ::-1], recovery_ratio
                            else:
                                return image, recovery_ratio
        elif frame_type == 'legacy_jpeg2000bgr':
            print(f"检测到传统JPEG2000BGR编码，原始大小: {original_size} bytes")
            jpeg_data = self._decode_legacy_data(frame_data, original_size)
            
            if jpeg_data:
                image = self._try_open_jpeg2000(jpeg_data)
                if image is not None:
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    recovery_ratio = calculate_recovery_ratio(image, default_size)
                    image = fix_image(image, default_size)
                    
                    print(f"JPEG2000BGR传统解码成功，恢复图像尺寸: {image.size}")
                    
                    if return_type == 'numpy':
                        return np.array(image)[:, :, ::-1], recovery_ratio
                    else:
                        return image, recovery_ratio
                else:
                    print(f"JPEG2000BGR传统解码失败：无法识别图像格式")
        
        print(f"所有解码策略失败，创建灰色替代图像，尺寸: {default_size}")
        gray_color = (128, 128, 128)
        recovery_ratio = 0.0
        
        if return_type == 'numpy':
            gray_image = np.full((default_size[1], default_size[0], 3), gray_color, dtype=np.uint8)
            return gray_image[:, :, ::-1], recovery_ratio
        else:
            gray_image = Image.new('RGB', default_size, gray_color)
            return gray_image, recovery_ratio
    
    def decode_to_file(self, jpeg2000bgr_data, output_path):
        """
        将JPEG2000BGR格式的bytes数据解码并保存到文件
        :param jpeg2000bgr_data: JPEG2000BGR格式的bytes数据
        :param output_path: 输出文件路径
        :return: None
        """
        try:
            image, _ = self.decode_image(jpeg2000bgr_data, return_type='pil')
            image.save(output_path)
            print(f"图像已成功保存到: {output_path}")
        except Exception as e:
            print(f"解码并保存图像失败: {e}")
            raise
    
    def verify_jpeg2000bgr_data(self, jpeg2000bgr_data):
        """
        验证JPEG2000BGR数据是否有效
        :param jpeg2000bgr_data: JPEG2000BGR格式的bytes数据
        :return: 布尔值，True表示有效，False表示无效
        """
        try:
            buffer = io.BytesIO(jpeg2000bgr_data)
            image = Image.open(buffer)
            image.load()
            buffer.close()
            return image.format in ['JPEG', 'JPEG2000']
        except Exception as e:
            print(f"JPEG2000BGR数据验证失败: {e}")
            return False


def jpeg2000bgr_decode(jpeg2000bgr_data, return_type='pil'):
    """
    便捷的JPEG2000BGR解码函数
    :param jpeg2000bgr_data: JPEG2000BGR格式的bytes数据
    :param return_type: 返回类型，'pil'返回PIL Image对象，'numpy'返回numpy数组
    :return: 解码后的图像
    """
    decoder = JPEG2000BGRDecoder()
    return decoder.decode_image(jpeg2000bgr_data, return_type)


def jpeg2000bgr_decode_to_file(jpeg2000bgr_data, output_path):
    """
    便捷的JPEG2000BGR解码并保存到文件函数
    :param jpeg2000bgr_data: JPEG2000BGR格式的bytes数据
    :param output_path: 输出文件路径
    :return: None
    """
    decoder = JPEG2000BGRDecoder()
    decoder.decode_to_file(jpeg2000bgr_data, output_path)


def jpeg2000bgr_verify(jpeg2000bgr_data):
    """
    便捷的JPEG2000BGR数据验证函数
    :param jpeg2000bgr_data: JPEG2000BGR格式的bytes数据
    :return: 布尔值，True表示有效，False表示无效
    """
    decoder = JPEG2000BGRDecoder()
    return decoder.verify_jpeg2000bgr_data(jpeg2000bgr_data)


if __name__ == "__main__":
    import sys
    import os
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from image_process.baseline.jpeg2000bgr.jpeg2000bgr_encoder import jpeg2000bgr_encode_from_file
    
    test_image_path = os.path.join(project_root, 'data_input', 'image', '1-img-00000-00000_00002.png')
    
    if os.path.exists(test_image_path):
        encoder = JPEG2000BGREncoder(quality=90)
        jp2kbgr_data = encoder.encode_from_file(test_image_path)
        print(f"传统编码: JPEG2000BGR数据大小: {len(jp2kbgr_data)} bytes")
        
        encoder_block = JPEG2000BGREncoder(quality=90, use_block_codec=True)
        jp2kbgr_data_block = encoder_block.encode_from_file(test_image_path)
        print(f"分块编码: JPEG2000BGR数据大小: {len(jp2kbgr_data_block)} bytes")
        
        decoder = JPEG2000BGRDecoder()
        image, ratio = decoder.decode_image(jp2kbgr_data)
        print(f"传统解码恢复比例: {ratio:.2%}")
        
        decoder_block = JPEG2000BGRDecoder(use_block_codec=True)
        image_block, ratio_block = decoder_block.decode_image(jp2kbgr_data_block)
        print(f"分块解码恢复比例: {ratio_block:.2%}")
        
    else:
        print(f"测试图像不存在: {test_image_path}")
