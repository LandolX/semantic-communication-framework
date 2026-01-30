# CRC信道解码器 (CRC Channel Decoder)

## 功能描述
CRC信道解码器负责对CRC编码的数据进行解码，以检测和纠正数据传输过程中的错误。

## 核心功能
- **CRC解码**：从编码数据中提取原始数据
- **CRC校验**：验证数据传输是否正确
- **错误检测**：检测数据传输过程中的错误

## 输入输出
### 输入
- `data`: 编码后的数据（bytes）

### 输出
- 解码后的数据（bytes），如果CRC校验失败返回None

## 参数说明
- `crc_polynomial`: CRC多项式，默认使用CRC-32多项式（0xEDB88320）
- `crc_width`: CRC宽度，默认32位

## 使用示例
```python
from image_recover.channel_coding.crc_channel_codec.crc_decoder import CRCChannelDecoder

# 初始化CRC解码器
crc_decoder = CRCChannelDecoder()

# 解码数据
test_data = b'Hello, CRC!' + b'\x00\x00\x00\x00'  # 假设包含CRC校验码
decoded_data = crc_decoder.decode(test_data)

if decoded_data is not None:
    print(f"解码成功: {decoded_data}")
else:
    print("CRC校验失败，数据可能损坏")
```