# JPEG2000BGR编码器 (JPEG2000BGR Encoder)

## 功能描述
JPEG2000BGR编码器负责将BGR格式的图像数据编码为JPEG2000格式，以减少数据传输量。特别适用于OpenCV默认的BGR图像格式。

## 核心功能
- **JPEG2000BGR编码**：将BGR格式图像编码为JPEG2000格式
- **质量控制**：支持调整压缩质量
- **分块编码集成**：可选集成分块编码功能
- **前端预处理**：包含BGR→YUV转换和降噪处理
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
from image_process.compression_coding.baseline.jpeg2000bgr.jpeg2000bgr_encoder import JPEG2000BGREncoder

# 初始化JPEG2000BGR编码器
jpeg2000bgr_encoder = JPEG2000BGREncoder(quality=90)

# 编码图像
encoded_data = jpeg2000bgr_encoder.encode_image(image)

# 从文件编码
encoded_data = jpeg2000bgr_encoder.encode_from_file('image.jpg')

# 计算压缩比
compression_ratio = jpeg2000bgr_encoder.get_compression_ratio(image, encoded_data)
print(f"压缩比: {compression_ratio:.2f}")
```