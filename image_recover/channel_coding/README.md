# 信道解码模块 (Channel Decoding Module)

## 功能描述
信道解码模块负责对传输过来的信道编码数据进行解码，以恢复原始数据。支持多种信道解码算法。

## 模块结构
- `crc_channel_codec/`: CRC信道解码器
- `ldpc_channel_codec/`: LDPC信道解码器
- `polar_channel_codec/`: 极化码信道解码器

## 核心功能
- CRC解码：通过循环冗余校验检测和纠正数据传输错误
- LDPC解码：使用低密度奇偶校验码解码，提高数据传输可靠性
- 极化码解码：利用信道极化特性实现接近香农限的解码性能

## 输入输出
### 输入
- 信道编码后的数据（bytes或numpy数组）

### 输出
- 解码后的数据（bytes或numpy数组）

## 使用示例
```python
# CRC解码示例
from image_recover.channel_coding.crc_channel_codec.crc_decoder import CRCChannelDecoder

crc_decoder = CRCChannelDecoder()
decoded_data = crc_decoder.decode(encoded_data)

# LDPC解码示例
from image_recover.channel_coding.ldpc_channel_codec.ldpc_channel_decoder import LDPCChannelDecoder

ldpc_decoder = LDPCChannelDecoder()
decoded_data = ldpc_decoder.decode(encoded_data)

# 极化码解码示例
from image_recover.channel_coding.polar_channel_codec.polar_decoder import PolarDecoder

polar_decoder = PolarDecoder()
decoded_data = polar_decoder.decode(encoded_data)
```