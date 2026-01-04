#!/usr/bin/env python3
"""
JPEG解码器 - 传统编码baseline实现
将JPEG格式的bytes数据解码为图像，与数字通信系统对齐
"""

from PIL import Image
import io
import numpy as np
import struct


class JPEGDecoder:
    """
    JPEG解码器类
    """
    
    def __init__(self):
        """
        初始化JPEG解码器
        """
        pass
    
    def _remove_repeated_fec(self, data):
        """
        移除简单的重复FEC编码 - 检测并移除重复的数据
        针对我们的特殊FEC编码方式：前100字节使用2倍重复，其余部分使用1倍重复
        :param data: 包含重复FEC编码的数据
        :return: 移除重复后的原始数据
        """
        if len(data) <= 1:
            return data
        
        # 我们的FEC编码方式：
        # - 如果数据长度 > 100 bytes，前100字节使用2倍重复，其余部分使用1倍重复
        # - 否则，整个数据使用2倍重复
        
        # 检查前100字节是否有重复
        if len(data) > 200 and data[:100] == data[100:200]:
            # 检测到文件头重复
            print("检测到并移除文件头FEC编码")
            # 只保留一个文件头，其余部分不变
            return data[:100] + data[200:]
        elif len(data) > 100 and len(data) % 2 == 0 and data == data[:len(data)//2] * 2:
            # 整个数据重复的情况
            print(f"检测到并移除整个数据重复FEC编码，长度: {len(data)//2} bytes")
            return data[:len(data)//2]
        
        # 没有检测到重复模式，返回原始数据
        return data
    
    def decode_image(self, framed_data, return_type='pil', default_size=(776, 776)):
        """
        解码包含FEC和交织的JPEG数据为图像，带有容错机制
        :param framed_data: 包含FEC和交织的JPEG数据
        :param return_type: 返回类型，'pil'返回PIL Image对象，'numpy'返回numpy数组
        :param default_size: 当解码失败时，生成的默认图像尺寸
        :return: 解码后的图像，如果解码失败则返回灰色替代图像
        """
        # 辅助函数：修复图像中的黑色区域
        def fix_black_regions(image, expected_size):
            """
            修复图像中的黑色区域
            :param image: PIL Image对象
            :param expected_size: 预期的图像尺寸
            :return: 修复后的PIL Image对象
            """
            # 1. 检查图像尺寸
            if image.size != expected_size:
                print(f"图像尺寸不完整，预期: {expected_size}, 实际: {image.size}")
                # 创建灰色背景图像
                fixed_image = Image.new('RGB', expected_size, (128, 128, 128))
                # 居中粘贴原始图像
                paste_x = (expected_size[0] - image.size[0]) // 2
                paste_y = (expected_size[1] - image.size[1]) // 2
                fixed_image.paste(image, (paste_x, paste_y))
                return fixed_image
            
            # 2. 检查黑色区域 - 只在特定条件下修复
            # 正常解码的图像可能本身包含黑色内容，不应被误修复
            # 只有当图像极暗或出现异常情况时才进行黑色区域修复
            image_np = np.array(image)
            
            # 计算图像的平均亮度
            avg_brightness = np.mean(image_np)
            
            # 只有当平均亮度低于10时，才认为是解码错误导致的黑色区域
            # 否则，黑色区域是图像正常内容，不应修复
            if avg_brightness < 10:
                print(f"图像平均亮度极低: {avg_brightness:.2f}，检测黑色区域")
                # 定义黑色阈值范围
                black_low = np.array([0, 0, 0])
                black_high = np.array([10, 10, 10])
                
                # 创建黑色区域掩码
                black_mask = np.all((image_np >= black_low) & (image_np <= black_high), axis=2)
                has_black_pixels = np.any(black_mask)
                
                if has_black_pixels:
                    # 计算黑色像素比例
                    total_pixels = image_np.shape[0] * image_np.shape[1]
                    black_pixels = np.sum(black_mask)
                    black_ratio = black_pixels / total_pixels
                    
                    print(f"检测到黑色区域，黑色像素比例: {black_ratio:.2%}，将其填充为灰色")
                    # 将黑色像素替换为灰色
                    image_np[black_mask] = [128, 128, 128]
                    # 转换回PIL Image
                    return Image.fromarray(image_np)
            
            # 3. 检查平均亮度 - 已在上面检查过，此处不再重复
            # 只有当平均亮度低于10时，才认为解码失败
            if avg_brightness < 10:
                print(f"图像平均亮度: {avg_brightness:.2f}，认为解码失败")
                # 返回灰色替代图像
                return Image.new('RGB', expected_size, (128, 128, 128))
            
            return image
        
        # 策略1：处理带有帧标记的数据
        try:
            # 查找帧标记
            frame_start = framed_data.find(b'JPEG')
            if frame_start != -1:
                # 提取原始JPEG数据长度
                jpeg_len = struct.unpack('>I', framed_data[frame_start+4:frame_start+8])[0]
                print(f"找到帧标记，原始JPEG长度: {jpeg_len} bytes")
                
                # 提取交织的数据部分
                interleaved_data = framed_data[frame_start+8:]
                
                # 1. 去交织处理
                block_size = 16
                # 计算块数
                num_blocks = len(interleaved_data) // block_size
                if len(interleaved_data) % block_size != 0:
                    num_blocks += 1
                
                # 创建空块列表
                deinterleaved_blocks = [b'' for _ in range(num_blocks)]
                
                # 按列重新排列数据（去交织）
                for i, byte in enumerate(interleaved_data):
                    block_idx = i % num_blocks
                    deinterleaved_blocks[block_idx] += bytes([byte])
                
                # 合并去交织后的数据
                deinterleaved_data = b''.join(deinterleaved_blocks)
                
                # 2. 提取原始JPEG数据
                # 从去交织后的数据中提取JPEG数据
                # 查找SOI标记
                soi_pos = deinterleaved_data.find(b'\xFF\xD8')
                if soi_pos != -1:
                    # 查找EOI标记
                    eoi_pos = deinterleaved_data.find(b'\xFF\xD9', soi_pos)
                    if eoi_pos != -1:
                        # 提取完整的JPEG数据
                        jpeg_data = deinterleaved_data[soi_pos:eoi_pos+2]
                        print(f"提取到完整JPEG数据，长度: {len(jpeg_data)} bytes")
                    else:
                        # 没有找到EOI，提取到数据末尾
                        jpeg_data = deinterleaved_data[soi_pos:]
                        print(f"提取到部分JPEG数据（无EOI），长度: {len(jpeg_data)} bytes")
                else:
                    # 没有找到SOI，尝试直接使用去交织后的数据
                    jpeg_data = deinterleaved_data
                    print(f"未找到SOI标记，使用整个去交织数据，长度: {len(jpeg_data)} bytes")
                
                # 3. 移除FEC编码
                jpeg_data = self._remove_repeated_fec(jpeg_data)
                
                # 4. 尝试解码JPEG数据
                try:
                    buffer = io.BytesIO(jpeg_data)
                    image = Image.open(buffer)
                    image.load()
                    buffer.close()
                    
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # 修复黑色区域
                    image = fix_black_regions(image, default_size)
                    
                    print(f"JPEG解码成功，恢复图像尺寸: {image.size}")
                    
                    if return_type == 'numpy':
                        return np.array(image)
                    else:
                        return image
                except Exception as e:
                    print(f"JPEG解码失败: {e}")
        except Exception as e:
            print(f"帧标记解码失败: {e}")
        
        # 策略2：基于JPEG文件格式的天然边界处理
        try:
            # JPEG文件的天然边界
            SOI = b'\xFF\xD8'  # 图像开始标记
            EOI = b'\xFF\xD9'  # 图像结束标记
            
            # 查找所有SOI标记位置
            soi_positions = []
            search_pos = 0
            
            while True:
                soi_pos = framed_data.find(SOI, search_pos)
                if soi_pos == -1:
                    break
                soi_positions.append(soi_pos)
                search_pos = soi_pos + 2  # 移动到SOI标记之后
            
            if not soi_positions:
                print("未找到JPEG文件开始标记(FF D8)")
                raise ValueError("未找到JPEG SOI标记")
            
            print(f"找到 {len(soi_positions)} 个JPEG文件开始标记")
            
            # 对每个SOI标记，查找对应的EOI标记
            for soi_pos in soi_positions:
                # 查找EOI标记，从SOI位置开始
                eoi_pos = framed_data.find(EOI, soi_pos)
                if eoi_pos != -1:
                    # 提取完整的JPEG数据段
                    jpeg_segment = framed_data[soi_pos:eoi_pos + 2]
                else:
                    # 如果没有找到EOI，尝试使用数据末尾
                    print(f"SOI位置 {soi_pos} 未找到EOI标记，尝试使用数据末尾")
                    jpeg_segment = framed_data[soi_pos:]
                
                try:
                    print(f"尝试解码JPEG片段，长度: {len(jpeg_segment)} bytes")
                    # 解码JPEG数据
                    buffer = io.BytesIO(jpeg_segment)
                    image = Image.open(buffer)
                    image.load()  # 确保图像数据完全加载
                    buffer.close()
                    
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # 修复黑色区域
                    image = fix_black_regions(image, default_size)
                    
                    print(f"JPEG解码成功，恢复图像尺寸: {image.size}")
                    
                    if return_type == 'numpy':
                        return np.array(image)
                    else:
                        return image
                except Exception as e:
                    print(f"JPEG片段解码失败: {e}")
                    continue
        except Exception as e:
            print(f"JPEG边界解码失败: {e}")
        
        # 策略3：尝试使用整个数据
        try:
            print("尝试使用整个数据作为JPEG")
            buffer = io.BytesIO(framed_data)
            image = Image.open(buffer)
            image.load()
            buffer.close()
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 修复黑色区域
            image = fix_black_regions(image, default_size)
            
            if return_type == 'numpy':
                return np.array(image)
            else:
                return image
        except Exception as e:
            print(f"整个数据解码失败: {e}")
        
        # 策略4：使用截断图像加载和误码隐藏
        try:
            print("尝试加载截断的JPEG图像并应用误码隐藏")
            from PIL import ImageFile
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            
            # 1. 尝试提取部分有效JPEG数据
            soi_pos = framed_data.find(b'\xFF\xD8')
            if soi_pos != -1:
                # 提取从SOI开始的数据
                jpeg_data = framed_data[soi_pos:]
                
                # 2. 尝试加载截断的JPEG图像
                buffer = io.BytesIO(jpeg_data)
                image = Image.open(buffer)
                image.load()
                buffer.close()
                
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # 修复黑色区域
                image = fix_black_regions(image, default_size)
                
                print(f"截断图像修复成功，恢复图像尺寸: {image.size}")
                
                if return_type == 'numpy':
                    return np.array(image)
                else:
                    return image
        except Exception as e:
            print(f"截断图像加载失败: {e}")
        
        # 最终策略：返回灰色替代图像
        print(f"所有解码策略失败，创建灰色替代图像，尺寸: {default_size}")
        
        gray_color = (128, 128, 128)  # 灰色RGB值
        
        if return_type == 'numpy':
            gray_image = np.full((default_size[1], default_size[0], 3), gray_color, dtype=np.uint8)
            return gray_image
        else:
            gray_image = Image.new('RGB', default_size, gray_color)
            return gray_image
    
    def _decode_blocks(self, framed_data, default_size, return_type):
        """
        块解码策略：解码多个独立的图像块并重组
        """
        import struct
        import zlib
        
        print(f"   尝试块解码策略")
        
        # 1. 读取块信息头
        try:
            # 块信息头格式：[总块数X(2B)] + [总块数Y(2B)] + [块大小(2B)]
            num_blocks_x = struct.unpack('>H', framed_data[0:2])[0]
            num_blocks_y = struct.unpack('>H', framed_data[2:4])[0]
            block_size = struct.unpack('>H', framed_data[4:6])[0]
            
            print(f"   块信息：{num_blocks_x}x{num_blocks_y}块，每块{block_size}x{block_size}")
        except Exception as e:
            print(f"   读取块信息头失败: {e}")
            raise
        
        # 2. 创建空白图像
        width = num_blocks_x * block_size
        height = num_blocks_y * block_size
        result_image = Image.new('RGB', (width, height), (128, 128, 128))  # 灰色背景
        
        # 3. 解码并重组块
        current_pos = 6
        valid_blocks = 0
        total_blocks = num_blocks_x * num_blocks_y
        
        for y in range(num_blocks_y):
            for x in range(num_blocks_x):
                try:
                    # 读取块大小
                    if current_pos + 4 > len(framed_data):
                        print(f"   数据不足，无法读取块 {x},{y} 的大小")
                        break
                    
                    block_jpeg_size = struct.unpack('>I', framed_data[current_pos:current_pos+4])[0]
                    current_pos += 4
                    
                    # 读取CRC32校验和
                    if current_pos + 4 > len(framed_data):
                        print(f"   数据不足，无法读取块 {x},{y} 的CRC32")
                        break
                    
                    expected_crc32 = struct.unpack('>I', framed_data[current_pos:current_pos+4])[0]
                    current_pos += 4
                    
                    # 读取块数据
                    if current_pos + block_jpeg_size > len(framed_data):
                        print(f"   数据不足，无法读取块 {x},{y} 的JPEG数据")
                        break
                    
                    block_jpeg = framed_data[current_pos:current_pos+block_jpeg_size]
                    current_pos += block_jpeg_size
                    
                    # 验证CRC32校验和
                    actual_crc32 = zlib.crc32(block_jpeg) & 0xFFFFFFFF
                    if actual_crc32 != expected_crc32:
                        print(f"   块 {x},{y} CRC32校验失败：预期={expected_crc32:08x}, 实际={actual_crc32:08x}")
                        continue
                    
                    # CRC32校验通过，尝试解码块
                    try:
                        buffer = io.BytesIO(block_jpeg)
                        block_image = Image.open(buffer)
                        block_image.load()  # 确保图像数据加载
                        buffer.close()
                        
                        # 确保块是RGB格式
                        if block_image.mode != 'RGB':
                            block_image = block_image.convert('RGB')
                        
                        # 计算块在结果图像中的位置
                        paste_x = x * block_size
                        paste_y = y * block_size
                        
                        # 粘贴块到结果图像中
                        result_image.paste(block_image, (paste_x, paste_y))
                        valid_blocks += 1
                        print(f"   块 {x},{y} 解码成功")
                    except Exception as e:
                        print(f"   块 {x},{y} CRC32校验通过，但解码失败: {e}")
                        continue
                    
                except Exception as e:
                    # 忽略损坏的块，保持灰色
                    print(f"   块 {x},{y} 处理失败: {e}")
                    continue
        
        print(f"   块解码完成：{valid_blocks}/{total_blocks} 块有效")
        
        # 调整图像大小到默认尺寸
        result_image = result_image.resize(default_size)
        
        # 根据返回类型返回图像
        if return_type == 'numpy':
            return np.array(result_image)
        else:
            return result_image
    
    def _reconstruct_jpeg_data(self, framed_data):
        """
        从分块数据中重建JPEG数据，只使用CRC校验通过的块
        :param framed_data: 分块的JPEG数据
        :return: 重建的JPEG数据
        """
        import struct
        import zlib
        
        # 策略1：尝试从所有可能的位置提取有效JPEG数据
        # 查找所有可能的JPEG文件头
        jpeg_starts = []
        search_pos = 0
        while True:
            # 查找JPEG文件头特征
            header_pos = framed_data.find(b'\xFF\xD8\xFF', search_pos)
            if header_pos == -1:
                break
            jpeg_starts.append(header_pos)
            search_pos = header_pos + 1
        
        if not jpeg_starts:
            # 策略2：尝试直接使用分块数据，不考虑块结构
            print(f"   未找到JPEG文件头，尝试直接使用数据")
            return framed_data
        
        # 尝试从每个可能的头位置提取JPEG数据
        for header_pos in jpeg_starts:
            # 查找文件尾，从当前头位置向后搜索
            footer_pos = framed_data.find(b'\xFF\xD9', header_pos)
            if footer_pos != -1:
                jpeg_data = framed_data[header_pos : footer_pos + 2]
                print(f"   找到JPEG数据段，位置: {header_pos} - {footer_pos + 2}，长度: {len(jpeg_data)} bytes")
                
                # 验证数据有效性
                if self.verify_jpeg_data(jpeg_data):
                    print(f"   直接提取的JPEG数据有效")
                    return jpeg_data
        
        # 策略3：尝试从所有可能的位置提取最大的JPEG数据段
        print(f"   未找到完整有效的JPEG段，尝试提取最大可能段")
        for header_pos in jpeg_starts:
            # 从当前头位置开始，取剩余所有数据
            jpeg_data = framed_data[header_pos:]
            if len(jpeg_data) > 100:  # 至少需要一定长度
                print(f"   尝试使用从位置{header_pos}开始的所有数据，长度: {len(jpeg_data)} bytes")
                return jpeg_data
        
        # 策略4：尝试解析分块数据，只使用有效块
        try:
            print(f"   尝试传统分块解析")
            # 1. 读取总块数
            total_chunks = struct.unpack('>H', framed_data[0:2])[0]
            print(f"   预期总块数: {total_chunks}")
            
            # 2. 提取并验证每个块
            valid_chunks = []
            current_pos = 2
            
            for i in range(total_chunks):
                if current_pos + 6 > len(framed_data):
                    break
                
                try:
                    # 读取块大小
                    chunk_size = struct.unpack('>H', framed_data[current_pos:current_pos+2])[0]
                    
                    # 确保块大小合理
                    if chunk_size > 0 and chunk_size < 10000:  # 防止过大的块
                        # 读取CRC32
                        expected_crc = struct.unpack('>I', framed_data[current_pos+2:current_pos+6])[0]
                        
                        # 确保有足够的数据
                        if current_pos + 6 + chunk_size <= len(framed_data):
                            # 读取块数据
                            chunk_data = framed_data[current_pos+6:current_pos+6+chunk_size]
                            
                            # 计算实际CRC32
                            actual_crc = zlib.crc32(chunk_data) & 0xFFFFFFFF
                            
                            # 验证CRC
                            if actual_crc == expected_crc:
                                valid_chunks.append(chunk_data)
                                print(f"   块 {i+1}: 有效，大小={chunk_size} bytes")
                            else:
                                print(f"   块 {i+1}: CRC不匹配")
                        else:
                            print(f"   块 {i+1}: 数据不足")
                    else:
                        print(f"   块 {i+1}: 无效块大小 {chunk_size}")
                    
                    # 更新当前位置
                    current_pos += 6 + chunk_size
                except Exception as e:
                    print(f"   块 {i+1}: 解析失败 - {e}")
                    # 跳过这个块，尝试下一个可能的位置
                    current_pos += 1
            
            print(f"   有效块数: {len(valid_chunks)}/{total_chunks}")
            
            # 3. 合并有效块
            if len(valid_chunks) > 0:
                jpeg_data = b''.join(valid_chunks)
                print(f"   重建JPEG数据，长度={len(jpeg_data)} bytes")
                return jpeg_data
            else:
                raise ValueError("没有找到有效的块")
                
        except Exception as e:
            print(f"   分块解析失败: {e}")
            # 返回原始数据作为最后尝试
            return framed_data
    
    def decode_to_file(self, jpeg_data, output_path):
        """
        将JPEG格式的bytes数据解码并保存到文件
        :param jpeg_data: JPEG格式的bytes数据
        :param output_path: 输出文件路径
        :return: None
        """
        try:
            # 解码图像
            image = self.decode_image(jpeg_data, return_type='pil')
            
            # 保存图像到文件
            image.save(output_path)
            
            print(f"图像已成功保存到: {output_path}")
            
        except Exception as e:
            print(f"解码并保存图像失败: {e}")
            raise
    
    def verify_jpeg_data(self, jpeg_data):
        """
        验证JPEG数据是否有效
        :param jpeg_data: JPEG格式的bytes数据
        :return: 布尔值，True表示有效，False表示无效
        """
        try:
            # 创建字节流缓冲区
            buffer = io.BytesIO(jpeg_data)
            
            # 尝试打开图像
            image = Image.open(buffer)
            
            # 验证图像格式
            if image.format != 'JPEG':
                return False
            
            # 尝试加载图像数据
            image.load()
            
            # 关闭缓冲区
            buffer.close()
            
            return True
            
        except Exception as e:
            print(f"JPEG数据验证失败: {e}")
            return False


# 便捷函数
def jpeg_decode(jpeg_data, return_type='pil'):
    """
    便捷的JPEG解码函数
    :param jpeg_data: JPEG格式的bytes数据
    :param return_type: 返回类型，'pil'返回PIL Image对象，'numpy'返回numpy数组
    :return: 解码后的图像
    """
    decoder = JPEGDecoder()
    return decoder.decode_image(jpeg_data, return_type)


def jpeg_decode_to_file(jpeg_data, output_path):
    """
    便捷的JPEG解码并保存到文件函数
    :param jpeg_data: JPEG格式的bytes数据
    :param output_path: 输出文件路径
    :return: None
    """
    decoder = JPEGDecoder()
    decoder.decode_to_file(jpeg_data, output_path)


def jpeg_verify(jpeg_data):
    """
    便捷的JPEG数据验证函数
    :param jpeg_data: JPEG格式的bytes数据
    :return: 布尔值，True表示有效，False表示无效
    """
    decoder = JPEGDecoder()
    return decoder.verify_jpeg_data(jpeg_data)


if __name__ == "__main__":
    """
    测试JPEG解码器
    """
    import os
    
    # 将项目根目录添加到sys.path中，确保能够导入其他模块
    import sys
    import os
    # 获取当前文件的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 项目根目录：当前目录 -> image_recover -> semantic-communication-workplace
    project_root = os.path.dirname(os.path.dirname(current_dir))
    # 添加项目根目录到sys.path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 使用绝对路径构建测试图像路径，确保测试能够运行
    test_image_path = os.path.join(project_root, 'data_input', 'image', '1-img-00000-00000_00002.png')
    
    if os.path.exists(test_image_path):
        # 首先编码图像
        from image_process.baseline.jpeg_encoder import jpeg_encode_from_file
        jpeg_data = jpeg_encode_from_file(test_image_path, quality=90)
        print(f"编码成功，JPEG数据大小: {len(jpeg_data)} bytes")
        
        # 创建解码器
        decoder = JPEGDecoder()
        
        # 测试解码为PIL Image对象
        pil_image = decoder.decode_image(jpeg_data, return_type='pil')
        print(f"解码为PIL对象成功，图像模式: {pil_image.mode}, 尺寸: {pil_image.size}")
        
        # 测试解码为numpy数组
        numpy_image = decoder.decode_image(jpeg_data, return_type='numpy')
        print(f"解码为numpy数组成功，形状: {numpy_image.shape}, 数据类型: {numpy_image.dtype}")
        
        # 测试验证功能
        is_valid = decoder.verify_jpeg_data(jpeg_data)
        print(f"JPEG数据验证: {'有效' if is_valid else '无效'}")
        
        # 使用绝对路径构建输出路径，确保测试能够运行
        output_path = os.path.join(project_root, 'output', 'test_decoded.jpg')
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        decoder.decode_to_file(jpeg_data, output_path)
        if os.path.exists(output_path):
            print(f"图像已成功保存到: {output_path}")
        
        # 测试便捷函数
        pil_image2 = jpeg_decode(jpeg_data)
        print(f"便捷函数解码成功，图像模式: {pil_image2.mode}, 尺寸: {pil_image2.size}")
        
    else:
        print(f"测试图像不存在: {test_image_path}")