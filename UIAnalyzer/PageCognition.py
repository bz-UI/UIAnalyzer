import cv2
import os
import easyocr
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from .Rect import Rect
from .XML import XML
from .Utils import get_bounds_average_color, get_inverse_color, calculate_levenshtein_similarity
from .Driver import Driver


# 获取当前脚本文件目录
script_dir = os.path.dirname(os.path.abspath(__file__))
blank = 5
text_widths, text_height = [20, 40, 60], 35
font_path = os.path.join(script_dir, "Assets", "Arial.ttf")


class PageCognition:
    @staticmethod
    def draw_SoM(img_path: str, enable_ocr: Optional[bool] = False, enable_edge=False, lang: Optional[str] = 'ch_sim') -> Tuple[str, Dict]:
        def filter_xml_rects() -> List:
            ret_rects = []
            for xml_rect in xml_rects:
                # Crop each rect and use OCR to recognize text
                rect_img = Rect.crop_image(img_path, xml_rect['bounds'])
                if rect_img is None:
                    ret_rects.append(xml_rect)
                    continue
                ocr_results = ocr.readtext(rect_img, text_threshold=0.8)
                ocr_res = []
                for ocr_result in ocr_results:
                    bounds = [xml_rect['bounds'][0] + round(ocr_result[0][0][0]), xml_rect['bounds'][1] + round(ocr_result[0][0][1]), xml_rect['bounds'][0] + round(ocr_result[0][2][0]), xml_rect['bounds'][1] + round(ocr_result[0][2][1])]
                    ocr_re = {"class": "OCRText", "text": ocr_result[1], "bounds": bounds}
                    ocr_res.append(ocr_re)

                # If the text in xml_rect is recognized by OCR, add it to ret_rects
                if 'text' in xml_rect.keys():
                    if ocr_res:  # If there is any OCR result
                        # 如果xml 有文本，则过滤掉和 OCR 结果相似度低的框
                        if isinstance(xml_rect['text'], str):
                            for ocr_re in ocr_res:
                                if calculate_levenshtein_similarity(xml_rect['text'], ocr_re['text']) > 0.5:
                                    ret_rects.append(xml_rect)
                                    break
                        else:
                            for text in xml_rect['text']:
                                for ocr_re in ocr_res:
                                    if calculate_levenshtein_similarity(text, ocr_re['text']) > 0.5 or text in ocr_re['text']:
                                        ret_rects.append(xml_rect)
                                        break
                else:
                    ret_rects.append(xml_rect)
            return ret_rects

        def get_ocr_rects() -> List:
            ocr_results = ocr.readtext(img_path, text_threshold=0.8)
            ocr_res = []
            for ocr_result in ocr_results:
                add_ocr = True
                bounds = [round(ocr_result[0][0][0]), round(ocr_result[0][0][1]), round(ocr_result[0][2][0]), round(ocr_result[0][2][1])]
                for xml_rect in xml_rects:
                    if Rect.is_containing(bounds, xml_rect['bounds']) or Rect.intersection_over_second_area(xml_rect['bounds'], bounds) > 0.7:
                        add_ocr = False
                        break

                if add_ocr:
                    ocr_re = {"class": "OCRText", "text": ocr_result[1], "bounds": bounds}
                    ocr_res.append(ocr_re)

            return ocr_res

        def filter_rects_by_edge_detection(rects=None) -> List:
            """
            使用边缘检测过滤矩形框。
            如果边缘不存在/距离 bounds 较远，则认为被遮挡/实际不存在
            """
            low_threshold = 50
            high_threshold = 100
            edge_presence_threshold = 100

            filtered_rects = []
            img_cv = cv2.imread(img_path)

            for rect in rects:
                bounds = rect['bounds']
                x1, y1, x2, y2 = int(bounds[0]), int(bounds[1]), int(bounds[2]), int(bounds[3])
                width, height = x2 - x1, y2 - y1
                if width <= 0 or height <= 0:
                   continue
                element_img = img_cv[y1:y2, x1:x2]  # 裁剪目标元素
                gray_img = cv2.cvtColor(element_img, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray_img, low_threshold, high_threshold)

                if np.sum(edges) > edge_presence_threshold:
                    edge_positions = np.column_stack(np.where(edges > 0))
                    
                    # 垂直方向的坐标值从上往下增加。也就是说，y 坐标值越小，位置越靠近图像的顶部。
                    edge_top = np.min(edge_positions[:, 0])  # 边缘在垂直方向上的最小坐标值。
                    edge_bottom = np.max(edge_positions[:, 0])  # 边缘在垂直方向上的最大坐标值。
                    edge_left = np.min(edge_positions[:, 1])  # 边缘在水平方向上的最小坐标值。
                    edge_right = np.max(edge_positions[:, 1])   # 边缘在水平方向上的最大坐标值。

                    # TODO:
                    # 如果线条在图像边界上被检测到，并且仅有极少数 pixel 出现在边界上，说明可能存在贯穿元素的线条，则表示该元素被可能被遮挡
                    # 边缘像素阈值设置为总边缘像素数量的 1%
                    edge_pixel_threshold = edges.shape[0] * edges.shape[1] * 0.01
                    
                    filtered_rects.append(rect)
            return filtered_rects
            
        # 0. Screenshot if necessary
        if not os.path.exists(img_path):
            Driver.screenshot(img_path)

        # 1. Get XML Rects
        xml_path = os.path.splitext(img_path)[0] + ".xml"
        xml = XML(xml_path)
        xml_rects = xml.group_interactive_nodes()

        if enable_ocr:
            ocr = easyocr.Reader([lang, 'en'])
            filtered_xml_rects = filter_xml_rects()  # 2. Use OCR to filter XML Rects
            ocr_rects = get_ocr_rects()  # 3. Add OCR Rects
            rects = filtered_xml_rects + ocr_rects
        else:
            rects = xml_rects

        # 2. Use edge detection to filter rects
        if enable_edge:
            print(f"before filter rects: {len(rects)}")
            rects_copy = rects.copy()
            rects = filter_rects_by_edge_detection(rects=rects_copy)
            print(f"after filter rects: {len(rects)}")

        rects = sorted(rects, key=lambda r: (r['bounds'][1], r['bounds'][0]))
        return PageCognition.__draw_rects(img_path, rects, "SoM")

    @staticmethod
    def grid(img_path: str) -> Tuple[str, Dict]:
        """
        Draw grid on the image
        """
        rows = 12
        cols = 8
        rects = []

        if not os.path.exists(img_path):
            Driver.screenshot(img_path)
        image = cv2.imread(img_path)
        height, width, _ = image.shape

        unit_height = height / rows
        unit_width = width / cols

        for i in range(rows):
            for j in range(cols):
                rect = dict()
                rect['bounds'] = [int(j * unit_width), int(i * unit_height), int((j + 1) * unit_width), int((i + 1) * unit_height)]
                rects.append(rect)

        return PageCognition.__draw_rects(img_path, rects, "grid")

    @staticmethod
    def __draw_rects(img_path: str, rects: List[Dict], extension_name: str) -> Tuple[str, Dict]:
        """
        Draw rectangles and text on the image
        """
        assert(extension_name in ["SoM", "grid"]), f"Invalid extension name: {extension_name}"

        SoM = (extension_name == "SoM")
        img = Image.open(img_path)
        w, h = img.size[0], img.size[1]
        draw = ImageDraw.Draw(img)
        ret_rects = dict()

        # draw rectangles and text
        for index, rect in enumerate(rects):
            rect_w, rect_h = rect['bounds'][2] - rect['bounds'][0], rect['bounds'][3] - rect['bounds'][1]
            if rect['bounds'][2] >= rect['bounds'][0] and rect['bounds'][3] >= rect['bounds'][1]:
                if (SoM and (rect_w < (w / 2) or rect_h < (h / 2)) and rect['bounds'][1] > (h / 50)) or not SoM:  # filter big rects and top status bar
                    # draw rectangle
                    bound_color = get_inverse_color(get_bounds_average_color(img_path, rect['bounds']))
                    draw.rectangle(rect['bounds'], outline=bound_color, width=3)

                    # draw text
                    text_width = text_widths[0 if index < 10 else 1 if index < 100 else 2]
                    if SoM:
                        width_start = max(rect['bounds'][0], 0)
                        height_start = max(rect['bounds'][1] - text_height, 0)
                        rect['id_bounds'] = [width_start, height_start, width_start + text_width, height_start + text_height]
                    else:
                        rect['id_bounds'] = [rect['bounds'][0] + blank, rect['bounds'][1] + blank, rect['bounds'][0] + blank + text_width, rect['bounds'][1] + blank + text_height]
                    draw.rectangle(rect['id_bounds'], fill=(0, 0, 255), width=3)
                    draw.text((rect['id_bounds'][0], rect['id_bounds'][1]), str(index), fill=(0, 255, 0), font=ImageFont.truetype(font=font_path, size=35))

                    # save
                    ret_rects[index] = rect

        # save image
        directory, filename = os.path.split(img_path)
        name, extension = os.path.splitext(filename)
        SoM_file_path = os.path.join(directory, f"{name}_{extension_name}{extension}")
        img.save(SoM_file_path)

        # save rect info
        if SoM:
            rect_result_path = os.path.join(directory, f"{name}_{extension_name}.txt")
            with open(rect_result_path, "w", encoding='utf-8') as f:
                for key, value in ret_rects.items():
                    f.write(f"{key}: {value}\n")

        return SoM_file_path, ret_rects
