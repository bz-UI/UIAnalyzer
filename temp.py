# 禁止生成 __pycache__ 
import sys
sys.dont_write_bytecode = True

import os
from utils.get_data import get_screenshot_and_xml
from UIAnalyzer.PageCognition import PageCognition


def get_data():
    dir_path = os.path.join("dataset", "Meituan")
    get_screenshot_and_xml(dir_path=dir_path)


# todo: 修改文件路径，因为后面要从数据集批量处理。
def get_som(image_num=0, enable_ocr=True):
    origin_image_path = os.path.join("data", "origin", f"{image_num}.png")
    print(origin_image_path)
    output_image_path = os.path.join("data", "origin", f"{image_num}_SoM.png")
    output_txt_path = os.path.join("data", "origin", f"{image_num}_SoM.txt")

    if enable_ocr:
        target_image_path = os.path.join("data", "ocr", f"{image_num}_SoM.png")
        target_txt_path = os.path.join("data", "ocr", f"{image_num}_SoM.txt")
    else:
        target_image_path = os.path.join("data", "no_ocr", f"{image_num}_SoM.png")
        target_txt_path = os.path.join("data", "no_ocr", f"{image_num}_SoM.txt")
    
    PageCognition.draw_SoM(img_path=origin_image_path, enable_ocr=True)

    # 复制 SoM 文件
    os.system(f"cp {output_image_path} {target_image_path}")
    os.system(f"cp {output_txt_path} {target_txt_path}")

    # 删除临时SoM文件
    os.system(f"rm {output_image_path} {output_txt_path}")


if __name__ == "__main__":
    get_data()
    # get_som(image_num=0, enable_ocr=True)
