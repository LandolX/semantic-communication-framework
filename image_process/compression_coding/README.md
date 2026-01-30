# 压缩编码模块 (Compression Coding Module)

## 功能描述
压缩编码模块负责对图像数据进行压缩编码，以减少数据传输量。支持多种图像压缩编码算法。

## 模块结构
- `baseline/`: 基础压缩编码实现
  - `h264/`: H.264编码器
  - `jpeg/`: JPEG编码器
  - `jpeg2000/`: JPEG2000编码器
  - `jpeg2000bgr/`: JPEG2000BGR编码器

## 核心功能
- H.264编码：采用H.264标准进行图像压缩
- JPEG编码：采用JPEG标准进行图像压缩
- JPEG2000编码：采用JPEG2000标准进行图像压缩，支持无损压缩
- JPEG2000BGR编码：针对BGR格式图像的JPEG2000编码

## 输入输出
### 输入
- 图像数据（PIL Image对象或numpy数组）

### 输出
- 压缩编码后的数据（bytes）

## 使用示例
```python
# JPEG编码示例
from image_process.compression_coding.baseline.jpeg.jpeg_encoder import JPEGEncoder

jpeg_encoder = JPEGEncoder(quality=90)
encoded_data = jpeg_encoder.encode_image(image)

# H.264编码示例
from image_process.compression_coding.baseline.h264.h264_encoder import H264Encoder

h264_encoder = H264Encoder(quality=90)
encoded_data = h264_encoder.encode_image(image)

# JPEG2000编码示例
from image_process.compression_coding.baseline.jpeg2000.jpeg2000_encoder import JPEG2000Encoder

jpeg2000_encoder = JPEG2000Encoder(quality=90)
encoded_data = jpeg2000_encoder.encode_image(image)

# JPEG2000BGR编码示例
from image_process.compression_coding.baseline.jpeg2000bgr.jpeg2000bgr_encoder import JPEG2000BGREncoder

jpeg2000bgr_encoder = JPEG2000BGREncoder(quality=90)
encoded_data = jpeg2000bgr_encoder.encode_image(image)
```