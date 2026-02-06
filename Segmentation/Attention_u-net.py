import os
import numpy as np
from PIL import Image
import cv2
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from keras_unet_collection import models, losses
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

# === 1. 配置参数 ===
IMAGE_DIR = 'images_ves_train'
MASK_DIR = 'masks_ves_train'
MODEL_SAVE_PATH = 'medical_att_unet_512_v4.h5'
IMG_HEIGHT = 512
IMG_WIDTH = 512
INPUT_CHANNELS = 1
NUM_CLASSES = 2
BATCH_SIZE = 8
EPOCHS = 150
LEARNING_RATE = 1e-4


# === 2.  Dice Loss ===
def dice_loss(y_true, y_pred):
    return losses.dice(y_true, y_pred)


# === 3. 数据加载  ===
def apply_clahe(img_np):
    """CLAHE 对比度增强"""
    img_uint8 = (img_np * 255).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img_clahe = clahe.apply(img_uint8)
    return img_clahe.astype(np.float32) / 255.0


def load_data_v4(img_dir, mask_dir):
    images = []
    masks = []

    file_list = os.listdir(img_dir)
    image_files = [f for f in file_list if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    print(f"正在加载 {len(image_files)} 张图片 (V4: Deep+Aug+Dice)...")

    for file_name in image_files:
        img_path = os.path.join(img_dir, file_name)
        base_name = os.path.splitext(file_name)[0]
        mask_name = base_name + '.png'
        mask_path = os.path.join(mask_dir, mask_name)
        if not os.path.exists(mask_path):
            mask_path = os.path.join(mask_dir, base_name + '.jpg')

        if not os.path.exists(mask_path): continue

        try:
            # --- 读取与预处理 ---
            img = Image.open(img_path).convert('L')
            img = img.resize((IMG_WIDTH, IMG_HEIGHT))
            img_np = np.array(img) / 255.0

            img_np = apply_clahe(img_np)

            mask = Image.open(mask_path).convert('L')
            mask = mask.resize((IMG_WIDTH, IMG_HEIGHT), resample=Image.NEAREST)
            mask_np = np.array(mask)
            mask_np = (mask_np > 127).astype(int)

            # === 4倍无损数据扩充 ===
            # 1. 原始
            images.append(img_np)
            masks.append(mask_np)

            # 2. 水平翻转
            images.append(np.fliplr(img_np))
            masks.append(np.fliplr(mask_np))

            # 3. 垂直翻转
            images.append(np.flipud(img_np))
            masks.append(np.flipud(mask_np))

            # 4. 旋转 90 度
            images.append(np.rot90(img_np))
            masks.append(np.rot90(mask_np))

        except Exception as e:
            print(f"Error: {e}")
            continue

    X = np.array(images, dtype=np.float32)
    Y = np.array(masks, dtype=np.float32)

    print(f" 数据加载完成 总样本量: {len(X)} 张")

    if INPUT_CHANNELS == 1:
        X = np.expand_dims(X, axis=-1)

    Y = to_categorical(Y, num_classes=NUM_CLASSES)
    return X, Y


# === 4. 主流程 ===
if __name__ == "__main__":
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(e)

    # 1. 加载数据
    X, Y = load_data_v4(IMAGE_DIR, MASK_DIR)

    # 2. 划分
    X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size=0.15, random_state=42)

    # 3. 构建深层模型
    print("--- 构建深层 Attention U-Net (Stack=4) ---")
    model = models.att_unet_2d(
        (IMG_HEIGHT, IMG_WIDTH, INPUT_CHANNELS),
        filter_num=[32, 64, 128, 256, 512],
        n_labels=NUM_CLASSES,
        stack_num_down=4,
        stack_num_up=4,
        activation='ReLU',
        output_activation='Softmax',
        batch_norm=True,
        name='medical_att_unet_v4'
    )

    # 4. 编译
    model.compile(
        loss=dice_loss,
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        metrics=['accuracy', losses.dice_coef]
    )

    # 5. 回调
    callbacks_list = [
        EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True),
        ModelCheckpoint(MODEL_SAVE_PATH, monitor='val_loss', save_best_only=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=8, min_lr=1e-6)
    ]

    # 6. 训练
    print(f"--- 开始 V4训练 (Batch: {BATCH_SIZE}) ---")
    history = model.fit(
        X_train, Y_train,
        validation_data=(X_val, Y_val),
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        callbacks=callbacks_list,
        verbose=1,
        shuffle=True
    )

    model.save(MODEL_SAVE_PATH)
    print("训练完成！")

