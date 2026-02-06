import torch
import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from PIL import Image
from torchvision import transforms
import os
import math
import random
from tqdm import tqdm


# === 固定随机种子  ===
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

# 引入模型定义
from model_DeepJSCC import DeepJSCC

# ==========================================
#               0. 全局配置
# ==========================================
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL_PATH = 'deepjscc_best.pth'
TEST_IMG_DIR = 'images_ves_test'
TEST_MASK_DIR = 'masks_ves_test'
SAVE_DIR = "results_final_paper_roi_v2"

COMPRESSION_RATIO = 0.5
IN_CHANNELS = 1

# 现实通信限制
CODING_EFFICIENCY = 0.8
MIN_BPP_THRESHOLD = 0.02

# 图像参数
IMG_SIZE = 512

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


# ==========================================
#             1. 工具函数
# ==========================================
def get_k_over_n(model, img_size):
    c_out = model.encoder_tail.out_channels
    feat_h = img_size // 2
    feat_w = img_size // 2

    k_source = 1 * img_size * img_size
    n_channel = c_out * feat_h * feat_w

    k_over_n = n_channel / k_source
    print(f"[*] 模型参数: C_out={c_out}, FeatureMap={feat_h}x{feat_w}")
    print(f"[*] 带宽比 (K/N): {k_over_n:.4f}")
    return k_over_n


def bpp_to_snr(target_bpp, k_over_n):
    if k_over_n == 0: return 0
    exponent = (2 * target_bpp) / k_over_n
    if exponent > 50: exponent = 50
    snr_linear = (2 ** exponent) - 1
    if snr_linear <= 1e-9: return -10.0
    return 10 * math.log10(snr_linear)


def snr_to_bpp(snr_db, k_over_n, efficiency=1.0):
    snr_linear = 10 ** (snr_db / 10.0)
    capacity = 0.5 * math.log2(1 + snr_linear)
    return k_over_n * capacity * efficiency


def to_numpy(tensor_img):
    img = tensor_img.squeeze().cpu().detach().numpy()
    img = (img * 255).clip(0, 255).astype(np.uint8)
    return img


def calc_roi_metrics(img1, img2, mask):
    """
    计算 ROI-SSIM 和 ROI-PSNR
    """
    if img2 is None: return 0.0, 0.0

    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
    num_roi_pixels = np.sum(mask)

    # --- 1. ROI-SSIM 计算 ---
    _, ssim_map = ssim(img1, img2, data_range=255, full=True)

    # 只累加 Mask 区域的 SSIM 值
    if num_roi_pixels < 1:
        roi_ssim = 0.0
    else:
        roi_ssim = np.sum(ssim_map * mask) / num_roi_pixels

    # --- 2. ROI-PSNR 计算 ---
    diff = (img1 - img2)
    diff_roi = diff * mask  # 只保留血管差异

    if num_roi_pixels < 1:
        mse = np.mean(diff ** 2)
    else:
        mse = np.sum(diff_roi ** 2) / num_roi_pixels

    if mse == 0:
        p_roi = 100.0
    else:
        p_roi = 10 * np.log10((255.0 ** 2) / mse)

    return roi_ssim, p_roi


def find_fixed_bpp_jpeg2000(img_np, target_bpp):
    # 1. 悬崖效应判定
    if target_bpp < MIN_BPP_THRESHOLD:
        return None, 0

    h, w = img_np.shape
    total_pixels = h * w

    # === 2. 自动侦测参数方向 ===
    p1 = 100
    p2 = 500
    res1, buf1 = cv2.imencode('.jp2', img_np, [int(cv2.IMWRITE_JPEG2000_COMPRESSION_X1000), p1])
    res2, buf2 = cv2.imencode('.jp2', img_np, [int(cv2.IMWRITE_JPEG2000_COMPRESSION_X1000), p2])

    if not res1 or not res2: return None, 0
    bpp1 = (buf1.size * 8) / total_pixels
    bpp2 = (buf2.size * 8) / total_pixels
    higher_param_gives_larger_file = bpp2 > bpp1

    # === 3. 二分查找 ===
    low = 10
    high = 1000
    best_img = None
    min_diff = float('inf')

    for _ in range(12):
        if low > high: break
        mid = (low + high) // 2

        res, encimg = cv2.imencode('.jp2', img_np, [int(cv2.IMWRITE_JPEG2000_COMPRESSION_X1000), mid])
        if not res:
            low = mid + 1
            continue

        current_bpp = (encimg.size * 8) / total_pixels

        if current_bpp <= target_bpp:
            diff = target_bpp - current_bpp
            if diff < min_diff:
                min_diff = diff
                best_img = cv2.imdecode(encimg, 0)

            if higher_param_gives_larger_file:
                low = mid + 1
            else:
                high = mid - 1
        else:
            if higher_param_gives_larger_file:
                high = mid - 1
            else:
                low = mid + 1

    return best_img, min_diff


# ==========================================
#             2. 主流程
# ==========================================

# A. 加载模型
print(f"Loading Model from {MODEL_PATH}...")
model = DeepJSCC(in_channels=IN_CHANNELS, channel_compression_ratio=COMPRESSION_RATIO).to(DEVICE)
if os.path.exists(MODEL_PATH):
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
else:
    print(f"未找到模型文件 {MODEL_PATH}, 使用随机初始化")
model.eval()

# B. 计算 K/N
K_over_N = get_k_over_n(model, IMG_SIZE)

# C. 准备测试数据
test_files = [f for f in os.listdir(TEST_IMG_DIR) if f.endswith(('.jpg', '.png'))]
if len(test_files) == 0: raise ValueError(f"测试集为空: {TEST_IMG_DIR}")
print(f"Found {len(test_files)} test images.")

transform = transforms.Compose([transforms.Resize((IMG_SIZE, IMG_SIZE)), transforms.ToTensor()])
mask_transform = transforms.Compose([transforms.Resize((IMG_SIZE, IMG_SIZE)), transforms.ToTensor()])

# ==========================================
#      实验 A: Rate-Distortion (ROI-Metrics)
# ==========================================
print("\n=== Running Experiment A: Rate-Distortion (ROI-Metrics) ===")
BPP_LIST = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
avg_res_a = {"bpp": BPP_LIST, "jscc_ssim": [], "jp2_ssim": [], "jscc_psnr": [], "jp2_psnr": []}

for bpp in BPP_LIST:
    equiv_snr = bpp_to_snr(bpp, K_over_N)
    effective_bpp = bpp * CODING_EFFICIENCY

    t_jscc_s, t_jp2_s = [], []
    t_jscc_p, t_jp2_p = [], []

    print(f"Processing BPP={bpp:.3f}...")
    for fname in tqdm(test_files):
        # 1. 读图和掩码
        path = os.path.join(TEST_IMG_DIR, fname)
        img_gt = to_numpy(transform(Image.open(path).convert('L')).unsqueeze(0).to(DEVICE))

        mask_name = os.path.splitext(fname)[0] + '.png'
        mask_path = os.path.join(TEST_MASK_DIR, mask_name)
        if not os.path.exists(mask_path): mask_path = os.path.join(TEST_MASK_DIR, fname)

        if os.path.exists(mask_path):
            mask_np = to_numpy(mask_transform(Image.open(mask_path).convert('L')).unsqueeze(0).to(DEVICE)) / 255.0
            mask_np = (mask_np > 0.5).astype(float)
        else:
            mask_np = np.ones_like(img_gt).astype(float)

        # 2. 推理
        with torch.no_grad():
            img_jscc = to_numpy(
                model(transform(Image.open(path).convert('L')).unsqueeze(0).to(DEVICE), snr_db=equiv_snr))
        img_jp2, _ = find_fixed_bpp_jpeg2000(img_gt, effective_bpp)

        # 3. 计算 ROI 指标
        s_j, p_j = calc_roi_metrics(img_gt, img_jscc, mask_np)
        s_p, p_p = calc_roi_metrics(img_gt, img_jp2, mask_np)

        t_jscc_s.append(s_j);
        t_jscc_p.append(p_j)
        t_jp2_s.append(s_p);
        t_jp2_p.append(p_p)

    avg_res_a["jscc_ssim"].append(np.mean(t_jscc_s))
    avg_res_a["jp2_ssim"].append(np.mean(t_jp2_s))
    avg_res_a["jscc_psnr"].append(np.mean(t_jscc_p))
    avg_res_a["jp2_psnr"].append(np.mean(t_jp2_p))

# 绘图 A
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(BPP_LIST, avg_res_a["jscc_psnr"], 'r-o', label='DeepJSCC')
plt.plot(BPP_LIST, avg_res_a["jp2_psnr"], 'b--x', label='JPEG2000+Channel')
plt.xlabel('BPP');
plt.ylabel('ROI-PSNR (dB)');
plt.grid(True);
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(BPP_LIST, avg_res_a["jscc_ssim"], 'r-o', label='DeepJSCC')
plt.plot(BPP_LIST, avg_res_a["jp2_ssim"], 'b--x', label='JPEG2000+Channel')
plt.xlabel('BPP');
plt.ylabel('ROI-SSIM');
plt.grid(True);
plt.legend()
plt.savefig(os.path.join(SAVE_DIR, "ExpA_ROI_Metrics.png"))

# ==========================================
#      实验 B: Robustness (ROI-Metrics)
# ==========================================
print("\n=== Running Experiment B: SNR Robustness (ROI-Metrics) ===")
SNR_LIST = [-6, -4, -2, 0, 2, 4, 6]
avg_res_b = {"snr": SNR_LIST, "jscc_ssim": [], "jp2_ssim": [], "jscc_psnr": [], "jp2_psnr": []}

for snr in SNR_LIST:
    target_bpp = snr_to_bpp(snr, K_over_N, efficiency=CODING_EFFICIENCY)

    t_jscc_s, t_jp2_s = [], []
    t_jscc_p, t_jp2_p = [], []

    print(f"Processing SNR={snr}dB (Cap BPP={target_bpp:.3f})...")
    for fname in tqdm(test_files):
        path = os.path.join(TEST_IMG_DIR, fname)
        img_gt = to_numpy(transform(Image.open(path).convert('L')).unsqueeze(0).to(DEVICE))

        mask_name = os.path.splitext(fname)[0] + '.png'
        mask_path = os.path.join(TEST_MASK_DIR, mask_name)
        if not os.path.exists(mask_path): mask_path = os.path.join(TEST_MASK_DIR, fname)

        if os.path.exists(mask_path):
            mask_np = to_numpy(mask_transform(Image.open(mask_path).convert('L')).unsqueeze(0).to(DEVICE)) / 255.0
            mask_np = (mask_np > 0.5).astype(float)
        else:
            mask_np = np.ones_like(img_gt).astype(float)

        with torch.no_grad():
            img_jscc = to_numpy(model(transform(Image.open(path).convert('L')).unsqueeze(0).to(DEVICE), snr_db=snr))
        img_jp2, _ = find_fixed_bpp_jpeg2000(img_gt, target_bpp)

        s_j, p_j = calc_roi_metrics(img_gt, img_jscc, mask_np)
        s_p, p_p = calc_roi_metrics(img_gt, img_jp2, mask_np)

        t_jscc_s.append(s_j)
        t_jscc_p.append(p_j)
        t_jp2_s.append(s_p)
        t_jp2_p.append(p_p)

    avg_res_b["jscc_ssim"].append(np.mean(t_jscc_s))
    avg_res_b["jp2_ssim"].append(np.mean(t_jp2_s))
    avg_res_b["jscc_psnr"].append(np.mean(t_jscc_p))
    avg_res_b["jp2_psnr"].append(np.mean(t_jp2_p))

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(SNR_LIST, avg_res_b["jscc_psnr"], 'r-o', label='DeepJSCC')
plt.plot(SNR_LIST, avg_res_b["jp2_psnr"], 'b--x', label='JPEG2000+Channel')
plt.xlabel('SNR (dB)')
plt.ylabel('ROI-PSNR (dB)')
plt.grid(True)
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(SNR_LIST, avg_res_b["jscc_ssim"], 'r-o', label='DeepJSCC')
plt.plot(SNR_LIST, avg_res_b["jp2_ssim"], 'b--x', label='JPEG2000+Channel')
plt.xlabel('SNR (dB)')
plt.ylabel('ROI-SSIM')
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(SAVE_DIR, "ExpB_ROI_Metrics.png"))

print(f"\nEvaluation Complete! Results saved to {SAVE_DIR}")
