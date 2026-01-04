# 5G语义通信框架实现

## 项目概述

这是一个基于5G的语义通信框架实现，支持图像数据的语义编码、传输和恢复。该框架采用模块化设计，包括数据输入、图像处理、数字通信和图像恢复等核心模块，实现了从图像输入到JPEG编码，到信道物理层传输，再到解码恢复的完整流程。

## 目录结构

```
semantic-communication-workplace/
├── baseline/                     # 基线模型实现
│   ├── baseline_pipeline.py      # 传统编码baseline完整流程
├── data_input/                   # 数据输入模块
│   ├── image/                    # 图像文件目录
│   ├── image_loader.py           # 图像加载核心实现
│   ├── usage_example.py          # 使用示例
│   └── README.md                 # 模块说明文档
├── digital_communication_system/  # 数字通信系统模块
│   ├── examples/                 # 示例代码
│   ├── py5g_phy_comm/           # 5G物理层通信实现
│   ├── tests/                    # 测试脚本
│   ├── README.md                 # 模块说明文档
│   └── requirements.txt          # 依赖列表
├── image_process/                # 图像处理模块
│   ├── baseline/                 # 基线编码实现
│   │   └── jpeg_encoder.py       # JPEG编码核心实现
│   ├── image_preprocessor.py     # 图像预处理实现
│   ├── test_image_process.py     # 测试脚本
│   └── README.md                 # 模块说明文档
├── image_recover/                # 图像恢复模块
│   ├── baseline/                 # 基线解码实现
│   │   └── jpeg_decoder.py       # JPEG解码核心实现
│   └── README.md                 # 模块说明文档
├── output/                       # 输出目录，存储恢复的图像
├── README.md                     # 项目说明文档
└── venv/                         # Python虚拟环境
```

## 功能模块

### 1. 数据输入模块 (data_input)
- 负责加载和提供图像数据
- 支持批量加载指定目录下的所有图像
- 提供简洁易用的API接口

### 2. 图像处理模块 (image_process)
- 提供图像预处理功能
- 基线JPEG编码实现
- 支持FEC编码和数据交织

### 3. 数字通信系统模块 (digital_communication_system)
- 5G物理层通信系统仿真
- 支持多种调制方式（BPSK, QPSK, 16QAM, 64QAM）
- 支持多种信道模型（AWGN, Rayleigh, Rician）
- 提供误码率计算

### 4. 图像恢复模块 (image_recover)
- 基线JPEG解码实现
- 容错机制，支持从受损数据中恢复图像
- 黑色区域修复
- FEC编码移除

### 5. 基线流程 (baseline)
- 传统编码baseline完整流程
- 从图像输入到JPEG编码，到信道物理层传输，再到解码恢复

## 安装依赖

```bash
# 安装基础依赖
pip install pillow numpy

# 安装数字通信系统依赖
cd digital_communication_system
pip install -r requirements.txt
cd ..
```

## 使用方法

### 1. 运行基线流程

```bash
# 运行基线流程，处理所有图像
python3 baseline/baseline_pipeline.py
```

### 2. 单独使用各模块

```python
# 示例：数据输入 -> 图像处理 -> 通信系统 -> 图像恢复

from data_input.image_loader import load_images_from_dir
from image_process.baseline.jpeg_encoder import JPEGEncoder
from image_recover.baseline.jpeg_decoder import JPEGDecoder
from digital_communication_system.py5g_phy_comm import create_system
from PIL import Image
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

# 1. 加载图像
image_dir = os.path.join(project_root, 'data_input', 'image')
images = load_images_from_dir(image_dir)

# 2. 初始化编码器和解码器
encoder = JPEGEncoder(quality=90)
decoder = JPEGDecoder()

# 3. 初始化通信系统
system = create_system(
    use_simple=True,
    modulation_type='qpsk',
    snr_dB=14,
    channel_type='awgn'
)

# 4. 处理图像
for i, img_np in enumerate(images):
    # 转换为PIL Image
    img = Image.fromarray(img_np)
    
    # JPEG编码
    jpeg_data = encoder.encode_image(img)
    
    # 通信系统传输
    received_data, ber = system.transmit_receive(jpeg_data)
    
    # JPEG解码
    recovered_image = decoder.decode_image(received_data, return_type='pil', default_size=img.size)
    
    # 保存恢复的图像
    output_path = os.path.join(project_root, 'output', f'recovered_{i}.jpg')
    recovered_image.save(output_path)
    
    print(f"处理完成第{i+1}张图像，误码率: {ber:.6f}")
    if i >= 2:  # 只处理前3张
        break
```

## 核心 API

### 数据输入模块
- `load_images_from_dir(image_dir)`: 加载指定目录下的所有图像
- `get_image_loader(image_dir)`: 获取图像加载器实例

### 图像处理模块
- `preprocess_image(image)`: 标准图像预处理
- `preprocess_image_custom(image, target_size=(224, 224), normalize=True, expand_dims=True)`: 自定义图像预处理
- `JPEGEncoder.encode_image(image)`: 将图像编码为JPEG格式

### 图像恢复模块
- `JPEGDecoder.decode_image(framed_data, return_type='pil', default_size=(776, 776))`: 解码JPEG数据

### 数字通信系统
- `create_system(use_simple=True, modulation_type='qpsk', snr_dB=15, channel_type='awgn')`: 创建通信系统
- `system.transmit_receive(data)`: 传输和接收数据

## 测试与验证

### 运行基线流程测试

```bash
python3 baseline/baseline_pipeline.py
```

### 测试数字通信系统

```bash
cd digital_communication_system
python3 tests/simple_test.py
```

### 测试图像处理模块

```bash
python3 image_process/test_image_process.py
```

## 许可证

本项目采用 MIT 许可证。