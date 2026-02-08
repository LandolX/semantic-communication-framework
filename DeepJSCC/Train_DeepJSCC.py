import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import os
import random
import torch.nn.functional as F 
import lpips 

# === 固定随机种子 ===
def seed_everything(seed=42):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
seed_everything(42)

# --- 1. 导入 Dataset 和 Model ---
from dataset_DeepJSCC import MedicalDataset
from model_DeepJSCC import DeepJSCC

# --- 2. 导入 SSIM 库 ---
try:
    from pytorch_msssim import ssim
except ImportError:
    raise ImportError("请先安装 SSIM 库: pip install pytorch_msssim")

# --- 3. 配置参数 ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
BATCH_SIZE = 16
LR = 1e-4
EPOCHS = 200

SNR_MIN = -7
SNR_MAX = 20
SEMANTIC_WEIGHT = 50.0

# --- 4. 准备数据 ---
# 训练集
train_dataset = MedicalDataset(img_dir='images_ves_train', mask_dir='masks_ves_train')
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)

# 验证集
val_dataset = MedicalDataset(img_dir='images_ves_test', mask_dir='masks_ves_test')
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

# --- 5. 模型与优化器 ---
model = DeepJSCC(in_channels=1, channel_compression_ratio=0.5).to(DEVICE)
optimizer = optim.Adam(model.parameters(), lr=LR)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=1e-6)

# ==========================================
# 初始化 LPIPS，再冻结参数
# ==========================================
print("正在加载 LPIPS 感知模型...")
perceptual_loss_fn = lpips.LPIPS(net='vgg').to(DEVICE)

# 冻结参数，只做计算
for param in perceptual_loss_fn.parameters():
    param.requires_grad = False

def visual_semantic_loss(output, target, mask):
    # 1. SSIM Loss 
    ssim_val = ssim(output, target, data_range=1.0, size_average=True)
    loss_ssim = 1 - ssim_val

    # 2. 语义加权 Loss 
    pixel_loss = torch.abs(output - target)
    weight_map = 1 + (mask * SEMANTIC_WEIGHT)
    loss_semantic = torch.mean(pixel_loss * weight_map)

    # 3. LPIPS 感知 Loss 
    output_norm = output.repeat(1, 3, 1, 1) * 2 - 1
    target_norm = target.repeat(1, 3, 1, 1) * 2 - 1

    output_small = F.interpolate(output_norm, size=(256, 256), mode='bilinear', align_corners=False)
    target_small = F.interpolate(target_norm, size=(256, 256), mode='bilinear', align_corners=False)
    
    # 计算 loss 
    loss_lpips = perceptual_loss_fn(output_small, target_small).mean()

    # Loss 配方
    total_loss = 0.5 * loss_ssim + 0.2 * loss_semantic + 0.3 * loss_lpips

    return total_loss, loss_ssim.item(), loss_semantic.item(), loss_lpips.item()

# --- 7. 训练循环 ---
print(f" 开始训练 DeepJSCC (with LPIPS)... Device: {DEVICE}")
best_val_loss = float('inf')

for epoch in range(EPOCHS):
    # ================= 训练阶段 =================
    model.train()
    train_loss_meter = 0
    ssim_loss_meter = 0
    sem_loss_meter = 0
    lpips_loss_meter = 0 

    for imgs, masks in train_loader:
        imgs, masks = imgs.to(DEVICE), masks.to(DEVICE)

        optimizer.zero_grad()

        # 训练 SNR 策略
        if epoch < 5:
            current_snr = np.random.uniform(10, 20)
        else:
            current_snr = np.random.uniform(SNR_MIN, SNR_MAX)

        outputs = model(imgs, snr_db=current_snr)

        loss, l_ssim, l_sem, l_lpips = visual_semantic_loss(outputs, imgs, masks)

        loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        optimizer.step()

        train_loss_meter += loss.item()
        ssim_loss_meter += l_ssim
        sem_loss_meter += l_sem
        lpips_loss_meter += l_lpips

    scheduler.step()

    # ================= 验证阶段 =================
    model.eval()
    
    val_snr_list = [-6, 0, 10]
    val_loss_dict = {snr: 0.0 for snr in val_snr_list}
    
    with torch.no_grad():
        for v_imgs, v_masks in val_loader:
            v_imgs, v_masks = v_imgs.to(DEVICE), v_masks.to(DEVICE)
            
            for snr in val_snr_list:
                v_outputs = model(v_imgs, snr_db=float(snr))
                
                v_loss, _, _, _ = visual_semantic_loss(v_outputs, v_imgs, v_masks)
                
                val_loss_dict[snr] += v_loss.item()

    # 计算平均验证 Loss
    avg_loss_neg6 = val_loss_dict[-6] / len(val_loader)
    avg_loss_0 = val_loss_dict[0] / len(val_loader)
    avg_loss_10 = val_loss_dict[10] / len(val_loader)
    
    current_avg_val_loss = (avg_loss_0 + avg_loss_neg6 + avg_loss_10) / 3.0

    # ================= 打印与保存 =================
    avg_train_loss = train_loss_meter / len(train_loader)
    avg_lpips = lpips_loss_meter / len(train_loader) 
    current_lr = scheduler.get_last_lr()[0]

    print(f"Epoch [{epoch + 1}/{EPOCHS}] | "
          f"Train: {avg_train_loss:.4f} (LPIPS: {avg_lpips:.3f}) | "
          f"Val(0dB): {avg_loss_0:.4f} | Val(10dB): {avg_loss_10:.4f} | Val(-6dB): {avg_loss_neg6:.4f} | "
          f"AvgVal: {current_avg_val_loss:.4f} | LR: {current_lr:.2e}")

    # 保存最佳模型 
    if current_avg_val_loss < best_val_loss:
        best_val_loss = current_avg_val_loss
        torch.save(model.state_dict(), "deepjscc_best_v3.pth")
        print(" 发现最佳综合模型 (Best Robust Model)，已保存")

    # 定期保存 Checkpoint
    if (epoch + 1) % 50 == 0:
        torch.save(model.state_dict(), f"deepjscc_epoch_{epoch + 1}_v3.pth")

print("训练完成")
