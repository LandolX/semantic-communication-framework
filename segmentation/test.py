import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import tensorflow as tf
from keras_unet_collection import losses

# === 配置 ===
# 必须和训练时的设置完全一致
IMG_HEIGHT = 256
IMG_WIDTH = 256
MODEL_PATH = 'medical_att_unet.h5'
IMAGE_DIR = './dataset/images'
MASK_DIR = './dataset/masks'

# 定义颜色映射 (让不同的类别显示不同颜色)
# 格式: [R, G, B]
COLOR_MAP = {
    0: [0, 0, 0],  # 背景: 黑色
    1: [255, 0, 0],  # 导管: 红色
    2: [0, 255, 0]  # 导丝: 绿色 (如有器官则是蓝色)
}


def decode_one_hot(mask_one_hot):
    """
    把 One-Hot 格式 (256, 256, 3) 还原成 类别索引图 (256, 256)
    然后转换成 RGB 彩色图以便肉眼观察
    """
    # 1. argmax: 找出每个像素概率最大的那个类别的索引 (0, 1, or 2)
    # mask_one_hot shape: [H, W, Classes] -> [H, W]
    mask_class_id = np.argmax(mask_one_hot, axis=-1)

    # 2. 映射成颜色
    h, w = mask_class_id.shape
    color_mask = np.zeros((h, w, 3), dtype=np.uint8)

    for class_id, color in COLOR_MAP.items():
        # 找到所有属于该类别的像素，填上颜色
        color_mask[mask_class_id == class_id] = color

    return color_mask


def check_prediction():
    # 1. 加载模型 (注意：必须带上 custom_objects 否则报错)
    print(f"正在加载模型: {MODEL_PATH} ...")
    if not os.path.exists(MODEL_PATH):
        print("错误: 找不到模型文件！请先完成训练。")
        return

    try:
        model = tf.keras.models.load_model(
            MODEL_PATH,
            custom_objects={'dice': losses.dice, 'dice_coef': losses.dice_coef}
        )
    except Exception as e:
        print(f"加载模型失败: {e}")
        return

    # 2. 随机挑一张图来测试
    file_list = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.png'))]
    if not file_list:
        print("目录里没图！")
        return

    # 这里我们挑第一张，或者你可以指定特定的文件名
    test_file = file_list[3]
    print(f"正在测试图片: {test_file}")

    img_path = os.path.join(IMAGE_DIR, test_file)
    mask_path = os.path.join(MASK_DIR, test_file.split('.')[0] + '.png')

    # 3. 预处理 (和训练时一模一样)
    # -- 图片 --
    img = Image.open(img_path).convert('L')
    img = img.resize((IMG_WIDTH, IMG_HEIGHT))
    img_np = np.array(img) / 255.0
    # 增加 batch 维度: [256, 256] -> [1, 256, 256, 1]
    img_input = np.expand_dims(img_np, axis=-1)
    img_input = np.expand_dims(img_input, axis=0)

    # -- 预测 --
    # pred shape: [1, 256, 256, 3] (One-Hot 概率分布)
    pred_one_hot = model.predict(img_input)[0]

    # -- 真实 Mask (为了对比) --
    if os.path.exists(mask_path):
        mask_gt = Image.open(mask_path).convert('L')
        mask_gt = mask_gt.resize((IMG_WIDTH, IMG_HEIGHT), resample=Image.NEAREST)
        mask_gt_np = np.array(mask_gt)
        # 构造成伪 One-Hot 方便统一处理 (这里简单处理直接转颜色)
        # 注意：这里我们不需要转 One-Hot，直接用 decode 逻辑的后半部分即可
        mask_gt_color = np.zeros((IMG_HEIGHT, IMG_WIDTH, 3), dtype=np.uint8)
        for cid, color in COLOR_MAP.items():
            mask_gt_color[mask_gt_np == cid] = color
    else:
        mask_gt_color = np.zeros((IMG_HEIGHT, IMG_WIDTH, 3))  # 全黑

    # 4. 转换预测结果为彩色
    pred_color = decode_one_hot(pred_one_hot)

    # 5. 画图展示
    plt.figure(figsize=(12, 4))

    # 第一张：原图
    plt.subplot(1, 3, 1)
    plt.title("Original Image (Input)")
    plt.imshow(img, cmap='gray')
    plt.axis('off')

    # 第二张：标准答案 (你的标注)
    plt.subplot(1, 3, 2)
    plt.title("Ground Truth (Your Label)")
    plt.imshow(mask_gt_color)
    plt.axis('off')

    # 第三张：AI 的预测
    plt.subplot(1, 3, 3)
    plt.title("AI Prediction (Output)")
    plt.imshow(pred_color)
    plt.axis('off')

    plt.tight_layout()
    plt.show()
    print("展示完毕！")


if __name__ == "__main__":
    check_prediction()
