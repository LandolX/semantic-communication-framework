# JPEG编码器 (JPEG Encoder)

## 功能描述
JPEG编码器负责将图像数据编码为JPEG格式，以减少数据传输量。JPEG是一种广泛使用的有损压缩图像格式。

## 核心功能
- **JPEG编码**：将图像编码为JPEG格式
- **质量控制**：支持调整压缩质量
- **分块编码集成**：可选集成分块编码功能
- **前端预处理**：包含RGB→YUV转换和降噪处理

## 输入输出
### 输入
- `image`: 输入图像，可以是PIL Image对象或numpy数组
- `use_block_codec`: 是否使用分块编码，覆盖构造函数设置
- `lossless`: 是否使用无损压缩（JPEG不支持，仅作为兼容参数）

### 输出
- 编码后的数据（bytes）

## 参数说明
- `quality`: 压缩质量，0-100，默认为90
- `use_block_codec`: 是否使用分块编码，默认False（兼容旧模式）

## 使用示例
```python
from image_process.compression_coding.baseline.jpeg.jpeg_encoder import JPEGEncoder

# 初始化JPEG编码器
jpeg_encoder = JPEGEncoder(quality=90)

# 编码图像
encoded_data = jpeg_encoder.encode_image(image)

# 从文件编码
encoded_data = jpeg_encoder.encode_from_file('image.jpg')

# 计算压缩比
compression_ratio = jpeg_encoder.get_compression_ratio(image, encoded_data)
print(f"压缩比: {compression_ratio:.2f}")
```