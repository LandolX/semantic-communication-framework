# JPEG2000解码器 (JPEG2000 Decoder)

## 功能描述
JPEG2000解码器负责将JPEG2000格式的压缩数据解码为原始图像。JPEG2000是一种基于小波变换的图像压缩标准，支持无损压缩。

## 核心功能
- **JPEG2000解码**：将JPEG2000格式数据解码为图像
- **分块解码集成**：可选集成分块解码功能
- **错误处理**：处理解码过程中的错误
- **质量评估**：评估解码图像的质量
- **支持无损压缩**：JPEG2000标准支持无损压缩

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
from image_recover.compression_coding.baseline.jpeg2000.jpeg2000_decoder import JPEG2000Decoder

# 初始化JPEG2000解码器
jpeg2000_decoder = JPEG2000Decoder()

# 解码数据
decoded_image, quality = jpeg2000_decoder.decode_image(encoded_data)

print(f"解码质量: {quality:.2f}")
```