# py5g_phy_comm

5G物理层通信系统仿真模块，支持多种调制方式和信道模型，用于快速构建和测试通信系统。

## 依赖项

```bash
pip install -r requirements.txt
```

## 最简使用示例

### 1. 基本通信仿真

```python
# 添加当前目录到Python路径
import sys
sys.path.append('../')

# 从py5g_phy_comm包导入create_system函数
from py5g_phy_comm import create_system

# 创建通信系统
system = create_system(
    use_simple=True,        # 使用简化版本（无OFDM）
    modulation_type='qpsk',  # 使用QPSK调制
    snr_dB=15,               # 设置SNR为15 dB
    channel_type='awgn'      # 使用AWGN信道
)

# 定义要传输的数据
test_data = b"Hello, 5G Physical Layer!"

# 传输和接收数据
received_data, ber = system.transmit_receive(test_data)

# 显示结果
print(f"原始数据: {test_data}")
print(f"接收数据: {received_data}")
print(f"误码率: {ber:.6f}")
print(f"数据正确接收: {test_data == received_data}")
```

### 2. 运行简单测试

```python
from py5g_phy_comm import run_simple_test

# 运行简单测试
result = run_simple_test(
    input_data=b"Simple test message",
    use_simple=True,
    modulation_type='qpsk',
    snr_dB=10,
    channel_type='awgn'
)
```

## 配置选项

### 调制方式

支持的调制方式：
- `bpsk`：二进制相移键控
- `qpsk`：正交相移键控
- `16qam`：16正交振幅调制
- `64qam`：64正交振幅调制
- `256qam`：256正交振幅调制

```python
# 切换调制方式
system.set_modulation_type('16qam')
```

### 信道模型

支持的信道模型：
- `awgn`：加性高斯白噪声信道
- `rayleigh`：瑞利衰落信道
- `rician`：莱斯衰落信道
- `frequency_selective`：频率选择性衰落信道

```python
# 切换信道类型
system.set_channel_type('rayleigh')
```

### SNR设置

可以通过dB设置信噪比：

```python
# 设置SNR为20 dB
system.set_snr_dB(20)
```

### 星座图可视化

支持星座图可视化，显示发送和接收符号的星座分布：

```python
# 可视化星座图
system.visualize_constellation(title='QPSK Constellation - AWGN Channel, SNR=20 dB')
```

## 更复杂的使用示例

### 1. 不同调制方式对比

```python
# 创建系统
system = create_system(use_simple=True, snr_dB=20, channel_type='awgn')

test_data = b"Testing modulation types"

# 测试不同调制方式
for mod_type in ['bpsk', 'qpsk', '16qam', '64qam']:
    system.set_modulation_type(mod_type)
    received_data, ber = system.transmit_receive(test_data)
    print(f"{mod_type.upper()}: BER = {ber:.6f}, 数据匹配: {test_data == received_data}")
```

### 2. 不同信道模型对比

```python
# 创建系统
system = create_system(use_simple=True, modulation_type='qpsk', snr_dB=25)

test_data = b"Testing channel models"

# 测试不同信道模型
for chan_type in ['awgn', 'rayleigh', 'rician']:
    system.set_channel_type(chan_type)
    received_data, ber = system.transmit_receive(test_data)
    print(f"{chan_type.upper()} 信道: BER = {ber:.6f}, 数据匹配: {test_data == received_data}")
```

### 3. SNR性能测试

```python
# 创建系统
system = create_system(use_simple=True, modulation_type='qpsk', channel_type='awgn')

test_data = b"Testing SNR performance"

# 测试不同SNR值
for snr in [0, 5, 10, 15, 20]:
    system.set_snr_dB(snr)
    received_data, ber = system.transmit_receive(test_data)
    print(f"SNR = {snr} dB: BER = {ber:.6f}, 数据匹配: {test_data == received_data}")
```

## 核心组件

- `system.py`：核心通信系统类，集成收发器和信道
- `channel.py`：多种信道模型实现
- `modulation.py`：多种调制方式实现
- `transmitter.py`：发送器实现
- `receiver.py`：接收器实现

## 运行测试

```bash
# 运行简单测试
python ../tests/simple_test.py

# 运行基本示例
python ../examples/basic_example.py

# 运行综合测试
python ../tests/comprehensive_test.py
```