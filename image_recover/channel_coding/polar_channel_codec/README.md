# 极化码信道解码器 (Polar Channel Decoder)

## 功能描述
极化码信道解码器负责对极化码编码的数据进行解码，利用信道极化特性实现接近香农限的解码性能。

## 核心功能
- **极化码解码**：将极化码编码数据解码为原始数据
- **错误纠正**：纠正数据传输过程中的错误
- **灵活的码率配置**：支持不同的编码率
- **高效解码**：采用基于SC（ successive cancellation）的解码算法

## 输入输出
### 输入
- `data`: 编码后的数据（bytes）

### 输出
- 解码后的数据（bytes）

## 参数说明
- `code_rate`: 编码率，默认0.5
- `block_size`: 块大小，默认256

## 使用示例
```python
from image_recover.channel_coding.polar_channel_codec.polar_decoder import PolarDecoder

# 初始化极化码解码器
polar_decoder = PolarDecoder(code_rate=0.5)

# 解码数据
test_data = b'Hello, Polar!'  # 假设是极化码编码后的数据
decoded_data = polar_decoder.decode(test_data)

print(f"解码成功: {decoded_data}")
```