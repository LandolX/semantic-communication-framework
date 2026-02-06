import os
import numpy as np
import tensorflow as tf
from PIL import Image
import cv2
import pandas as pd

# === 1. 配置参数 ===
IMG_HEIGHT = 512
IMG_WIDTH = 512
MODEL_PATH = 'medical_att_unet_512_v4_dice.h5'
IMAGE_DIR = './images_ves_test'  # 测试集原图
MASK_DIR = './masks_ves_test'  # 测试集标签(Ground Truth)


# === 2. CLAHE 增强  ===
def apply_clahe(img_np):
    img_uint8 = (img_np * 255).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img_clahe = clahe.apply(img_uint8)
    return img_clahe.astype(np.float32) / 255.0


# === 3. 核心：数值指标计算函数 ===
def calculate_metrics(y_true, y_pred, epsilon=1e-7):
    """
    计算二分类分割的各项指标
    y_true, y_pred: shape 必须一致，且为 0/1 的二值矩阵
    """
    # 展平以便计算混淆矩阵元素
    y_true_f = y_true.flatten()
    y_pred_f = y_pred.flatten()

    # 计算混淆矩阵的核心元素
    # TP: 真阳性 (预测是血管，真是血管)
    # FP: 假阳性 (预测是血管，其实是背景 -> 噪点)
    # FN: 假阴性 (预测是背景，其实是血管 -> 断裂/漏检)
    # TN: 真阴性 (预测是背景，真是背景)

    tp = np.sum(y_true_f * y_pred_f)
    fp = np.sum((1 - y_true_f) * y_pred_f)
    fn = np.sum(y_true_f * (1 - y_pred_f))
    tn = np.sum((1 - y_true_f) * (1 - y_pred_f))

    # 1. IoU (Intersection over Union)
    iou = tp / (tp + fp + fn + epsilon)

    # 2. Dice Coefficient (F1-Score)
    dice = 2 * tp / (2 * tp + fp + fn + epsilon)

    # 3. Recall (Sensitivity) - 衡量血管有没有断/漏
    recall = tp / (tp + fn + epsilon)

    # 4. Precision - 衡量有没有噪点
    precision = tp / (tp + fp + epsilon)

    # 5. Accuracy - 全局准确率
    accuracy = (tp + tn) / (tp + tn + fp + fn + epsilon)

    # 6. Specificity - 背景识别率
    specificity = tn / (tn + fp + epsilon)

    return {
        "IoU": iou,
        "Dice": dice,
        "Recall": recall,
        "Precision": precision,
        "Accuracy": accuracy,
        "Specificity": specificity
    }


# === 4. 后处理 ===
def post_process(pred_prob, threshold=0.5):

    return (pred_prob > threshold).astype(np.uint8)

# === 5. 主评估流程 ===
def evaluate_all():
    print(f"正在加载模型: {MODEL_PATH} ...")
    if not os.path.exists(MODEL_PATH):
        print(" 模型不存在！")
        return

    # compile=False 避免加载 Loss 报错
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)

    file_list = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.png'))]
    if not file_list:
        print("测试集为空")
        return

    print(f" 开始评估 {len(file_list)} 张图片...")

    # 存储所有图片的指标
    results_list = []

    for file_name in file_list:
        img_path = os.path.join(IMAGE_DIR, file_name)

        # 找 Mask
        base_name = os.path.splitext(file_name)[0]
        mask_name = base_name + '.png'
        mask_path = os.path.join(MASK_DIR, mask_name)
        if not os.path.exists(mask_path): mask_path = os.path.join(MASK_DIR, base_name + '.jpg')

        if not os.path.exists(mask_path):
            print(f" 跳过 {file_name}: 找不到 Ground Truth Mask")
            continue

        # --- 1. 预处理 (输入) ---
        img = Image.open(img_path).convert('L')
        img = img.resize((IMG_WIDTH, IMG_HEIGHT))
        img_np = np.array(img) / 255.0
        img_enhanced = apply_clahe(img_np)
        img_input = np.expand_dims(np.expand_dims(img_enhanced, axis=-1), axis=0)

        # --- 2. 预处理 (真实标签 GT) ---
        mask_gt = Image.open(mask_path).convert('L')
        mask_gt = mask_gt.resize((IMG_WIDTH, IMG_HEIGHT), Image.NEAREST)
        mask_gt = np.array(mask_gt)
        # 严格二值化 (0 或 1)
        mask_gt = (mask_gt > 127).astype(int)

        # --- 3. 预测 ---
        pred_raw = model.predict(img_input, verbose=0)[0]
        pred_prob = pred_raw[:, :, 1]

        # 二值化预测结果
        pred_mask = post_process(pred_prob, threshold=0.3)

        # --- 4. 计算指标 ---
        metrics = calculate_metrics(mask_gt, pred_mask)
        metrics['File'] = file_name  # 记录文件名
        results_list.append(metrics)

        # 打印单张进度
        print(f"Processing {file_name} -> Dice: {metrics['Dice']:.4f}, IoU: {metrics['IoU']:.4f}")

    # === 6. 汇总与输出 ===
    if not results_list:
        print("没有处理任何图片。")
        return

    # 转为 DataFrame 方便统计
    df = pd.DataFrame(results_list)

    # 计算平均值
    mean_metrics = df.mean(numeric_only=True)

    print("\n" + "=" * 40)
    print(" 最终测试集平均评估结果 (Average Metrics)")
    print("=" * 40)
    print(f" Dice Coefficient (F1):  {mean_metrics['Dice']:.4f}  <-- 核心指标")
    print(f" IoU (Jaccard Index):    {mean_metrics['IoU']:.4f}")
    print(f" Recall (Sensitivity):   {mean_metrics['Recall']:.4f}  <-- 查全率")
    print(f" Precision:              {mean_metrics['Precision']:.4f}  <-- 查准率")
    print(f" Accuracy:               {mean_metrics['Accuracy']:.4f}")
    print(f" Specificity:            {mean_metrics['Specificity']:.4f}")
    print("=" * 40)

    # 保存详细报告到 CSV
    csv_path = 'evaluation_report.csv'
    df.to_csv(csv_path, index=False)
    print(f" 详细报表已保存至: {csv_path}")


if __name__ == "__main__":
    evaluate_all()
