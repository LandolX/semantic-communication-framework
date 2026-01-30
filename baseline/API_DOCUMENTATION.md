# Baseline Pipeline API 文档

## 1. 概述

Baseline Pipeline 是一个完整的图像通信系统，集成了图像编码、信道编码、数字通信系统传输和解码恢复功能。该系统充分利用了 `digital_communication_system` 模块，实现了高效、可靠的图像传输。

## 2. 核心类

### 2.1 BaselinePipeline

#### 2.1.1 初始化参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| compression_type | str | 'jpeg' | 压缩方式，可选值：'jpeg', 'jpeg2000', 'jpeg2000bgr', 'h264' |
| quality | int | 90 | 压缩质量，范围 0-100 |
| modulation_type | str | 'qpsk' | 调制方式，可选值：'bpsk', 'qpsk', '16qam', '64qam', '256qam' |
| snr_dB | float | 15 | 信噪比，单位 dB |
| channel_type | str | 'awgn' | 信道类型，可选值：'awgn', 'rayleigh', 'rician' |
| use_block_codec | bool | False | 是否使用分块编码 |
| use_coding | bool | False | 是否使用信道编码 |
| coding_scheme | str | 'ldpc' | 信道编码方案，可选值：'crc', 'ldpc' |
| crc_type | str | 'crc16' | CRC编码类型，可选值：'crc8', 'crc16', 'crc32' |
| ldpc_code_rate | float | 1/2 | LDPC编码的码率 |
| visualize_constellation | bool | False | 是否可视化星座图 |
| debug | int | 0 | 调试级别，0：关闭，1：开启 |
| lossless | bool | False | 是否使用无损压缩 |

#### 2.1.2 主要方法

##### process_image

```python
def process_image(self, image_path: str, output_path: str = None) -> PIL.Image.Image:
    """
    处理单张图像的完整流程
    
    参数:
        image_path: 输入图像路径
        output_path: 输出图像路径，默认为None
    
    返回:
        恢复的图像（PIL Image对象）
    """
```

##### process_image_directory

```python
def process_image_directory(self, image_dir: str, output_dir: str) -> None:
    """
    处理目录中的所有图像
    
    参数:
        image_dir: 输入图像目录
        output_dir: 输出图像目录
    """
```

##### get_system_info

```python
def get_system_info(self) -> dict:
    """
    获取系统信息
    
    返回:
        包含系统参数的字典
    """
```

## 3. 信道编码模块

### 3.1 CRC编码

#### 3.1.1 编码器

**类名**: `AWGNChannelEncoder`

**初始化参数**:

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| crc_polynomial | str | 'crc16' | CRC多项式类型 |
| use_channel_codec | bool | True | 是否使用信道编码 |

**编码方法**:

```python
def encode(self, data: bytes) -> bytes:
    """
    对数据进行CRC信道编码
    
    参数:
        data: 原始数据（bytes）
    
    返回:
        编码后的数据（bytes），包含CRC校验位
    """
```

**输入输出示例**:

```python
# 输入
data = b'hello world'

# 编码后输出（示例，实际值根据CRC类型不同而不同）
encoded_data = b'A\x02hello world\x12\x34'  # 包含头信息和CRC
```

#### 3.1.2 解码器

**类名**: `AWGNChannelDecoder`

**初始化参数**:

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| use_channel_codec | bool | True | 是否使用信道编码 |

**解码方法**:

```python
def decode(self, encoded_data: bytes) -> tuple[bytes, bool]:
    """
    对数据进行CRC信道解码
    
    参数:
        encoded_data: 编码后的数据（bytes）
    
    返回:
        (原始数据（bytes）, 解码状态（bool）) 
        解码状态：True表示成功，False表示CRC校验失败
    """
```

### 3.2 LDPC编码

#### 3.2.1 编码器

**类名**: `LDPCChannelEncoder`

**初始化参数**:

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| code_rate | float | 1/2 | 编码码率 |
| use_channel_codec | bool | True | 是否使用信道编码 |

**编码方法**:

```python
def encode(self, data: bytes) -> bytes:
    """
    对数据进行LDPC信道编码
    
    参数:
        data: 原始数据（bytes）
    
    返回:
        编码后的数据（bytes），包含LDPC冗余位
    """
```

**输入输出示例**:

```python
# 输入
data = b'hello world'

# 编码后输出（示例，实际值根据码率不同而不同）
encoded_data = b'L\x01\x00hello world\x56\x78\x9a...'  # 包含头信息和LDPC冗余位
```

#### 3.2.2 解码器

**类名**: `LDPCChannelDecoder`

**初始化参数**:

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| use_channel_codec | bool | True | 是否使用信道编码 |

**解码方法**:

```python
def decode(self, encoded_data: bytes) -> tuple[bytes, bool]:
    """
    对数据进行LDPC信道解码
    
    参数:
        encoded_data: 编码后的数据（bytes）
    
    返回:
        (原始数据（bytes）, 解码状态（bool）) 
        解码状态：True表示成功，False表示解码失败
    """
```

## 4. 数字通信系统集成

### 4.1 通信系统初始化

BaselinePipeline 类使用 `digital_communication_system.py5g_phy_comm.create_system` 函数初始化通信系统，主要参数如下：

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| use_simple | bool | True | 是否使用简化的发送器/接收器 |
| modulation_type | str | 'qpsk' | 调制方式 |
| snr_dB | float | 15 | 信噪比 |
| channel_type | str | 'awgn' | 信道类型 |

### 4.2 传输流程

通信系统的传输流程如下：

1. **编码数据输入**：接收信道编码后的 bytes 数据
2. **发射机处理**：
   - 将 bytes 转换为比特序列
   - 使用指定调制方式进行调制
   - 生成发射信号
3. **信道传播**：
   - 通过指定类型的信道传播
   - 添加相应的噪声
4. **接收机处理**：
   - 接收信号
   - 解调得到符号
   - 符号转换为比特序列
   - 比特序列转换为 bytes 数据
5. **解码数据输出**：返回恢复的 bytes 数据和误码率

## 5. 便捷函数

### 5.1 run_baseline_pipeline

```python
def run_baseline_pipeline(input_path: str = None, output_path: str = None, 
                          visualize_constellation: bool = False, debug: int = 0, 
                          image_path: str = None, lossless: bool = False, **kwargs) -> PIL.Image.Image | None:
    """
    运行baseline流程的便捷函数
    
    参数:
        input_path: 输入图像路径或目录路径
        output_path: 输出图像路径或目录路径
        visualize_constellation: 是否可视化星座图，默认False
        debug: 调试级别，0表示关闭调试输出，1表示开启，默认0
        image_path: 输入图像路径（兼容旧版本参数名）
        lossless: 是否使用无损压缩，默认False
        **kwargs: 其他参数，包括use_coding、coding_scheme、crc_type和ldpc_code_rate
    
    返回:
        处理单张图像时返回恢复的图像，处理目录时返回None
    """
```

## 6. 完整流程

### 6.1 单图像处理流程

```
1. 加载图像
2. 图像编码（JPEG/H264等）
3. 信道编码（CRC/LDPC）
4. 数字通信系统传输：
   - 数据 → 比特 → 调制 → 信道 → 解调 → 比特 → 数据
5. 信道解码
6. 图像解码
7. 保存恢复的图像
```

### 6.2 目录处理流程

```
1. 遍历目录中的所有图像文件
2. 对每个图像执行单图像处理流程
3. 将恢复的图像保存到输出目录
```

## 7. 示例用法

### 7.1 基本用法

```python
from baseline_pipeline import BaselinePipeline

# 创建baseline流程实例
pipeline = BaselinePipeline(
    compression_type='jpeg',           # 使用JPEG编码
    quality=100,                        # 编码质量
    modulation_type='qpsk',            # 使用QPSK调制
    lossless=True,
    snr_dB=15,                          # 15dB SNR
    channel_type='awgn',               # 使用AWGN信道
    use_block_codec=True,             # 使用分块编码
    use_coding=True,                   # 启用信道编码
    coding_scheme='crc',               # 使用CRC编码
    visualize_constellation=False,      # 关闭星座图可视化
    debug=0                             # 关闭调试输出
)

# 处理图像
recovered_image = pipeline.process_image(image_path, output_path)
```

### 7.2 使用便捷函数

```python
from baseline_pipeline import run_baseline_pipeline

# 运行baseline流程
run_baseline_pipeline(
    input_path='input.jpg',
    output_path='output.jpg',
    use_coding=True,
    coding_scheme='ldpc',
    debug=1
)
```

## 8. 系统信息输出

`get_system_info()` 方法返回的系统信息示例：

```python
{
    'compression_type': 'jpeg',
    'quality': 100,
    'use_block_codec': True,
    'use_coding': True,
    'coding_scheme': 'crc',
    'crc_type': 'crc16',
    'ldpc_code_rate': 0.5,
    'modulation_type': 'qpsk',
    'snr_dB': 15,
    'channel_type': 'awgn',
    'comm_system_initialized': True
}
```

## 9. 错误处理

系统在处理过程中可能抛出以下异常：

- `ValueError`: 参数错误或不支持的选项
- `FileNotFoundError`: 输入文件不存在
- `RuntimeError`: 编码/解码失败

建议在使用时添加适当的异常处理：

```python
try:
    recovered_image = pipeline.process_image(image_path, output_path)
except Exception as e:
    print(f"处理图像失败: {e}")
```

## 10. 性能指标

系统运行过程中会输出以下性能指标：

- 压缩比：原始大小 / 压缩后大小
- 误码率（BER）：传输过程中的比特错误率
- 恢复比例：恢复图像中非灰色区域占总像素的比例

这些指标可以帮助评估系统的性能和可靠性。