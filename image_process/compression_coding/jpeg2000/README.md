# JPEG2000编码器 (JPEG2000 Encoder)

## 功能描述
JPEG2000编码器负责将图像数据编码为JPEG2000格式，以减少数据传输量。JPEG2000是一种基于小波变换的图像压缩标准，支持无损和有损压缩。

## 核心功能
- **JPEG2000编码**：将图像编码为JPEG2000格式
- **质量控制**：支持调整压缩质量
- **分块编码集成**：可选集成分块编码功能
- **前端预处理**：包含RGB→YUV转换和降噪处理
- **支持无损压缩**：JPEG2000标准支持无损压缩

## 输入输出
### 输入
- `image`: 输入图像，可以是PIL Image对象或numpy数组
- `use_block_codec`: 是否使用分块编码，覆盖构造函数设置
- `lossless`: 是否使用无损压缩，默认False

### 输出
- 编码后的数据（bytes）

## 参数说明
- `quality`: 压缩质量，0-100，默认为90
- `use_block_codec`: 是否使用分块编码，默认False（兼容旧模式）

## 使用示例
```python
from image_process.compression_coding.baseline.jpeg2000.jpeg2000_encoder import JPEG2000Encoder

# 初始化JPEG2000编码器
jpeg2000_encoder = JPEG2000Encoder(quality=90)

# 编码图像
encoded_data = jpeg2000_encoder.encode_image(image)

# 从文件编码
encoded_data = jpeg2000_encoder.encode_from_file('image.jpg')

# 计算压缩比
compression_ratio = jpeg2000_encoder.get_compression_ratio(image, encoded_data)
print(f"压缩比: {compression_ratio:.2f}")
```