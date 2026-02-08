import torch
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from PIL import Image
from torchvision import transforms
import os
import math
import random
from tqdm import tqdm
import lpips 

# === TensorFlow / Keras 设置 ===
import tensorflow as tf
from tensorflow.keras.models import load_model

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

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

# 引入模型定义
from model_DeepJSCC import DeepJSCC

# ==========================================
#               0. 全局配置
# ==========================================
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL_PATH = 'deepjscc_best_v3.pth' # 确保文件名正确
SEG_MODEL_PATH = 'medical_att_unet_512_v4_finetuned.h5' 

TEST_IMG_DIR = 'images_ves_test'
TEST_MASK_DIR = 'masks_ves_test'
SAVE_DIR = "results_final_paper_v4_dice_unet" 

# 图片保存子目录
IMG_SAVE_DIR = os.path.join(SAVE_DIR, "visual_comparison")
if not os.path.exists(IMG_SAVE_DIR):
    os.makedirs(IMG_SAVE_DIR)

COMPRESSION_RATIO = 0.5
IN_CHANNELS = 1

# 现实通信限制
CODING_EFFICIENCY = 0.8
MIN_BPP_THRESHOLD = 0.02

# 图像参数
IMG_SIZE = 512

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 初始化 LPIPS
print("Loading LPIPS model (PyTorch)...")
loss_fn_lpips = lpips.LPIPS(net='vgg').to(DEVICE)
loss_fn_lpips.eval()

# ==========================================
#          1. 下游任务分割器 
# ==========================================
class DownstreamSegmentor:
    def __init__(self, model_path):
        print(f"[*] Loading Segmentation Model: {model_path}")
        try:
            self.model = load_model(model_path, compile=False) 
            print("[*] Segmentation Model Loaded Successfully.")
        except Exception as e:
            print(f" 模型加载失败: {e}")
            self.model = None

    def apply_clahe(self, img_np):
        """
        输入: [H, W] 的 numpy 数组, 范围 0-255 (uint8) 或 0-1 (float)
        输出: [H, W] 的 numpy 数组, 范围 0-1 (float)
        """
        if img_np.max() <= 1.0:
            img_uint8 = (img_np * 255).astype(np.uint8)
        else:
            img_uint8 = img_np.astype(np.uint8)
            
        # CLAHE 对比度增强
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img_clahe = clahe.apply(img_uint8)
        
        # 归一化回 0-1
        return img_clahe.astype(np.float32) / 255.0

    def predict(self, img_rec_numpy):
        """
        输入: DeepJSCC 恢复的图像 [H, W], 0-255, uint8
        """
        if self.model is None: return np.zeros_like(img_rec_numpy)

        x_enhanced = self.apply_clahe(img_rec_numpy)

        # 2. 调整维度 [1, H, W, 1]
        x = np.expand_dims(x_enhanced, axis=0) 
        x = np.expand_dims(x, axis=-1) 

        # 3. 推理
        pred_raw = self.model.predict(x, verbose=0)
        
        # 4. 处理多通道 (取前景概率)
        if pred_raw.shape[-1] == 2:
            pred_prob = pred_raw[..., 1]
        else:
            pred_prob = pred_raw 

        pred_prob = np.squeeze(pred_prob)
        if pred_prob.ndim == 3: pred_prob = pred_prob[..., 0]

        pred_mask = (pred_prob > 0.3).astype(np.uint8)
        
        return pred_mask

segmentor = DownstreamSegmentor(SEG_MODEL_PATH)

# ==========================================
#             2. 工具函数
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

def calc_all_metrics(img_tensor_gt, img_tensor_rec, mask_np):
    img_gt = to_numpy(img_tensor_gt)
    img_rec = to_numpy(img_tensor_rec)
    
    with torch.no_grad():
        t_gt = img_tensor_gt.repeat(1, 3, 1, 1) * 2 - 1
        t_rec = img_tensor_rec.repeat(1, 3, 1, 1) * 2 - 1
        lpips_val = loss_fn_lpips(t_gt, t_rec).item()

    img1 = img_gt.astype(np.float64)
    img2 = img_rec.astype(np.float64)
    num_roi = np.sum(mask_np)
    if num_roi < 1: num_roi = 1 

    _, ssim_map = ssim(img1, img2, data_range=255, full=True)
    roi_ssim = np.sum(ssim_map * mask_np) / num_roi

    diff = (img1 - img2) * mask_np
    mse = np.sum(diff ** 2) / num_roi
    if mse == 0: roi_psnr = 100.0
    else: roi_psnr = 10 * np.log10((255.0 ** 2) / mse)

    img_bin = segmentor.predict(img_rec)
    mask_gt = mask_np.astype(np.uint8)
    intersection = np.sum(img_bin * mask_gt)
    sum_pixels = np.sum(img_bin) + np.sum(mask_gt)
    
    if sum_pixels == 0: dice = 1.0
    else: dice = (2.0 * intersection) / sum_pixels
    
    return roi_psnr, roi_ssim, dice, lpips_val

def find_fixed_bpp_jpeg2000(img_np, target_bpp):
    if target_bpp < MIN_BPP_THRESHOLD: return None, 0
    h, w = img_np.shape
    total_pixels = h * w
    p1, p2 = 100, 500
    res1, buf1 = cv2.imencode('.jp2', img_np, [int(cv2.IMWRITE_JPEG2000_COMPRESSION_X1000), p1])
    res2, buf2 = cv2.imencode('.jp2', img_np, [int(cv2.IMWRITE_JPEG2000_COMPRESSION_X1000), p2])
    if not res1 or not res2: return None, 0
    bpp1 = (buf1.size * 8) / total_pixels
    bpp2 = (buf2.size * 8) / total_pixels
    higher_param_gives_larger_file = bpp2 > bpp1
    low, high = 10, 1000
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
            if higher_param_gives_larger_file: low = mid + 1
            else: high = mid - 1
        else:
            if higher_param_gives_larger_file: high = mid - 1
            else: low = mid + 1
    return best_img, min_diff

# ==========================================
#             3. 主流程
# ==========================================

print(f"Loading DeepJSCC Model from {MODEL_PATH}...")
model = DeepJSCC(in_channels=IN_CHANNELS, channel_compression_ratio=COMPRESSION_RATIO).to(DEVICE)
if os.path.exists(MODEL_PATH):
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
else:
    print(f"未找到模型文件 {MODEL_PATH}, 使用随机初始化")
model.eval()

K_over_N = get_k_over_n(model, IMG_SIZE)

test_files = [f for f in os.listdir(TEST_IMG_DIR) if f.endswith(('.jpg', '.png'))]
test_files.sort()

if len(test_files) == 0: raise ValueError(f"测试集为空: {TEST_IMG_DIR}")
print(f"Found {len(test_files)} test images.")

transform = transforms.Compose([transforms.Resize((IMG_SIZE, IMG_SIZE)), transforms.ToTensor()])
mask_transform = transforms.Compose([transforms.Resize((IMG_SIZE, IMG_SIZE)), transforms.ToTensor()])

# ==========================================
#      实验 A: Rate-Distortion
# ==========================================
print("\n=== Running Experiment A: Rate-Distortion ===")
BPP_LIST = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
metrics_names = ["psnr", "ssim", "dice", "lpips"] 
avg_res_a = { "bpp": BPP_LIST }
for m in metrics_names:
    avg_res_a[f"jscc_{m}"] = []
    avg_res_a[f"jp2_{m}"] = []

for bpp in BPP_LIST:
    equiv_snr = bpp_to_snr(bpp, K_over_N)
    effective_bpp = bpp * CODING_EFFICIENCY
    
    tmp = { f"jscc_{m}": [] for m in metrics_names }
    tmp.update({ f"jp2_{m}": [] for m in metrics_names })
    
    print(f"Processing BPP={bpp:.3f}...")
    for fname in tqdm(test_files):
        path = os.path.join(TEST_IMG_DIR, fname)
        img_pil = Image.open(path).convert('L')
        img_tensor = transform(img_pil).unsqueeze(0).to(DEVICE)
        img_gt = to_numpy(img_tensor)
        
        mask_name = os.path.splitext(fname)[0] + '.png'
        mask_path = os.path.join(TEST_MASK_DIR, mask_name)
        if not os.path.exists(mask_path): mask_path = os.path.join(TEST_MASK_DIR, fname)
        
        if os.path.exists(mask_path):
            mask_np = to_numpy(mask_transform(Image.open(mask_path).convert('L')).unsqueeze(0).to(DEVICE)) / 255.0
            mask_np = (mask_np > 0.5).astype(float)
        else:
            mask_np = np.ones_like(img_gt).astype(float)

        with torch.no_grad():
            rec_tensor = model(img_tensor, snr_db=equiv_snr)
        
        img_jp2, _ = find_fixed_bpp_jpeg2000(img_gt, effective_bpp)
        if img_jp2 is None: img_jp2 = np.zeros_like(img_gt)
        tensor_jp2 = transforms.ToTensor()(img_jp2).unsqueeze(0).to(DEVICE)
        
        res_jscc = calc_all_metrics(img_tensor, rec_tensor, mask_np)
        res_jp2 = calc_all_metrics(img_tensor, tensor_jp2, mask_np)
        
        for i, m in enumerate(metrics_names):
            tmp[f"jscc_{m}"].append(res_jscc[i])
            tmp[f"jp2_{m}"].append(res_jp2[i])

    for m in metrics_names:
        avg_res_a[f"jscc_{m}"].append(np.mean(tmp[f"jscc_{m}"]))
        avg_res_a[f"jp2_{m}"].append(np.mean(tmp[f"jp2_{m}"]))

# 绘图 A 
plt.figure(figsize=(16, 4))
titles = ['ROI-PSNR (dB) ↑', 'ROI-SSIM ↑', 'Dice Score (AI-Seg) ↑', 'LPIPS ↓']
keys = ['psnr', 'ssim', 'dice', 'lpips']
for i, key in enumerate(keys):
    plt.subplot(1, 4, i+1)
    plt.plot(BPP_LIST, avg_res_a[f"jscc_{key}"], 'r-o', label='DeepJSCC')
    plt.plot(BPP_LIST, avg_res_a[f"jp2_{key}"], 'b--x', label='JPEG2000')
    plt.xlabel('BPP'); plt.ylabel(key.upper()); plt.title(titles[i]); plt.grid(True)
    if i == 0: plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(SAVE_DIR, "ExpA_2.png"))
plt.close()

# ==========================================
#      实验 B: Robustness 
# ==========================================
print("\n=== Running Experiment B: SNR Robustness ===")
SNR_LIST = [-6, -4, -2, 0, 2, 4, 6]
avg_res_b = { "snr": SNR_LIST }
for m in metrics_names:
    avg_res_b[f"jscc_{m}"] = []
    avg_res_b[f"jp2_{m}"] = []

SAVE_IMG_IDX = 0 
save_fname = test_files[SAVE_IMG_IDX]

for snr in SNR_LIST:
    target_bpp = snr_to_bpp(snr, K_over_N, efficiency=CODING_EFFICIENCY)
    
    tmp = { f"jscc_{m}": [] for m in metrics_names }
    tmp.update({ f"jp2_{m}": [] for m in metrics_names })
    
    print(f"Processing SNR={snr}dB (Cap BPP={target_bpp:.3f})...")
    for idx, fname in enumerate(tqdm(test_files)):
        path = os.path.join(TEST_IMG_DIR, fname)
        img_pil = Image.open(path).convert('L')
        img_tensor = transform(img_pil).unsqueeze(0).to(DEVICE)
        img_gt = to_numpy(img_tensor)
        
        mask_name = os.path.splitext(fname)[0] + '.png'
        mask_path = os.path.join(TEST_MASK_DIR, mask_name)
        if not os.path.exists(mask_path): mask_path = os.path.join(TEST_MASK_DIR, fname)
        
        if os.path.exists(mask_path):
            mask_np = to_numpy(mask_transform(Image.open(mask_path).convert('L')).unsqueeze(0).to(DEVICE)) / 255.0
            mask_np = (mask_np > 0.5).astype(float)
        else:
            mask_np = np.ones_like(img_gt).astype(float)

        with torch.no_grad():
            rec_tensor = model(img_tensor, snr_db=snr)
        
        img_jp2, _ = find_fixed_bpp_jpeg2000(img_gt, target_bpp)
        if img_jp2 is None: img_jp2 = np.zeros_like(img_gt)
        tensor_jp2 = transforms.ToTensor()(img_jp2).unsqueeze(0).to(DEVICE)
        
        res_jscc = calc_all_metrics(img_tensor, rec_tensor, mask_np)
        res_jp2 = calc_all_metrics(img_tensor, tensor_jp2, mask_np)
        
        for i, m in enumerate(metrics_names):
            tmp[f"jscc_{m}"].append(res_jscc[i])
            tmp[f"jp2_{m}"].append(res_jp2[i])

        # ===  保存代表性图片 ===
        if idx == SAVE_IMG_IDX:
            # 拼图: 左(DeepJSCC) 中(GT) 右(JPEG2000)
            img_jscc_np = to_numpy(rec_tensor)
            img_gt_np = img_gt
            img_jp2_np = img_jp2
            
            # 画注文字
            font = cv2.FONT_HERSHEY_SIMPLEX
            # 为了防止灰度图画彩色字报错，转成 BGR
            vis_jscc = cv2.cvtColor(img_jscc_np, cv2.COLOR_GRAY2BGR)
            vis_gt = cv2.cvtColor(img_gt_np, cv2.COLOR_GRAY2BGR)
            vis_jp2 = cv2.cvtColor(img_jp2_np, cv2.COLOR_GRAY2BGR)

            cv2.putText(vis_jscc, f"DeepJSCC", (10, 30), font, 1, (0, 0, 255), 2)
            cv2.putText(vis_jscc, f"SNR={snr}dB", (10, 70), font, 0.8, (0, 0, 255), 2)
            
            cv2.putText(vis_gt, "Ground Truth", (10, 30), font, 1, (0, 255, 0), 2)
            
            cv2.putText(vis_jp2, f"JPEG2000", (10, 30), font, 1, (255, 0, 0), 2)
            cv2.putText(vis_jp2, f"BPP={target_bpp:.3f}", (10, 70), font, 0.8, (255, 0, 0), 2)

            # 横向拼接
            comparison = np.hstack([vis_jscc, vis_gt, vis_jp2])
            
            save_path = os.path.join(IMG_SAVE_DIR, f"Vis_SNR_{snr}dB_{fname}")
            cv2.imwrite(save_path, comparison)
            
             #保存分割的 Mask 预测图，如果想看 U-Net 
            mask_jscc = segmentor.predict(img_jscc_np) * 255
            cv2.imwrite(os.path.join(IMG_SAVE_DIR, f"MaskPred_SNR_{snr}dB_{fname}"), mask_jscc)

    for m in metrics_names:
        avg_res_b[f"jscc_{m}"].append(np.mean(tmp[f"jscc_{m}"]))
        avg_res_b[f"jp2_{m}"].append(np.mean(tmp[f"jp2_{m}"]))

# 绘图 B
plt.figure(figsize=(16, 4))
for i, key in enumerate(keys):
    plt.subplot(1, 4, i+1)
    plt.plot(SNR_LIST, avg_res_b[f"jscc_{key}"], 'r-o', label='DeepJSCC')
    plt.plot(SNR_LIST, avg_res_b[f"jp2_{key}"], 'b--x', label='JPEG2000')
    plt.xlabel('SNR (dB)'); plt.ylabel(key.upper()); plt.title(titles[i]); plt.grid(True)
    if i == 0: plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(SAVE_DIR, "ExpB_2.png"))
plt.close()

print(f"\nEvaluation Complete! Results saved to {SAVE_DIR}")
