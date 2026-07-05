#!/usr/bin/env python3
"""
图片自动审核工具 - CLI 版本
用法: python3 image_checker.py <图片路径> <指令>

指令：
  1 或 "2号门"   -> 1440 x 1080
  2 或 "8号门"   -> 1032 x 1720
  3 或 "广告机"   -> 2160 x 3840
"""

import sys
import os
from PIL import Image

INSTRUCTIONS = {
    "1": {"name": "2号门", "width": 1440, "height": 1080},
    "2": {"name": "8号门", "width": 1032, "height": 1720},
    "3": {"name": "广告机", "width": 2160, "height": 3840},
}

ALIASES = {
    "2号门": "1",
    "8号门": "2",
    "广告机": "3",
}


def get_instruction(key):
    key = key.strip()
    if key in INSTRUCTIONS:
        return INSTRUCTIONS[key]
    if key in ALIASES:
        return INSTRUCTIONS[ALIASES[key]]
    raise ValueError(f"未知指令: {key}，可用指令: 1(2号门), 2(8号门), 3(广告机)")


def process_image(image_path, instruction_key):
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return False

    try:
        target = get_instruction(instruction_key)
    except ValueError as e:
        print(f"❌ {e}")
        return False

    target_w, target_h = target["width"], target["height"]
    target_name = target["name"]

    with Image.open(image_path) as img:
        original_w, original_h = img.size

        print(f"📋 指令: {target_name} ({target_w}×{target_h})")
        print(f"📏 当前尺寸: {original_w}×{original_h}")

        if original_w == target_w and original_h == target_h:
            print(f"✅ 尺寸正确")
            return True
        else:
            print(f"⚠️  尺寸不匹配，正在调整...")
            resized_img = img.resize((target_w, target_h), Image.LANCZOS)

            base, ext = os.path.splitext(image_path)
            output_path = f"{base}_{target_name}_{target_w}x{target_h}{ext}"
            resized_img.save(output_path)
            print(f"✅ 已保存调整后的图片: {output_path}")
            print(f"   新尺寸: {target_w}×{target_h}")
            return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 image_checker.py <图片路径> <指令>")
        print("指令: 1 / 2号门 / 2 / 8号门 / 3 / 广告机")
        print("示例: python3 image_checker.py photo.jpg 1")
        print("      python3 image_checker.py photo.png 广告机")
        sys.exit(1)

    image_path = sys.argv[1]
    instruction_key = sys.argv[2]
    success = process_image(image_path, instruction_key)
    sys.exit(0 if success else 1)
