# 图像恢复模块 (Image Recovery Module)

一个用于图像恢复的Python模块，支持多种图像格式的解码和恢复功能，能够从受损的数据中恢复图像。

## 功能特性

- ✨ 支持多种图像解码方式（JPEG, JPEG2000, JPEG2000BGR）
- 🛡️ 容错机制，支持从受损数据中恢复图像
- 📦 模块化设计，易于集成
- 🔄 支持分块解码

## 目录结构

```
image_recover/
├── baseline/                 # 基线解码实现
│   ├── jpeg/                 # JPEG解码实现
│   ├── jpeg2000/            # JPEG2000解码实现
│   └── jpeg2000bgr/          # JPEG2000BGR解码实现
└── README.md               # 本文件
```

## 安装依赖

```bash
pip install pillow numpy
# JPEG2000支持
pip install pyj2k
```

## 使用方法

### 1. 使用JPEG解码器

```python
# 导入JPEG解码器
from image_recover.baseline.jpeg.jpeg_decoder import JPEGDecoder

# 创建JPEG解码器实例（支持分块解码）
decoder = JPEGDecoder(use_block_codec=True)

# 解码JPEG数据
# 假设received_data是从信道接收的JPEG数据
recovered_image = decoder.decode_image(received_data, return_type='pil', default_size=(776, 776))

# 保存恢复的图像
recovered_image.save('recovered_image.jpg')
```

### 2. 使用JPEG2000解码器

```python
# 导入JPEG2000解码器
from image_recover.baseline.jpeg2000.jpeg2000_decoder import JPEG2000Decoder

# 创建JPEG2000解码器实例
decoder = JPEG2000Decoder()

# 解码JPEG2000数据
recovered_image = decoder.decode_image(received_data, return_type='pil', default_size=(776, 776))
```

### 3. 与编码器配合使用

```python
from image_process.baseline.jpeg.jpeg_encoder import JPEGEncoder
from image_recover.baseline.jpeg.jpeg_decoder import JPEGDecoder
from PIL import Image

# 加载图像
img = Image.open("path/to/your/image.jpg")

# 编码图像（使用分块编码）
encoder = JPEGEncoder(quality=90, use_block_codec=True)
encoded_data = encoder.encode_image(img)

# 解码图像（使用分块解码）
decoder = JPEGDecoder(use_block_codec=True)
recovered_image = decoder.decode_image(encoded_data, return_type='pil', default_size=img.size)

# 保存恢复的图像
recovered_image.save('recovered_image.jpg')
```

## API 说明

### 1. JPEGDecoder 类

#### `__init__(use_block_codec=False)`
- 初始化JPEG解码器
- **参数**：
  - `use_block_codec` - 是否使用分块解码

#### `decode_image(data, return_type='pil', default_size=None)`
- **功能**：解码JPEG数据为图像
- **参数**：
  - `data` - JPEG数据
  - `return_type` - 返回类型，'pil'返回PIL Image对象，'numpy'返回numpy数组
  - `default_size` - 当解码失败时，生成的默认图像尺寸
- **返回**：解码后的图像，如果解码失败则返回灰色替代图像

### 2. JPEG2000Decoder 类

#### `__init__(use_block_codec=False)`
- 初始化JPEG2000解码器
- **参数**：
  - `use_block_codec` - 是否使用分块解码

#### `decode_image(data, return_type='pil', default_size=None)`
- **功能**：解码JPEG2000数据为图像
- **参数**：与JPEGDecoder相同
- **返回**：解码后的图像

### 3. JPEG2000BGRDecoder 类

#### `__init__(use_block_codec=False)`
- 初始化JPEG2000BGR解码器
- **参数**：
  - `use_block_codec` - 是否使用分块解码

#### `decode_image(data, return_type='pil', default_size=None)`
- **功能**：解码JPEG2000BGR数据为图像
- **参数**：与JPEGDecoder相同
- **返回**：解码后的图像

## 许可证

本项目采用 MIT 许可证。