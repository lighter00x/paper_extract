from io import BytesIO
import cv2
import fitz
import numpy as np
from PIL import Image
from magic_pdf.data.data_reader_writer import DataWriter
from magic_pdf.libs.commons import join_path
from magic_pdf.libs.hash_utils import compute_sha256
import re


def match_legend(text):
    # 匹配常见图例模式：Fig./Figure/Scheme等开头，跟着数字或字母编号
    match = re.search(r'(Fig|Figure|Scheme|Table|Chart)\s*[\.:]?\s*([0-9A-Za-z]+)', text)
    if match:
        matched_str = match.group(0)
        # 替换 . 和空格为 _
        normalized_str = re.sub(r'[\.\s]+', '_', matched_str)
        return normalized_str
    return None

def cut_image(bbox: tuple, page_num: int, page: fitz.Page, return_path, imageWriter: DataWriter):
    """
    从PDF页面中裁剪指定区域的图像并保存为JPG文件
    ===================================================================
    参数:
        bbox: 裁剪区域坐标元组 (x0, y0, x1, y1)
        page_num: PDF页码，用于生成文件名
        page: fitz.Page对象，表示PDF页面
        return_path: 图像保存路径(支持本地路径或S3路径)
        imageWriter: 数据写入器，负责实际写入图像数据
        
    返回:
        str: 保存的图像文件哈希路径(格式: {SHA256哈希值}.jpg)
        
    文件命名规则:
        1. 原始文件名格式: {页码}_{x0}_{y0}_{x1}_{y1}.jpg
           - 示例: 1_100_200_300_400.jpg
           - 坐标值取自bbox参数并取整
        2. 最终保存路径使用文件的SHA256哈希值作为文件名:
           - 示例: a1b2c3d4...jpg
           - 避免文件名过长和特殊字符问题
           - 保证文件名的唯一性
    """
    # 拼接原始文件名: 页码_bbox坐标(取整)
    filename = f'{page_num}_{int(bbox[0])}_{int(bbox[1])}_{int(bbox[2])}_{int(bbox[3])}'

    # 生成原始路径(兼容旧版本，路径中不包含bucket信息)
    img_path = join_path(return_path, filename) if return_path is not None else None

    # 生成最终保存路径(使用文件内容的SHA256哈希值作为文件名)
    img_hash256_path = f'{compute_sha256(img_path)}.jpg'
    # print('img_hash256_path', img_hash256_path)
    # 将坐标元组转换为fitz.Rect对象
    rect = fitz.Rect(*bbox)
    # 创建3倍缩放矩阵(提高输出图像分辨率)
    zoom = fitz.Matrix(3, 3)
    # 从PDF页面获取指定区域的像素图
    pix = page.get_pixmap(clip=rect, matrix=zoom)

    # 将像素图转换为JPEG格式的字节数据(质量设置为95)
    byte_data = pix.tobytes(output='jpeg', jpg_quality=95)

    # 通过DataWriter写入图像数据
    imageWriter.write(img_hash256_path, byte_data)

    return img_hash256_path
def cut_image_self(bbox: tuple, page_num: int, page: fitz.Page, return_path, imageWriter: DataWriter, caption):
    """从第page_num页的page中，根据bbox进行裁剪出一张jpg图片，返回图片路径 save_path：需要同时支持s3和本地,
    图片存放在save_path下，文件名是:
    {page_num}_{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]}.jpg , bbox内数字取整。"""
    # print('###after_path', return_path)
    # 拼接文件名
    # filename = f'{page_num}_{int(bbox[0])}_{int(bbox[1])}_{int(bbox[2])}_{int(bbox[3])}'
    # 查找所有匹配项
    caption_content = caption['content']
    # print('#caption_content', caption_content)
    result = match_legend(caption_content)
    if result:
        print('#提取：', result)
        filename = result
    else:
        filename = caption_content
    filename = f'{filename}'

    # 老版本返回不带bucket的路径
    # img_path = join_path(return_path, filename) if return_path is not None else None
    # print(f'保存路径：{img_path}')
    # 新版本生成平铺路径
    # img_hash256_path = f'{compute_sha256(img_path)}.jpg'
    img_hash256_path = f'{filename}.jpg'
    print('new_path', img_hash256_path)
    # 将坐标转换为fitz.Rect对象
    rect = fitz.Rect(*bbox)
    # 配置缩放倍数为3倍
    zoom = fitz.Matrix(3, 3)
    # 截取图片
    pix = page.get_pixmap(clip=rect, matrix=zoom)

    byte_data = pix.tobytes(output='jpeg', jpg_quality=95)

    imageWriter.write(img_hash256_path, byte_data)

    return img_hash256_path

def cut_image_to_pil_image(bbox: tuple, page: fitz.Page, mode="pillow"):

    # 将坐标转换为fitz.Rect对象
    rect = fitz.Rect(*bbox)
    # 配置缩放倍数为3倍
    zoom = fitz.Matrix(3, 3)
    # 截取图片
    pix = page.get_pixmap(clip=rect, matrix=zoom)

    # 将字节数据转换为文件对象
    image_file = BytesIO(pix.tobytes(output='png'))
    # 使用 Pillow 打开图像
    pil_image = Image.open(image_file)
    if mode == "cv2":
        image_result = cv2.cvtColor(np.asarray(pil_image), cv2.COLOR_RGB2BGR)
    elif mode == "pillow":
        image_result = pil_image
    else:
        raise ValueError(f"mode: {mode} is not supported.")

    return image_result