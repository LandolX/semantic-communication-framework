# 图像加载器 (Image Loader)

一个用于加载图像的数据输入模块，支持批量加载指定目录下的所有图像，专注于数据输入功能。

## 目录结构

```
data_input/
├── image/              # 存放图像文件的目录
│   ├── 1-img-00000-00000_00002.png
│   ├── 1-img-00000-00001_00002.png
│   └── ...             # 更多图像文件
├── image_loader.py     # 图像加载器核心实现（仅数据输入）
├── usage_example.py    # 使用示例
└── README.md           # 本文件
```

## 安装依赖

```bash
pip install pillow numpy
```

## 使用方法

### 1. 导入模块

```python
from image_loader import load_images_from_dir, get_image_loader
```

### 2. 使用便捷函数加载图像

```python
from image_loader import load_images_from_dir
import os

# 获取图像目录路径
image_dir = os.path.join(os.path.dirname(__file__), 'image')

# 加载原始图像
images = load_images_from_dir(image_dir)

# 循环处理图像
for img in images:
    print(f"图像形状: {img.shape}")
    # 在这里添加你的图像处理逻辑
    # 例如：将图像传递给外部预处理模块
```

### 3. 使用 ImageLoader 类

```python
from image_loader import get_image_loader

# 获取 ImageLoader 实例
loader = get_image_loader(image_dir)

# 显示图像信息
loader.show_image_info()

# 获取图像数量
image_count = loader.get_image_count()
print(f"总图像数量: {image_count}")

# 循环处理图像
for img in loader.load_images():
    print(f"处理图像，形状: {img.shape}")
    # 在这里添加你的处理逻辑
```

## API 说明

### ImageLoader 类

#### `__init__(image_dir)`
- `image_dir`: 图像文件夹路径

#### `load_images()`
- 返回：图像生成器，每次返回一个原始图像（numpy数组）

#### `get_image_count()`
- 返回：图像数量（整数）

#### `show_image_info()`
- 功能：打印图像目录、数量和图像文件列表

### 便捷函数

#### `load_images_from_dir(image_dir)`
- **功能**：直接返回图像生成器
- **参数**：`image_dir` - 图像文件夹路径
- **返回**：图像生成器，每次返回一个原始图像

#### `get_image_loader(image_dir)`
- **功能**：获取 ImageLoader 实例
- **参数**：`image_dir` - 图像文件夹路径
- **返回**：ImageLoader 实例

## 运行示例

```bash
# 运行内置示例
python image_loader.py

# 运行详细使用示例
python usage_example.py
```

## 支持的图像格式

- PNG (.png)
- JPEG (.jpg, .jpeg)
- BMP (.bmp)
- GIF (.gif)

## 适用场景

- 深度学习模型的图像数据输入
- 批量图像读取
- 图像分析和计算机视觉任务的数据源
- 需要专注于数据输入的应用

## 预处理功能

预处理功能已迁移到项目根目录下的 `image_process` 文件夹中。使用时，可将本模块加载的原始图像传递给预处理模块进行处理。

## 许可证

本项目采用 MIT 许可证。