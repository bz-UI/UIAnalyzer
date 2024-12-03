import json
import os
import shutil
import re
import cv2
import pandas as pd
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
from glob import glob
from utils.macro import *
from datetime import datetime
from collections import deque, defaultdict
from skimage.metrics import structural_similarity as ssim


IMAGE_THRESHOLD = 0.95  # 图片相似度阈值

# 手机尺寸
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 2340


# ==================== 数据准备相关 ====================


def get_pre_made_intent(app_name):
    intent = ""
    if app_name == "meituan":
        intent = APPInfo.INTENT_MEITUAN
    elif app_name == "note":
        intent = APPInfo.INTENT_NOTE
    return intent


def get_package_name(intent):
    return intent.split("/")[0]


def ensure_dir(path):
    """确保目录存在"""
    try:
        os.makedirs(path, exist_ok=True)  # exist_ok=True 表示如果目录已经存在，则什么都不做
        # print(f"Directory '{path}' created successfully.")
    except Exception as e:
        print(f"An error occurred while creating directory '{path}': {e}")


def get_local_images(directory='./dataset', suffix='.png'):
    # 用于图片路径排序
    def atoi(text):
        return int(text) if text.isdigit() else text
    
    def natural_keys(text):
        """alist.sort(key=natural_keys) 使用这个函数作为 key 参数进行排序，可以实现自然排序"""
        return [atoi(c) for c in re.split(r'(\d+)', text)]

    image_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(suffix):
                full_path = os.path.join(root, file)
                image_paths.append(full_path)
    # 在返回之前按照自然排序进行排序
    image_paths.sort(key=natural_keys)
    return image_paths


# ==================== 主流程相关 ====================


def check_same_utg_page(full_data_dir, utg_data_dir, current_step):
    # 检查是否有相同页面，有：返回相同utg_page_id，没有，返回-1
    current_image_path = os.path.join(full_data_dir, f'{current_step}.png')
    png_files = glob(os.path.join(utg_data_dir, '*.png'))
    png_files = [f for f in png_files if re.match(r'\d+\.png$', os.path.basename(f))]  # 匹配所有数字命名的图片

    if not png_files:
        return -1
    
    # 策略 1：图片相似度对比，超过阈值，如 0.95，则返回 True
    current_image_cv = cv2.imread(current_image_path, cv2.IMREAD_GRAYSCALE)
    for png_file in png_files:
        # print(png_file)
        file_name = os.path.basename(png_file)
        image_num = int(os.path.splitext(file_name)[0])
        png_image_cv = cv2.imread(png_file, cv2.IMREAD_GRAYSCALE)
        score, diff = ssim(current_image_cv, png_image_cv, full=True)
        if score > IMAGE_THRESHOLD:
            return image_num

    # 策略 2：xml 结构对比，可以除去循环视图的元素（动态内容），解构完全一样则认为 True
    # 也可以加/改一些你认为可行的策略
    # TODO @LK: 补齐策略

    # 如果都不满足，则为不同的页面
    return -1


def copy_page_and_xml(src_dir, src_page_id, dst_dir, dst_page_id):
    # 复制图片和 xml
    src_image_path = os.path.join(src_dir, f"{src_page_id}.png")
    src_xml_path = os.path.join(src_dir, f"{src_page_id}.xml")
    des_image_path = os.path.join(dst_dir, f"{dst_page_id}.png")
    des_xml_path = os.path.join(dst_dir, f"{dst_page_id}.xml")
    shutil.copy(src_image_path, des_image_path)
    shutil.copy(src_xml_path, des_xml_path)
    return des_image_path, des_xml_path


# =============== 绘图记录相关 =================


def draw_image(src_image_dir, image_name, action, position):
    """
    绘制操作的图片
    src_image_dir: 原始图片的目录，image_name 是纯名字，不带后缀，一般是 current_step 纯数字，比如 1,2，表示执行的步骤
    """

    # coordinates 一般形式为 [a,b] 这样的坐标
    def draw_X(draw, coordinates, cross_length=18, width=10, fill='yellow'):
        # 画X形标记
        draw.line(
            [(coordinates[0] - cross_length, coordinates[1] - cross_length), (coordinates[0] + cross_length, coordinates[1] + cross_length)],
            fill=fill,
            width=width
        )
        draw.line(
            [(coordinates[0] - cross_length, coordinates[1] + cross_length), (coordinates[0] + cross_length, coordinates[1] - cross_length)],
            fill=fill,
            width=width
        )

    def draw_arrow(draw, coordinates, fill='yellow'):
        # 画一个箭头
        # 画一条线然后画一个叉，表示方向即可
        draw.line(coordinates, fill=fill, width=7)
        draw_X(draw=draw, coordinates=coordinates[1], fill=fill)

    src_image_path = os.path.join(src_image_dir, f"{image_name}.png")
    dst_image_path = os.path.join(src_image_dir, f"{image_name}_opt.png")


    image = Image.open(src_image_path)
    draw = ImageDraw.Draw(image)
    if action == EventType.CLICK:
        draw_X(draw=draw, coordinates=position)
    # elif data[DictKey.ACTION] == "long_click":
    #     if is_relative:
    #         coordinates = [int(coordinates[0]*SCREEN_WIDTH), int(coordinates[1]*SCREEN_HEIGHT)]
    #     draw_X(draw=draw, coordinates=coordinates, fill='blue')
    # elif data[DictKey.ACTION] == "scroll":
    #     if is_relative:
    #         start = (int(coordinates[0][0]*SCREEN_WIDTH), int(coordinates[0][1]*SCREEN_HEIGHT))  # 转换为元组
    #         end = (int(coordinates[1][0]*SCREEN_WIDTH), int(coordinates[1][1]*SCREEN_HEIGHT))
    #     else:
    #         start = (coordinates[0][0], coordinates[0][1])
    #         end = (coordinates[1][0], coordinates[1][1])
    #     draw_arrow(draw=draw, coordinates=(start, end))
    # else:
    #     action = data[DictKey.ACTION]
    #     raise ValueError(f"Error: action {action} is invalid.")

    image.save(dst_image_path)


def draw_rectangle(src_image_dir, image_num, bounds):
    # 绘制矩形框
    src_image_path = os.path.join(src_image_dir, f"{image_num}.png")
    dst_image_path = os.path.join(src_image_dir, f"{image_num}_rect.png")
    image = Image.open(src_image_path)
    draw = ImageDraw.Draw(image)
    
    # 将 bounds 转换为 (x1, y1), (x2, y2) 格式
    x1, y1 = bounds[0]  # 左上角坐标
    x2, y2 = bounds[1]  # 右下角坐标
    draw.rectangle([x1, y1, x2, y2], outline='red', width=5)  # 绘制矩形
    image.save(dst_image_path)  # 保存图片


# =============== 数据统计相关 =================


def count_txt_lines_to_excel(directory, excel_path='data.xlsx'):
    """
    统计指定目录下所有txt文件的行数,并将结果保存到Excel文件中。

    参数:
    directory (str): 要统计的目录路径 (Meituan目录)
    output_excel (str): 输出的Excel文件名,默认为'data.xlsx'

    返回:
    str: 生成的Excel文件的路径
    """
    def count_lines(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())

    strategies = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    results = {strategy: {} for strategy in strategies}

    for strategy in strategies:
        strategy_dir = os.path.join(directory, strategy)
        for file in os.listdir(strategy_dir):
            if file.endswith('.txt'):
                file_num = int(file.split('_')[0])  # 假设文件名格式为 "数字_SoM.txt"
                if 0 <= file_num <= 29:
                    file_path = os.path.join(strategy_dir, file)
                    line_count = count_lines(file_path)
                    results[strategy][file_num] = line_count

    # 创建DataFrame
    df = pd.DataFrame(results)
    df = df.reindex(sorted(df.index))  # 确保索引按数字顺序排序
    df = df.fillna(0)  # 将NaN值填充为0

    # 保存为Excel
    df.to_excel(excel_path)
    print(f"统计结果已保存到 {excel_path}")

    return excel_path