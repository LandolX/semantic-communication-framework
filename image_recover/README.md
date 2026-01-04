# 图像恢复模块 (Image Recovery Module)

一个用于图像恢复的Python模块，提供JPEG解码和图像恢复功能，支持从受损的JPEG数据中恢复图像。

## 功能特性

- ✨ JPEG解码功能
- 🛡️ 容错机制，支持从受损数据中恢复图像
- 🎨 黑色区域修复
- 🔄 FEC编码移除
- 📦 模块化设计，易于集成

## 目录结构

```
image_recover/
├── baseline/
│   ├── jpeg_decoder.py     # JPEG解码核心实现
└── README.md               # 本文件
```

## 安装依赖

```bash
pip install pillow numpy
```

## 使用方法

### 1. 导入模块

```python
from image_recover.baseline.jpeg_decoder import JPEGDecoder
```

### 2. 解码JPEG数据

```python
# 创建JPEG解码器实例
decoder = JPEGDecoder()

# 解码JPEG数据
# 假设received_data是从信道接收的带有FEC编码的JPEG数据
recovered_image = decoder.decode_image(received_data, return_type='pil', default_size=(776, 776))

# 保存恢复的图像
recovered_image.save('recovered_image.jpg')
```

### 3. 与其他模块配合使用

```python
from image_process.baseline.jpeg_encoder import JPEGEncoder
from image_recover.baseline.jpeg_decoder import JPEGDecoder
from PIL import Image
import os

# 加载图像
image_path = "path/to/your/image.jpg"
img = Image.open(image_path)

# 编码图像
encoder = JPEGEncoder(quality=90)
encoded_data = encoder.encode_image(img)

# 模拟信道传输（此处省略）
received_data = encoded_data

# 解码图像
decoder = JPEGDecoder()
recovered_image = decoder.decode_image(received_data, return_type='pil', default_size=img.size)

# 保存恢复的图像
recovered_image.save('recovered_image.jpg')
```

## API 说明

### JPEGDecoder 类

#### `__init__()`
- 初始化JPEG解码器

#### `decode_image(framed_data, return_type='pil', default_size=(776, 776))`
- **功能**：解码包含FEC和交织的JPEG数据为图像
- **参数**：
  - `framed_data` - 包含FEC和交织的JPEG数据
  - `return_type` - 返回类型，'pil'返回PIL Image对象，'numpy'返回numpy数组
  - `default_size` - 当解码失败时，生成的默认图像尺寸
- **返回**：解码后的图像，如果解码失败则返回灰色替代图像

#### `decode_to_file(jpeg_data, output_path)`
- **功能**：将JPEG格式的bytes数据解码并保存到文件
- **参数**：
  - `jpeg_data` - JPEG格式的bytes数据
  - `output_path` - 输出文件路径

#### `verify_jpeg_data(jpeg_data)`
- **功能**：验证JPEG数据是否有效
- **参数**：`jpeg_data` - JPEG格式的bytes数据
- **返回**：布尔值，True表示有效，False表示无效

## 核心功能

### 1. FEC编码移除
- 支持移除文件头的2倍重复FEC编码
- 支持移除整个数据的重复FEC编码
- 智能检测FEC编码类型

### 2. 图像恢复
- 支持从受损JPEG数据中恢复图像
- 自动修复黑色区域
- 支持多种解码策略
- 容错机制完善

### 3. 黑色区域修复
- 智能检测接近纯黑的区域
- 只在图像极暗时进行修复
- 避免误处理正常的黑色内容

## 便捷函数

```python
# 便捷的JPEG解码函数
from image_recover.baseline.jpeg_decoder import jpeg_decode, jpeg_decode_to_file, jpeg_verify

# 解码JPEG数据
pil_image = jpeg_decode(jpeg_data)

# 解码并保存到文件
jpeg_decode_to_file(jpeg_data, 'output.jpg')

# 验证JPEG数据
is_valid = jpeg_verify(jpeg_data)
```

## 许可证

本项目采用 MIT 许可证。