#!/usr/bin/env python3
"""
测试极化码编解码功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

# 导入编码器和解码器
try:
    from image_process.channel_coding.polar_channel_codec.polar_encoder import PolarEncoder
    from image_recover.channel_coding.polar_channel_codec.polar_decoder import PolarDecoder
    print("✓ 成功导入编码器和解码器")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试编码和解码功能
def test_polar_coding():
    """
    测试极化码编解码功能
    """
    print("\n=== 测试极化码编解码功能 ===")
    
    # 初始化编码器和解码器
    encoder = PolarEncoder(code_rate=0.5)
    decoder = PolarDecoder()
    
    # 测试数据
    test_data = b'Hello, Polar Channel Coding! This is a test message for polar code performance.'
    print(f"原始数据: {test_data}")
    print(f"原始数据长度: {len(test_data)} bytes")
    
    # 编码
    print("\n1. 开始编码...")
    encoded_data = encoder.encode(test_data)
    print(f"编码后数据长度: {len(encoded_data)} bytes")
    print(f"编码后数据前20字节: {encoded_data[:20]}")
    
    # 解码
    print("\n2. 开始解码...")
    decoded_data, status = decoder.decode(encoded_data)
    print(f"解码后数据: {decoded_data}")
    print(f"解码后数据长度: {len(decoded_data)} bytes")
    print(f"解码状态: {'成功' if status else '失败'}")
    
    # 验证解码结果
    print("\n3. 验证解码结果...")
    # 比较时忽略填充的零字节
    # 截取解码数据到原始数据的长度
    truncated_decoded_data = decoded_data[:len(test_data)]
    if truncated_decoded_data == test_data:
        print("✓ 解码成功，数据完全一致！")
        print(f"原始数据长度: {len(test_data)} bytes")
        print(f"解码数据长度: {len(decoded_data)} bytes")
        print(f"截取后解码数据长度: {len(truncated_decoded_data)} bytes")
        return True
    else:
        print("✗ 解码失败，数据不一致！")
        print(f"原始数据: {test_data}")
        print(f"解码数据: {truncated_decoded_data}")
        return False

if __name__ == "__main__":
    success = test_polar_coding()
    if success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 测试失败！")
    sys.exit(0 if success else 1)
