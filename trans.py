import os
import json
import numpy as np
import cv2
from PIL import Image

# === 1. 路径配置 ===
# 你的图片和JSON都在这个文件夹里
INPUT_DIR = './dataset/images'
# 输出的Mask图片将保存到这里
OUTPUT_DIR = './dataset/masks'

# === 2. 标签映射表 (关键！) ===
# 这里的名字必须和你 X-AnyLabeling 里打的标签【一模一样】，区分大小写！
LABEL_MAPPING = {
    # 名字 : 像素值 (ID)
    'background': 0,  # 背景
    'Catheter': 1,  # 导管
    'Wire': 2,  # 导丝
}


def json_to_png():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 获取所有 json 文件
    json_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    print(f"找到 {len(json_files)} 个 JSON 文件，开始转换...")

    count = 0
    for json_file in json_files:
        json_path = os.path.join(INPUT_DIR, json_file)

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 获取原图尺寸
            h = data['imageHeight']
            w = data['imageWidth']

            # 创建全黑画布 (默认全是背景 0)
            mask = np.zeros((h, w), dtype=np.uint8)

            # === 关键逻辑：按顺序绘制 ===
            # X-AnyLabeling 保存 shapes 的顺序就是你画的顺序。
            # 因为你是后画的“背景补丁”，所以它会覆盖在导管上面，形成空心效果。
            for shape in data['shapes']:
                label = shape['label']
                points = np.array(shape['points'], dtype=np.int32)

                if label in LABEL_MAPPING:
                    class_id = LABEL_MAPPING[label]
                    # fillPoly: 填充多边形
                    # 如果 class_id 是 0 (背景补丁)，它会在原来的颜色上涂黑，这就实现了“挖坑”
                    cv2.fillPoly(mask, [points], class_id)
                else:
                    # 如果遇到没见过的标签，打印警告
                    print(f"警告: 文件 {json_file} 中包含未知标签 '{label}'，已跳过。")

            # 保存为 PNG
            # 文件名保持一致，只是后缀变了
            filename_no_ext = os.path.splitext(json_file)[0]
            save_path = os.path.join(OUTPUT_DIR, filename_no_ext + ".png")

            # 使用 PIL 保存，确保不被压缩修改像素值
            Image.fromarray(mask).save(save_path)
            count += 1

        except Exception as e:
            print(f"处理 {json_file} 时出错: {e}")

    print(f"转换完成！共生成 {count} 张 Mask 图片。")
    print(f"保存位置: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == '__main__':
    json_to_png()
