from keras_unet_collection import models, losses
import tensorflow as tf
import os
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from keras_unet_collection import models, losses
from sklearn.model_selection import train_test_split

# === 1. 配置参数 (请根据你的实际情况修改) ===
IMAGE_DIR = './dataset/images'  # 原始图片文件夹
MASK_DIR = './dataset/masks'  # 标签图片文件夹 (png格式, 像素值为0,1,2,3)
MODEL_SAVE_PATH = 'medical_att_unet.h5'  # 训练好的模型保存路径
IMG_HEIGHT = 256
IMG_WIDTH = 256
INPUT_CHANNELS = 1  # 灰度图为1，RGB为3
NUM_CLASSES = 3  # 类别数：背景 + 导管 + 导丝  = 3
BATCH_SIZE = 8
EPOCHS = 300
LEARNING_RATE = 1e-4


# === 2. 数据加载与预处理函数 ===
# === 修改后的 load_data 函数 ===
def load_data(img_dir, mask_dir):
    images = []
    masks = []

    file_list = os.listdir(img_dir)
    # 筛选出只是图片的文件（排除 json）
    image_files = [f for f in file_list if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

    print(f"正在加载 {len(image_files)} 张图片...")  # 这里的数量应该显示 24 张左右

    for file_name in image_files:  # 注意这里改成了遍历 image_files
        # 构造路径
        img_path = os.path.join(img_dir, file_name)

        # 假设 mask 是同名的 png 文件 (注意：有些系统可能后缀是 .png 而不是 .jpg)
        # 这里我们需要把原图后缀换成 .png 来找对应的 mask
        base_name = os.path.splitext(file_name)[0]
        mask_name = base_name + '.png'
        mask_path = os.path.join(mask_dir, mask_name)

        if not os.path.exists(mask_path):
            print(f"警告: 找不到对应的 Mask {mask_path}，跳过。")
            continue

        # --- 处理图片 ---
        try:
            # 如果是医学灰度图，用 'L'；如果是彩色图，用 'RGB'
            img = Image.open(img_path).convert('L')
            img = img.resize((IMG_WIDTH, IMG_HEIGHT))
            img_np = np.array(img)

            # 归一化到 [0, 1]
            img_np = img_np / 255.0
            images.append(img_np)

            # --- 处理 Mask ---
            mask = Image.open(mask_path).convert('L')  # 确保是单通道
            mask = mask.resize((IMG_WIDTH, IMG_HEIGHT), resample=Image.NEAREST)
            mask_np = np.array(mask)

            masks.append(mask_np)

        except Exception as e:
            print(f"读取文件 {file_name} 出错: {e}")
            continue

    # 转换为 Numpy 数组
    X = np.array(images)
    Y = np.array(masks)

    # 调整维度
    if INPUT_CHANNELS == 1:
        X = np.expand_dims(X, axis=-1)

    # Y: [N, 256, 256] -> [N, 256, 256, NUM_CLASSES] (One-Hot 编码)
    try:
        Y = to_categorical(Y, num_classes=NUM_CLASSES)
    except IndexError:
        print(f"\n【严重错误】你的 Mask 中包含了超出 NUM_CLASSES 的像素值！")
        print(f"代码设置的 NUM_CLASSES = {NUM_CLASSES} (即 0~{NUM_CLASSES - 1})")
        print(f"Mask 中的实际最大值 = {np.max(Y)}")
        print("请检查你的 LABEL_MAPPING 或者把 NUM_CLASSES 改大。\n")
        exit()

    return X, Y

# === 3. 主训练流程 ===
if __name__ == "__main__":
    # A. 加载数据
    print("--- 步骤 1: 加载数据 ---")
    if not os.path.exists(IMAGE_DIR):
        print(f"错误: 文件夹 {IMAGE_DIR} 不存在，请先创建并放入图片！")
        exit()

    X, Y = load_data(IMAGE_DIR, MASK_DIR)
    print(f"数据加载完成: 输入形状 {X.shape}, 标签形状 {Y.shape}")

    # 划分训练集和验证集 (80% 训练, 20% 验证)
    X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.2, random_state=42)

    # B. 构建模型 (使用 Attention U-Net)
    print("--- 步骤 2: 构建 Attention U-Net 模型 ---")
    # 引用自 keras-unet-collection
    model = models.att_unet_2d(
        (IMG_HEIGHT, IMG_WIDTH, INPUT_CHANNELS),
        filter_num=[64, 128, 256, 512],
        n_labels=NUM_CLASSES,
        stack_num_down=2,
        stack_num_up=2,
        activation='ReLU',
        output_activation='Softmax',  # 多分类必须用 Softmax
        batch_norm=True,
        pool=False,
        unpool=False,
        name='medical_att_unet'
    )

    # C. 编译模型 (使用 Dice Loss 应对导管/导丝的样本不平衡)
    # 引用自 keras-unet-collection
    model.compile(
        loss=losses.dice,
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        metrics=['accuracy', losses.dice_coef]
    )

    model.summary()

    # D. 开始训练
    print("--- 步骤 3: 开始训练 ---")
    history = model.fit(
        X_train, Y_train,
        validation_data=(X_val, Y_val),
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        verbose=1,
        shuffle=True
    )

    # E. 保存模型
    print(f"--- 步骤 4: 保存模型至 {MODEL_SAVE_PATH} ---")
    model.save(MODEL_SAVE_PATH)
    print("全部完成！")