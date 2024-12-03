# 禁止生成 __pycache__ 
import sys
sys.dont_write_bytecode = True

import os
from utils.get_data import get_screenshot_and_xml
from utils.utils import *
from UIAnalyzer.PageCognition import PageCognition


def run_single(input_image_path, output_dir, enable_ocr=False, enable_edge=False):
    extension_name = "SoM"
    directory, filename = os.path.split(input_image_path)
    name, extension = os.path.splitext(filename)
    som_image_path = os.path.join(directory, f"{name}_{extension_name}{extension}")
    som_txt_path = os.path.join(directory, f"{name}_{extension_name}.txt")
    output_image_path = os.path.join(output_dir, f"{name}_{extension_name}{extension}")
    output_txt_path = os.path.join(output_dir, f"{name}_{extension_name}.txt")

    PageCognition.draw_SoM(img_path=input_image_path, enable_ocr=enable_ocr, enable_edge=enable_edge)
    os.system(f"cp {som_image_path} {output_image_path}")
    os.system(f"cp {som_txt_path} {output_txt_path}")

    # 删除临时SoM文件
    os.system(f"rm {som_image_path} {som_txt_path}")


def run_all(app_name, mode="xml"):
    input_image_dir = os.path.join("dataset", app_name)
    output_dir = os.path.join("output", app_name, mode)
    ensure_dir(output_dir)

    image_paths = get_local_images(directory=input_image_dir)

    for image_path in image_paths:
        print(f"Processing image: {image_path}")

        if mode == "xml":
            run_single(image_path, output_dir, enable_ocr=False, enable_edge=False)
        elif mode == "ocr":
            run_single(image_path, output_dir, enable_ocr=True, enable_edge=False)
        elif mode == "edge":
            run_single(image_path, output_dir, enable_ocr=False, enable_edge=True)
        elif mode == "all":
            run_single(image_path, output_dir, enable_ocr=True, enable_edge=True)
        else:
            raise ValueError(f"Invalid mode: {mode}")

def run():
    app_name = "Meituan"
    mode = "edge"
    print(f"Running {app_name} in {mode} ...")
    run_all(app_name, mode)


def test():
    print("test start")
    app_name = "Meituan"
    image_name = "12.png"
    input_image_path = os.path.join("dataset", app_name, image_name)
    output_dir = os.path.join("output", app_name)
    ensure_dir(output_dir)
    run_single(input_image_path, output_dir, enable_ocr=False, enable_edge=True)
    print("test done")


if __name__ == "__main__":
    run()
    # test()