# 压缩解码模块 (Compression Decoding Module)

## 功能描述
压缩解码模块负责对压缩编码的图像数据进行解码，以恢复原始图像。支持多种图像压缩解码算法。

## 模块结构
- `baseline/`: 基础压缩解码实现
  - `h264/`: H.264解码器
  - `jpeg/`: JPEG解码器
  - `jpeg2000/`: JPEG2000解码器
  - `jpeg2000bgr/`: JPEG2000BGR解码器

## 核心功能
- H.264解码：采用H.264标准进行图像解码
- JPEG解码：采用JPEG标准进行图像解码
- JPEG2000解码：采用JPEG2000标准进行图像解码，支持无损压缩
- JPEG2000BGR解码：针对BGR格式图像的JPEG2000解码

## 输入输出
### 输入
- 压缩编码后的数据（bytes）

### 输出
- 解码后的图像（元组），包含：
  - 解码后的图像（numpy数组）
  - 解码质量评估（float）

## 使用示例
```python
# JPEG解码示例
from image_recover.compression_coding.baseline.jpeg.jpeg_decoder import JPEGDecoder

jpeg_decoder = JPEGDecoder()
decoded_image, quality = jpeg_decoder.decode_image(encoded_data)

# H.264解码示例
from image_recover.compression_coding.baseline.h264.h264_decoder import H264Decoder

h264_decoder = H264Decoder()
decoded_image, quality = h264_decoder.decode_image(encoded_data)

# JPEG2000解码示例
from image_recover.compression_coding.baseline.jpeg2000.jpeg2000_decoder import JPEG2000Decoder

jpeg2000_decoder = JPEG2000Decoder()
decoded_image, quality = jpeg2000_decoder.decode_image(encoded_data)

# JPEG2000BGR解码示例
from image_recover.compression_coding.baseline.jpeg2000bgr.jpeg2000bgr_decoder import JPEG2000BGRDecoder

jpeg2000bgr_decoder = JPEG2000BGRDecoder()
decoded_image, quality = jpeg2000bgr_decoder.decode_image(encoded_data)
```