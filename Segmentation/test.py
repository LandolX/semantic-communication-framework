import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import tensorflow as tf
from keras_unet_collection import losses
import random
import cv2

# === 1. 配置参数  ===
IMG_HEIGHT = 512
IMG_WIDTH = 512

# 模型路径
MODEL_PATH = 'medical_att_unet_512_v4_finetuned.h5'

# 数据路径
IMAGE_DIR = './images_ves_test'
MASK_DIR = './masks_ves_test'

RESULT_DIR = './results_v4_prediction'
if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)

COLOR_MAP = {0: [0, 0, 0], 1: [255, 255, 255]}


# ===  CLAHE   ===
def apply_clahe(img_np):
    """CLAHE 对比度增强"""
    # 还原回 0-255 整数才能做 CLAHE
    img_uint8 = (img_np * 255).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img_clahe = clahe.apply(img_uint8)
    # 转回 0-1 浮点数
    return img_clahe.astype(np.float32) / 255.0


# === 后处理函数 ===
def post_process_prediction(pred_prob_map, threshold=0.3, min_object_size=50):
    # 1. 二值化
    binary_mask = (pred_prob_map > threshold).astype(np.uint8)

    # 2. 形态学闭运算
    kernel = np.ones((3, 3), np.uint8)
    closed_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)

    # 3. 去除小面积噪点
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed_mask, connectivity=8)
    cleaned_mask = np.zeros_like(binary_mask)

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area > min_object_size:
            cleaned_mask[labels == i] = 1

    h, w = cleaned_mask.shape
    color_mask = np.zeros((h, w, 3), dtype=np.uint8)
    color_mask[cleaned_mask == 1] = [255, 255, 255]

    return color_mask


def check_prediction():
    global MODEL_PATH
    print(f"正在加载 V4 模型: {MODEL_PATH} ...")

    if not os.path.exists(MODEL_PATH):
        print(f" 找不到模型文件: {MODEL_PATH}")
        return

    try:
        # 加上 compile=False 防止 Loss 报错
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        print(" 模型加载成功！")
    except Exception as e:
        print(f" 加载失败: {e}")
        return

    file_list = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.png'))]
    if not file_list:
        print(" 文件夹里没有图片！")
        return

    # === 随机抽取 3 张进行测试 ===
    test_files = random.sample(file_list, min(len(file_list), 5))
    print(f" 开始预测 {len(test_files)} 张图片...")

    for test_file in test_files:
        print(f"   处理: {test_file}")
        img_path = os.path.join(IMAGE_DIR, test_file)

        # 匹配 Mask
        file_name_no_ext = os.path.splitext(test_file)[0]
        possible_masks = [file_name_no_ext + '.png', file_name_no_ext + '.jpg', test_file]
        mask_path = None
        for m in possible_masks:
            if os.path.exists(os.path.join(MASK_DIR, m)):
                mask_path = os.path.join(MASK_DIR, m)
                break

        # === 预处理 ===
        img = Image.open(img_path).convert('L')
        img = img.resize((IMG_WIDTH, IMG_HEIGHT))

        # 1. 保留原始数据
        img_origin_np = np.array(img) / 255.0

        # 2. 生成增强数据
        img_enhanced_np = apply_clahe(img_origin_np)

        img_input = np.expand_dims(np.expand_dims(img_enhanced_np, axis=-1), axis=0)

        # 预测
        pred_one_hot = model.predict(img_input, verbose=0)[0]
        vessel_prob = pred_one_hot[:, :, 1]

        # GT 处理
        if mask_path:
            mask_gt = Image.open(mask_path).convert('L').resize((IMG_WIDTH, IMG_HEIGHT), Image.NEAREST)
            mask_gt = np.array(mask_gt)
            mask_gt = (mask_gt > 127).astype(int)
            mask_gt_color = np.zeros((IMG_HEIGHT, IMG_WIDTH, 3), dtype=np.uint8)
            mask_gt_color[mask_gt == 1] = [255, 255, 255]
        else:
            mask_gt_color = np.zeros((IMG_HEIGHT, IMG_WIDTH, 3), dtype=np.uint8)

        # 后处理
        raw_threshold_img = post_process_prediction(vessel_prob, threshold=0.5, min_object_size=0)
        cleaned_img = post_process_prediction(vessel_prob, threshold=0.5, min_object_size=100)

        # === 画图并保存  ===
        plt.figure(figsize=(20, 6))

        plt.subplot(1, 4, 1)
        plt.title(f"Original Input: {test_file}")
        plt.imshow(img_origin_np, cmap='gray')
        plt.axis('off')

        plt.subplot(1, 4, 2)
        plt.title("Ground Truth")
        plt.imshow(mask_gt_color)
        plt.axis('off')

        plt.subplot(1, 4, 3)
        plt.title("V4 Raw Prediction")
        plt.imshow(raw_threshold_img)
        plt.axis('off')

        plt.subplot(1, 4, 4)
        plt.title("V4 Final Result")
        plt.imshow(cleaned_img)
        plt.axis('off')

        save_path = os.path.join(RESULT_DIR, f"result_{file_name_no_ext}.png")
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
        print(f" 已保存: {save_path}")

    print(f"\n V4 测试完成  打开文件夹 {RESULT_DIR} 查看图片。")


if __name__ == "__main__":
    check_prediction()


