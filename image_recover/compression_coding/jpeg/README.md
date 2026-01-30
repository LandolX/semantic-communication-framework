# JPEG解码器 (JPEG Decoder)

## 功能描述
JPEG解码器负责将JPEG格式的压缩数据解码为原始图像。JPEG是一种广泛使用的有损压缩图像格式。

## 核心功能
- **JPEG解码**：将JPEG格式数据解码为图像
- **分块解码集成**：可选集成分块解码功能
- **错误处理**：处理解码过程中的错误
- **质量评估**：评估解码图像的质量

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
from image_recover.compression_coding.baseline.jpeg.jpeg_decoder import JPEGDecoder

# 初始化JPEG解码器
jpeg_decoder = JPEGDecoder()

# 解码数据
decoded_image, quality = jpeg_decoder.decode_image(encoded_data)

print(f"解码质量: {quality:.2f}")
```