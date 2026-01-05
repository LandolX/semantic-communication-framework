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
│   └── README.md                 # 模块说明文档
├── digital_communication_system/  # 数字通信系统模块
│   ├── examples/                 # 示例代码
│   ├── py5g_phy_comm/           # 5G物理层通信实现
│   ├── tests/                    # 测试脚本
│   ├── README.md                 # 模块说明文档
│   └── requirements.txt          # 依赖列表
├── image_process/                # 图像处理模块
│   ├── baseline/                 # 基线编码实现
│   │   ├── jpeg/                 # JPEG编码实现
│   │   ├── jpeg2000/            # JPEG2000编码实现
│   │   └── jpeg2000bgr/          # JPEG2000BGR编码实现
│   ├── block_codec/              # 分块编码实现
│   └── README.md                 # 模块说明文档
├── image_recover/                # 图像恢复模块
│   ├── baseline/                 # 基线解码实现
│   │   ├── jpeg/                 # JPEG解码实现
│   │   ├── jpeg2000/            # JPEG2000解码实现
│   │   └── jpeg2000bgr/          # JPEG2000BGR解码实现
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
- 支持多种图像编码方式（JPEG, JPEG2000, JPEG2000BGR）
- 实现了通用的分块编码（block_codec）支持
- 支持FEC编码策略

### 3. 数字通信系统模块 (digital_communication_system)
- 5G物理层通信系统仿真
- 支持多种调制方式（BPSK, QPSK, 16QAM, 64QAM, 256QAM）
- 支持多种信道模型（AWGN, Rayleigh, Rician）
- 提供误码率计算
- 支持星座图可视化

### 4. 图像恢复模块 (image_recover)
- 支持多种图像解码方式（JPEG, JPEG2000, JPEG2000BGR）
- 支持从受损数据中恢复图像
- 支持分块解码

### 5. 基线流程 (baseline)
- 传统编码baseline完整流程
- 支持多种图像编码方式和调制方式
- 从图像输入到编码，到信道物理层传输，再到解码恢复
- 支持星座图可视化

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

### 2. 带星座图可视化的基线流程

```python
# 带星座图可视化的baseline_pipeline使用示例
from baseline.baseline_pipeline import run_baseline_pipeline

run_baseline_pipeline(
    image_path='path/to/image.jpg',
    output_path='path/to/output.jpg',
    compression_type='jpeg2000',
    modulation_type='16qam',
    snr_dB=20,
    channel_type='awgn',
    visualize_constellation=True  # 启用星座图可视化
)
```

### 3. 运行数字通信系统示例

```bash
# 运行16QAM调制的通信系统示例
python3 digital_communication_system/examples/demo.py -m 16qam -c awgn -s 20
```

## 核心 API

### 数据输入模块
- `load_images_from_dir(image_dir)`: 加载指定目录下的所有图像

### 图像处理模块
- 支持多种编码器：`JPEGEncoder`, `JPEG2000Encoder`, `JPEG2000BGREncoder`
- `encoder.encode_image(image)`: 将图像编码为指定格式
- 支持自定义编码质量和分块编码选项

### 图像恢复模块
- 支持多种解码器：`JPEGDecoder`, `JPEG2000Decoder`, `JPEG2000BGRDecoder`
- `decoder.decode_image(data, return_type='pil', default_size=None)`: 解码图像数据

### 数字通信系统
- `create_system(use_simple=True, modulation_type='qpsk', snr_dB=15, channel_type='awgn')`: 创建通信系统
- `system.transmit_receive(data)`: 传输和接收数据
- `system.visualize_constellation(title=None)`: 可视化星座图

### 分块编码
- `BlockCodec.encode(data, codec_type)`: 对数据进行分块编码
- `BlockCodec.decode(encoded_data, codec_type)`: 对数据进行分块解码
- 支持多种FEC编码策略

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