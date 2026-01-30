# H.264解码器 (H.264 Decoder)

## 功能描述
H.264解码器负责将H.264格式的压缩数据解码为原始图像。H.264是一种高效的视频压缩标准，也可用于单帧图像压缩。

## 核心功能
- **H.264解码**：将H.264格式数据解码为图像
- **分块解码集成**：可选集成分块解码功能
- **错误处理**：处理解码过程中的错误
- **质量评估**：评估解码图像的质量
- **宏块分块处理**：支持宏块级别的分块处理

## 输入输出
### 输入
- `data`: 编码后的数据（bytes）

### 输出
- 解码后的图像（元组），包含：
  - 解码后的图像（numpy数组）
  - 解码质量评估（float）

## 参数说明
- `use_block_codec`: 是否使用分块解码，默认False（兼容旧模式）

## 使用示例
```python
from image_recover.compression_coding.baseline.h264.h264_decoder import H264Decoder

# 初始化H.264解码器
h264_decoder = H264Decoder()

# 解码数据
decoded_image, quality = h264_decoder.decode_image(encoded_data)

print(f"解码质量: {quality:.2f}")
```