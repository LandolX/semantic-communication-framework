import torch
import torch.nn as nn


class ChannelAttention(nn.Module):
    def __init__(self, in_planes, ratio=16):
        super(ChannelAttention, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.fc1 = nn.Conv2d(in_planes, in_planes // ratio, 1, bias=False)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Conv2d(in_planes // ratio, in_planes, 1, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = self.fc2(self.relu1(self.fc1(self.avg_pool(x))))
        max_out = self.fc2(self.relu1(self.fc1(self.max_pool(x))))
        out = avg_out + max_out
        return self.sigmoid(out)


class SpatialAttention(nn.Module):
    def __init__(self, kernel_size=7):
        super(SpatialAttention, self).__init__()
        assert kernel_size in (3, 7), 'kernel size must be 3 or 7'
        padding = 3 if kernel_size == 7 else 1
        self.conv1 = nn.Conv2d(2, 1, kernel_size, padding=padding, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        x = torch.cat([avg_out, max_out], dim=1)
        x = self.conv1(x)
        return self.sigmoid(x)


class CBAM(nn.Module):
    def __init__(self, planes):
        super(CBAM, self).__init__()
        self.ca = ChannelAttention(planes)
        self.sa = SpatialAttention()

    def forward(self, x):
        x = x * self.ca(x)
        x = x * self.sa(x)
        return x


class ResBlock(nn.Module):
    def __init__(self, channels):
        super(ResBlock, self).__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.prelu = nn.PReLU()
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        residual = x
        out = self.prelu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        return self.prelu(out)


class DeepJSCC(nn.Module):
    def __init__(self, in_channels=1, channel_compression_ratio=0.5):
        super(DeepJSCC, self).__init__()

        self.C_out = int(channel_compression_ratio * in_channels * 4)
        if self.C_out < 1: self.C_out = 1  # 防止通道为0

        print(
            f"DeepJSCC Configuration: Input={in_channels}, Compression Ratio={channel_compression_ratio}, Latent Channels={self.C_out}")

        # --- Encoder ---
        self.encoder_head = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=9, stride=2, padding=4),
            nn.PReLU(),
            nn.BatchNorm2d(64)
        )
        self.encoder_body = nn.Sequential(
            ResBlock(64),
            ResBlock(64),
            CBAM(64)
        )
        # 使用动态计算的通道数
        self.encoder_tail = nn.Conv2d(64, self.C_out, kernel_size=3, stride=1, padding=1)

        # --- Decoder ---
        self.decoder_head = nn.Sequential(
            nn.ConvTranspose2d(self.C_out, 64, kernel_size=3, stride=1, padding=1),
            nn.PReLU(),
            nn.BatchNorm2d(64)
        )
        self.decoder_body = nn.Sequential(
            ResBlock(64),
            ResBlock(64),
            ResBlock(64),
            CBAM(64)
        )
        self.decoder_tail = nn.Sequential(
            nn.ConvTranspose2d(64, 64, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.PReLU(),
            nn.Conv2d(64, in_channels, kernel_size=3, stride=1, padding=1),
            nn.Sigmoid()  # 确保你的数据 Target 也是 [0, 1] 范围
        )

    def power_normalize(self, feature):

        signal_power = torch.mean(feature ** 2, dim=(1, 2, 3), keepdim=True)
        feature = feature / torch.sqrt(signal_power + 1e-10)
        return feature

    def channel(self, feature, snr_db):
        feature = self.power_normalize(feature)

        # 噪声生成
        noise_power = 10 ** (-snr_db / 10.0)
        noise_std = torch.sqrt(torch.tensor(noise_power, device=feature.device))

        # 生成标准高斯噪声
        noise = torch.randn_like(feature) * noise_std
        return feature + noise

    def forward(self, x, snr_db):
        x = self.encoder_head(x)
        x = self.encoder_body(x)
        feat = self.encoder_tail(x)

        noisy_feat = self.channel(feat, snr_db)

        x = self.decoder_head(noisy_feat)
        x = self.decoder_body(x)
        out = self.decoder_tail(x)

        return out
