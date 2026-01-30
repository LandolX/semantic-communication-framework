# 信道编码模块 (Channel Coding Module)

## 功能描述
信道编码模块负责对分块编码后的数据进行信道编码，以提高数据在传输过程中的可靠性。支持多种信道编码算法。

## 模块结构
- `crc_channel_codec/`: CRC信道编码器
- `ldpc_channel_codec/`: LDPC信道编码器
- `polar_channel_codec/`: 极化码信道编码器

## 核心功能
- CRC编码：通过循环冗余校验检测数据传输错误
- LDPC编码：使用低密度奇偶校验码提高数据传输可靠性
- 极化码编码：利用信道极化特性实现接近香农限的编码性能

## 输入输出
### 输入
- 分块编码后的数据（bytes或numpy数组）

### 输出
- 信道编码后的数据（bytes或numpy数组）

## 使用示例
```python
# CRC编码示例
from image_process.channel_coding.crc_channel_codec.crc_encoder import CRCChannelEncoder

crc_encoder = CRCChannelEncoder()
encoded_data = crc_encoder.encode(data)

# LDPC编码示例
from image_process.channel_coding.ldpc_channel_codec.ldpc_channel_encoder import LDPCChannelEncoder

ldpc_encoder = LDPCChannelEncoder()
encoded_data = ldpc_encoder.encode(data)

# 极化码编码示例
from image_process.channel_coding.polar_channel_codec.polar_encoder import PolarEncoder

polar_encoder = PolarEncoder()
encoded_data = polar_encoder.encode(data)
```