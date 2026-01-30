# 极化码信道编码器 (Polar Channel Encoder)

## 功能描述
极化码信道编码器负责对数据进行极化码编码，利用信道极化特性实现接近香农限的编码性能。

## 核心功能
- **极化码编码**：将原始数据编码为极化码
- **灵活的码率配置**：支持不同的编码率
- **高效编码**：采用基于SC（ successive cancellation）的编码算法

## 输入输出
### 输入
- `data`: 原始数据（bytes）

### 输出
- 编码后的数据（bytes）

## 参数说明
- `code_rate`: 编码率，默认0.5
- `block_size`: 块大小，默认256

## 使用示例
```python
from image_process.channel_coding.polar_channel_codec.polar_encoder import PolarEncoder

# 初始化极化码编码器
polar_encoder = PolarEncoder(code_rate=0.5)

# 编码数据
test_data = b'Hello, Polar!'
encoded_data = polar_encoder.encode(test_data)

# 获取极化码信息
polar_info = polar_encoder.get_polar_info()
print(f"编码率: {polar_info['code_rate']}")
print(f"块大小: {polar_info['block_size']}")
```