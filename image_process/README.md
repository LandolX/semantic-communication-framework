# 图像处理模块 (Image Processing Module)

用于图像编码和分块编码的Python模块，支持多种图像编码方式和通用的分块编码功能。

## 功能特性

- ✨ 支持多种图像编码方式（JPEG, JPEG2000, JPEG2000BGR）
- 📦 实现了通用的分块编码（block_codec）
- 🎯 支持FEC编码策略
- 📁 模块化设计，易于集成

## 目录结构

```
image_process/
├── baseline/                 # 基线编码实现
│   ├── jpeg/                 # JPEG编码实现
│   ├── jpeg2000/            # JPEG2000编码实现
│   └── jpeg2000bgr/          # JPEG2000BGR编码实现
├── block_codec/              # 分块编码实现
│   └── block_codec.py       # 通用分块编码核心实现
└── README.md                 # 本文件
```

## 安装依赖

```bash
pip install pillow numpy
# JPEG2000支持
pip install pyj2k
```

## 使用方法

### 1. 使用图像编码器

```python
# 导入JPEG编码器
from image_process.baseline.jpeg.jpeg_encoder import JPEGEncoder
from PIL import Image

# 加载图像
img = Image.open("path/to/your/image.jpg")

# 初始化编码器（支持分块编码）
encoder = JPEGEncoder(quality=90, use_block_codec=True)

# 编码图像
data = encoder.encode_image(img)
print(f"编码后数据大小: {len(data)} bytes")
```

### 2. 使用分块编码

```python
# 导入分块编码器
from image_process.block_codec.block_codec import BlockCodec

# 初始化分块编码器
codec = BlockCodec(block_size=1024, fec_strategy='repetition', fec_level=2)

# 对数据进行分块编码
encoded_data = codec.encode(b"your_data", codec_type='jpeg')
print(f"分块编码后数据大小: {len(encoded_data)} bytes")

# 解码分块数据
decoded_data = codec.decode(encoded_data, codec_type='jpeg')
print(f"解码后数据: {decoded_data}")
```

## API 说明

### 1. 图像编码器

#### JPEGEncoder
- **功能**：JPEG图像编码
- **参数**：
  - `quality` - 编码质量 (0-100)
  - `use_block_codec` - 是否使用分块编码
- **方法**：
  - `encode_image(image)` - 编码图像

#### JPEG2000Encoder
- **功能**：JPEG2000图像编码
- **参数**：
  - `quality` - 编码质量 (0-100)
  - `use_block_codec` - 是否使用分块编码
- **方法**：
  - `encode_image(image)` - 编码图像

#### JPEG2000BGREncoder
- **功能**：JPEG2000BGR图像编码
- **参数**：
  - `quality` - 编码质量 (0-100)
  - `use_block_codec` - 是否使用分块编码
- **方法**：
  - `encode_image(image)` - 编码图像

### 2. 分块编码器

#### BlockCodec
- **功能**：通用分块编码，支持FEC
- **参数**：
  - `block_size` - 块大小
  - `fec_strategy` - FEC策略 ('repetition'等)
  - `fec_level` - FEC级别
- **方法**：
  - `encode(data, codec_type)` - 分块编码数据
  - `decode(encoded_data, codec_type)` - 分块解码数据

## 扩展建议

1. **添加更多编码方式**：支持更多图像编码格式
2. **增强FEC策略**：添加更多FEC编码策略
3. **优化分块算法**：提高分块编码的效率
4. **添加编码质量评估**：评估不同编码方式的质量和性能

## 许可证

本项目采用 MIT 许可证。