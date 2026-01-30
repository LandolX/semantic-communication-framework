# 通用分块编解码器 (Block Codec)

## 功能描述
通用分块编解码器负责将数据分割成固定大小的块，并应用前向纠错（FEC）编码，以提高数据传输的可靠性。同时支持从编码数据中恢复原始数据。

## 核心功能
- **数据分块**：将原始数据分割成固定大小的块
- **FEC编码**：支持重复编码和异或编码两种策略
- **帧标记生成**：为编码数据添加帧标记，包含编解码器类型、原始数据大小等信息
- **数据重组**：从编码块中恢复原始数据
- **错误恢复**：利用FEC编码恢复丢失或损坏的数据

## 输入输出
### 编码输入
- `data`: 原始数据（bytes）
- `codec_type`: 编解码器类型，用于生成帧标记，如'jpeg'、'jpeg2000'、'jpeg2000bgr'、'h264'

### 编码输出
- 编码后的数据（bytes），包含帧标记和FEC编码

### 解码输入
- `encoded_data`: 编码后的数据（bytes）
- `codec_type`: 编解码器类型，用于验证帧标记

### 解码输出
- 解码后的数据（bytes），如果解码失败返回None

## 参数说明
- `block_size`: 分块大小，单位为字节，默认1024
- `fec_strategy`: FEC编码策略，支持'repetition'（重复编码）、'xor'（异或编码），默认'repetition'
- `fec_level`: FEC编码级别，对于repetition表示重复次数，对于xor表示校验块数量，默认2

## 使用示例
```python
from image_process.block_coding.block_codec.block_codec import BlockCodec

# 初始化分块编码器
codec = BlockCodec(
    block_size=1024,      # 分块大小为1024字节
    fec_strategy='repetition',  # 使用重复编码策略
    fec_level=2           # 重复2次
)

# 编码数据
compressed_data = b'...'  # 压缩编码后的数据
encoded_data = codec.encode(compressed_data, 'jpeg')

# 解码数据
decoded_data = codec.decode(encoded_data, 'jpeg')
```