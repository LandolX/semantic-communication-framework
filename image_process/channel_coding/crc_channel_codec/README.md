# CRC信道编码器 (CRC Channel Encoder)

## 功能描述
CRC信道编码器负责对数据进行循环冗余校验（CRC）编码，以检测数据传输过程中的错误。

## 核心功能
- **CRC编码**：为数据添加CRC校验码
- **CRC校验**：验证数据传输是否正确
- **多种CRC多项式**：支持多种标准CRC多项式

## 输入输出
### 输入
- `data`: 原始数据（bytes或numpy数组）

### 输出
- 编码后的数据（bytes），包含原始数据和CRC校验码

## 参数说明
- `crc_polynomial`: CRC多项式，默认使用CRC-32多项式（0xEDB88320）
- `crc_width`: CRC宽度，默认32位

## 使用示例
```python
from image_process.channel_coding.crc_channel_codec.crc_encoder import CRCChannelEncoder

# 初始化CRC编码器
crc_encoder = CRCChannelEncoder()

# 编码数据
test_data = b'Hello, CRC!'
encoded_data = crc_encoder.encode(test_data)

# 获取CRC信息
crc_info = crc_encoder.get_crc_info()
print(f"CRC多项式: {crc_info['crc_polynomial']}")
print(f"CRC宽度: {crc_info['crc_width']}")
```