# H.264编码器 (H.264 Encoder)

## 功能描述
H.264编码器负责将图像数据编码为H.264格式，以减少数据传输量。H.264是一种高效的视频压缩标准，也可用于单帧图像压缩。

## 核心功能
- **H.264编码**：将图像编码为H.264格式
- **质量控制**：支持调整压缩质量
- **分块编码集成**：可选集成分块编码功能
- **前端预处理**：包含RGB→YUV420转换和降噪处理
- **宏块分块**：支持宏块级别的分块处理

## 输入输出
### 输入
- `image`: 输入图像，可以是PIL Image对象或numpy数组
- `use_block_codec`: 是否使用分块编码，覆盖构造函数设置
- `lossless`: 是否使用无损压缩（H.264不支持，仅作为兼容参数）

### 输出
- 编码后的数据（bytes）

## 参数说明
- `quality`: 压缩质量，0-100，默认为90
- `use_block_codec`: 是否使用分块编码，默认False（兼容旧模式）

## 使用示例
```python
from image_process.compression_coding.baseline.h264.h264_encoder import H264Encoder

# 初始化H.264编码器
h264_encoder = H264Encoder(quality=90)

# 编码图像
encoded_data = h264_encoder.encode_image(image)

# 从文件编码
encoded_data = h264_encoder.encode_from_file('image.jpg')

# 计算压缩比
compression_ratio = h264_encoder.get_compression_ratio(image, encoded_data)
print(f"压缩比: {compression_ratio:.2f}")
```