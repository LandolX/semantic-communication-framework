# LDPC信道解码器 (LDPC Channel Decoder)

## 功能描述
LDPC信道解码器负责对LDPC编码的数据进行解码，以恢复原始数据。LDPC码是一种接近香农限的信道编码方案。

## 核心功能
- **LDPC解码**：将LDPC编码数据解码为原始数据
- **错误纠正**：纠正数据传输过程中的错误
- **灵活的码长和码率**：支持不同的码长和码率配置

## 输入输出
### 输入
- `data`: 编码后的数据（numpy数组， dtype=np.uint8）

### 输出
- 解码后的数据（元组），包含：
  - 解码后的数据（numpy数组， dtype=np.uint8）
  - 解码是否成功（bool）

## 参数说明
- `code_length`: LDPC码长度，默认512
- `code_rate`: 编码率，默认0.5

## 使用示例
```python
import numpy as np
from image_recover.channel_coding.ldpc_channel_codec.ldpc_channel_decoder import LDPCChannelDecoder

# 初始化LDPC解码器
ldpc_decoder = LDPCChannelDecoder()

# 解码数据
test_data = np.random.randint(0, 2, 200, dtype=np.uint8)
decoded_data, success = ldpc_decoder.decode(test_data)

if success:
    print(f"解码成功: {decoded_data}")
else:
    print("解码失败，数据可能损坏严重")
```