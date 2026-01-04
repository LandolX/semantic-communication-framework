# 图像预处理模块 (Image Preprocessing Module)

一个用于图像预处理的Python模块，提供标准和自定义的图像预处理功能。

## 功能特性

- ✨ 标准图像预处理流程
- 🎨 自定义预处理参数
- 📦 模块化设计，易于集成
- 🎯 支持多种预处理配置

## 目录结构

```
image_process/
├── image_preprocessor.py     # 预处理核心实现
├── test_image_process.py     # 测试脚本，验证预处理功能
└── README.md                 # 本文件
```

## 安装依赖

```bash
pip install pillow numpy
```

## 使用方法

### 1. 导入模块

```python
from image_preprocessor import preprocess_image, preprocess_image_custom
from PIL import Image
```

### 2. 加载并预处理图像

```python
# 方法1: 使用标准预处理
from PIL import Image
import os

# 加载图像
image_path = "path/to/your/image.jpg"
img = Image.open(image_path)

# 标准预处理
preprocessed_img = preprocess_image(img)
print(f"预处理后图像形状: {preprocessed_img.shape}")  # (1, 224, 224, 1)

# 方法2: 使用自定义预处理
custom_preprocessed_img = preprocess_image_custom(
    img, 
    target_size=(256, 256),  # 自定义尺寸
    normalize=True,          # 归一化
    expand_dims=True         # 扩展维度
)
print(f"自定义预处理后图像形状: {custom_preprocessed_img.shape}")  # (1, 256, 256, 1)
```

### 3. 与数据输入模块配合使用

```python
# 导入数据输入模块
from data_input.image_loader import load_images_from_dir
# 导入预处理模块（同一目录）
from image_preprocessor import preprocess_image
import os

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.dirname(current_dir)

# 加载原始图像（相对路径）
image_dir = os.path.join(project_root, 'data_input', 'image')
original_images = load_images_from_dir(image_dir)

# 对每张图像进行预处理
for i, img in enumerate(original_images):
    # 转换为PIL Image对象
    from PIL import Image
    pil_img = Image.fromarray(img)
    
    # 进行预处理
    preprocessed_img = preprocess_image(pil_img)
    print(f"图像 {i+1}: 原始形状 = {img.shape}, 预处理后形状 = {preprocessed_img.shape}")
    
    if i >= 2:  # 只处理前3张
        break
```

## API 说明

### 1. `preprocess_image(image)`
- **功能**：标准图像预处理流程
- **参数**：`image` - PIL Image对象
- **返回**：预处理后的图像数组
- **预处理步骤**：
  1. 转换为灰度图
  2. 调整为统一尺寸 (224x224)
  3. 归一化到 [0, 1] 范围
  4. 添加批次和通道维度 (形状: (1, 224, 224, 1))

### 2. `preprocess_image_custom(image, target_size=(224, 224), normalize=True, expand_dims=True)`
- **功能**：自定义图像预处理
- **参数**：
  - `image` - PIL Image对象
  - `target_size` - 目标尺寸，默认为(224, 224)
  - `normalize` - 是否归一化，默认为True
  - `expand_dims` - 是否扩展维度，默认为True
- **返回**：预处理后的图像数组

## 扩展建议

1. **添加数据增强**：在预处理流程中添加旋转、翻转、缩放等数据增强操作
2. **支持彩色图像**：扩展预处理功能，支持彩色图像的预处理
3. **添加多种预处理策略**：根据不同任务需求，提供多种预处理策略
4. **优化性能**：添加并行处理，提高批量图像处理效率
5. **添加图像验证**：在预处理前添加图像质量验证

## 许可证

本项目采用 MIT 许可证。