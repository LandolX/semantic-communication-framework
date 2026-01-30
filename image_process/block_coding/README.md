# 分块编码模块 (Block Coding Module)

## 功能描述
分块编码模块负责将压缩编码后的数据分割成固定大小的块，并应用前向纠错（FEC）编码，以提高数据传输的可靠性。

## 模块结构
- `block_codec/`: 通用分块编解码器实现

## 核心功能
- 数据分块：将原始数据分割成固定大小的块
- FEC编码：支持重复编码和异或编码两种策略
- 帧标记：为编码数据添加帧标记，便于解码时识别

## 输入输出
### 输入
- 压缩编码后的数据（bytes）
- 编解码器类型（用于生成帧标记）

### 输出
- 分块编码后的数据（bytes），包含帧标记和FEC编码

## 使用示例
```python
from image_process.block_coding.block_codec.block_codec import BlockCodec

# 初始化分块编码器
codec = BlockCodec(block_size=1024, fec_strategy='repetition', fec_level=2)

# 编码数据
encoded_data = codec.encode(compressed_data, 'jpeg')

# 解码数据
decoded_data = codec.decode(encoded_data, 'jpeg')
```