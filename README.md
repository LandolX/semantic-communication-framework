# 5G语义通信框架实现

## 项目概述

这是一个基于5G的语义通信框架实现，支持图像数据的语义编码、传输和恢复。该框架采用模块化设计，包括数据输入、图像处理、数字通信和图像恢复等核心模块，实现了从图像输入到JPEG编码，到信道物理层传输，再到解码恢复的完整流程。

## 目录结构

```
semantic-communication-workplace/
├── advanced_polar_coding/        # 高级极化编码实现
│   ├── decoder/                  # 极化码解码器
│   ├── encoder/                  # 极化码编码器
│   ├── evaluator/                # 极化码评估器
│   └── polar-codes/              # 极化码库
├── baseline/                     # 基线模型实现
│   ├── baseline_pipeline.py      # 传统编码baseline完整流程
│   └── API_DOCUMENTATION.md      # API文档
├── data_input/                   # 数据输入模块
│   ├── image/                    # 图像文件目录
│   ├── tests/                    # 测试脚本
│   ├── README.md                 # 模块说明文档
│   ├── image_loader.py           # 图像加载核心实现
│   └── usage_example.py          # 使用示例
├── digital_communication_system/  # 数字通信系统模块
│   ├── examples/                 # 示例代码
│   ├── py5g_phy_comm/           # 5G物理层通信实现
│   ├── tests/                    # 测试脚本
│   ├── README.md                 # 模块说明文档
│   └── requirements.txt          # 依赖列表
├── evaluation/                   # 评估模块
│   ├── evaluation_main.py        # 评估主脚本
│   ├── generate_charts.py        # 生成图表脚本
│   └── *.png                     # 评估结果图表
├── image_process/                # 图像处理模块
│   ├── block_coding/             # 分块编码实现
│   ├── channel_coding/           # 信道编码实现
│   ├── common/                   # 通用工具
│   ├── compression_coding/       # 压缩编码实现
│   │   ├── h264/                 # H.264编码
│   │   ├── jpeg/                 # JPEG编码
│   │   ├── jpeg2000/             # JPEG2000编码
│   │   └── jpeg2000bgr/          # JPEG2000BGR编码
│   └── README.md                 # 模块说明文档
├── image_recover/                # 图像恢复模块
│   ├── channel_coding/           # 信道编码实现
│   ├── compression_coding/       # 压缩编码实现
│   │   ├── h264/                 # H.264解码
│   │   ├── jpeg/                 # JPEG解码
│   │   ├── jpeg2000/             # JPEG2000解码
│   │   └── jpeg2000bgr/          # JPEG2000BGR解码
│   └── README.md                 # 模块说明文档
├── output/                       # 输出目录，存储恢复的图像
│   └── snr_test/                 # SNR测试结果
├── README.md                     # 项目说明文档
└── venv/                         # Python虚拟环境
```

## 功能模块

### 1. 高级极化编码模块 (advanced_polar_coding)
- 实现了先进的极化码编解码算法
- 提供极化码性能评估工具
- 支持多种极化码配置和优化策略

### 2. 数据输入模块 (data_input)
- 负责加载和提供图像数据
- 支持批量加载指定目录下的所有图像
- 提供简洁易用的API接口

### 3. 图像处理模块 (image_process)
- 支持多种图像编码方式（JPEG, JPEG2000, JPEG2000BGR, H.264）
- 实现了通用的分块编码（block_coding）支持
- 支持信道编码（channel_coding）实现
- 提供通用工具函数（common）

### 4. 数字通信系统模块 (digital_communication_system)
- 5G物理层通信系统仿真
- 支持多种调制方式（BPSK, QPSK, 16QAM, 64QAM, 256QAM）
- 支持多种信道模型（AWGN, Rayleigh, Rician）
- 提供误码率计算
- 支持星座图可视化

### 5. 图像恢复模块 (image_recover)
- 支持多种图像解码方式（JPEG, JPEG2000, JPEG2000BGR, H.264）
- 支持从受损数据中恢复图像
- 支持分块解码和信道解码

### 6. 评估模块 (evaluation)
- 提供编码方案性能评估
- 生成各种性能比较图表
- 支持SNR性能测试和分析

### 7. 基线流程 (baseline)
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

### 3. 使用AWGN信道编码的基线流程

```python
# 使用CRC信道编码的baseline_pipeline使用示例
from baseline.baseline_pipeline import run_baseline_pipeline

run_baseline_pipeline(
    image_path='path/to/image.jpg',
    output_path='path/to/output.jpg',
    compression_type='jpeg2000',
    modulation_type='qpsk',
    snr_dB=25,  # 建议使用较高的SNR以获得更好的CRC校验效果
    channel_type='awgn',
    use_coding=True,  # 启用信道编码
    coding_scheme='crc',  # 使用CRC编码
    crc_type='crc16',  # 使用crc16编码
    visualize_constellation=True
)
```

### 4. 运行数字通信系统示例

```bash
# 运行16QAM调制的通信系统示例
python3 digital_communication_system/examples/demo.py -m 16qam -c awgn -s 20
```

## 核心 API

### 高级极化编码模块
- `PolarEncoder.encode(data)`: 对数据进行极化码编码
- `PolarDecoder.decode(encoded_data)`: 对数据进行极化码解码
- `PolarEvaluator.evaluate()`: 评估极化码性能

### 数据输入模块
- `load_images_from_dir(image_dir)`: 加载指定目录下的所有图像

### 图像处理模块
- 支持多种编码器：`JPEGEncoder`, `JPEG2000Encoder`, `JPEG2000BGREncoder`, `H264Encoder`
- `encoder.encode_image(image)`: 将图像编码为指定格式
- 支持自定义编码质量和分块编码选项

### 图像恢复模块
- 支持多种解码器：`JPEGDecoder`, `JPEG2000Decoder`, `JPEG2000BGRDecoder`, `H264Decoder`
- `decoder.decode_image(data, return_type='pil', default_size=None)`: 解码图像数据

### 数字通信系统
- `create_system(use_simple=True, modulation_type='qpsk', snr_dB=15, channel_type='awgn')`: 创建通信系统
- `system.transmit_receive(data)`: 传输和接收数据
- `system.visualize_constellation(title=None)`: 可视化星座图

### 分块编码
- `BlockCodec.encode(data, codec_type)`: 对数据进行分块编码
- `BlockCodec.decode(encoded_data, codec_type)`: 对数据进行分块解码
- 支持多种FEC编码策略

### 评估模块
- `EvaluationMain.run_evaluation()`: 运行编码方案评估
- `GenerateCharts.plot_performance()`: 生成性能比较图表

## 测试与验证

### 运行基线流程测试

```bash
python3 baseline/baseline_pipeline.py
```

### 测试数字通信系统

```bash
cd digital_communication_system
python3 tests/test_system.py
```

### 测试图像处理模块

```bash
python3 -m pytest image_process/common/tests/
```



### 运行评估模块

```bash
python3 evaluation/evaluation_main.py
```

## 许可证

本项目采用 MIT 许可证。