# 图像处理模块 (Image Processing Module)

用于图像编码和分块编码的Python模块，支持多种图像编码方式、分块编码和信道编码功能，为5G语义通信框架提供图像处理能力。

## 核心功能

- ✨ 多种图像编码方式（JPEG, JPEG2000, H.264）
- 📦 通用分块编码，提高无线传输容错能力
- 🎯 FEC编码策略，增强数据传输可靠性
- 🛡️ 多种信道编码方案（CRC, LDPC, 极化码）
- 🎨 支持无损压缩，确保图像质量

## 目录结构

```
image_process/
├── compression_coding/   # 压缩编码实现
├── block_coding/         # 分块编码实现
├── channel_coding/       # 信道编码实现
├── common/               # 通用工具模块
└── README.md             # 本文件
```

## 安装依赖

```bash
# 基础依赖
pip install pillow numpy

# 可选依赖
# JPEG2000支持
pip install pyj2k
# H.264支持
pip install av
```

## 快速使用

### 1. 图像编码

#### JPEG编码（支持无损压缩）

**输入**：
```python
from PIL import Image
from image_process.compression_coding.baseline.jpeg.jpeg_encoder import JPEGEncoder

# 加载图像
img = Image.open("data_input/image/1-img-00000-00009.png")

# 初始化编码器
encoder = JPEGEncoder(quality=100, use_block_codec=True)

# 编码图像（无损）
data = encoder.encode_image(img, lossless=True)
print(f"输出数据大小: {len(data)} bytes")
```

**输出**：
```
输出数据大小: 520218 bytes
输出数据前10字节: b'BLKJ\x00\x03\xf4\xec\x00\x00'
```

### 2. 分块编码

**输入**：
```python
from image_process.block_coding.block_codec.block_codec import BlockCodec

# 初始化分块编码器
codec = BlockCodec(block_size=1024, fec_strategy='repetition', fec_level=2)

# 编码数据
encoded_data = codec.encode(b"your_data", codec_type='jpeg')
print(f"分块编码后数据大小: {len(encoded_data)} bytes")

# 解码数据
decoded_data = codec.decode(encoded_data, codec_type='jpeg')
print(f"解码后数据: {decoded_data}")
```

### 3. 信道编码

#### 极化码编码

**输入**：
```python
from image_process.channel_coding.polar_channel_codec.polar_encoder import PolarEncoder

# 初始化编码器
encoder = PolarEncoder(code_rate=0.5)

# 编码数据
test_data = b"Hello, Polar Channel Coding!"
encoded_data = encoder.encode(test_data)
print(f"原始数据大小: {len(test_data)} bytes")
print(f"编码后大小: {len(encoded_data)} bytes")
```

**输出**：
```
原始数据大小: 27 bytes
编码后大小: 55 bytes
输出数据前10字节: b'P\x01\x00\x01\xf4\x00\x00\x00\x00\x00'
```

## 核心API

### 图像编码器
- **JPEGEncoder**：JPEG图像编码，支持无损压缩
- **JPEG2000Encoder**：JPEG2000图像编码
- **H264Encoder**：H.264视频编码

### 分块编码器
- **BlockCodec**：通用分块编码，支持FEC编码策略

### 信道编码器
- **CRCEncoder**：CRC信道编码
- **LDPCChannelEncoder**：LDPC信道编码
- **PolarEncoder**：极化码信道编码

## 与其他模块集成

- **data_input**：接收图像数据
- **digital_communication_system**：数据传输
- **image_recover**：图像恢复

## 许可证

MIT 许可证。