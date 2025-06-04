from PIL import Image, ImageDraw, ImageFont

"""
两个绘图工具函数，针对单一分子和多分子bbox绘制
"""
def draw_bbox_for_normalized(image, bbox, index, padding_ratio=0.1):
    """
    为归一化坐标[0,0,1,1]的边界框创建带白色背景的图像，并绘制边界框和索引
    
    参数:
    image (PIL.Image): 输入图像
    bbox (list): 边界框坐标，格式为[x,y,w,h]，通常是[0,0,1,1]
    index (int/str): 要显示的索引
    padding_ratio (float): 白色背景比原图大的比例，默认为0.1
    """
    # 创建比原图稍大的白色背景
    width, height = image.size
    new_width = int(width * (1 + padding_ratio * 2))
    new_height = int(height * (1 + padding_ratio * 2))
    
    # 创建白色背景图像
    background = Image.new('RGB', (new_width, new_height), (255, 255, 255))
    
    # 计算原图在背景中的位置（居中放置）
    x_offset = int((new_width - width) / 2)
    y_offset = int((new_height - height) / 2)
    
    # 将原图粘贴到白色背景上
    background.paste(image, (x_offset, y_offset))
    
    # 创建绘图对象
    draw = ImageDraw.Draw(background)
    
    # 计算实际像素坐标（考虑偏移）
    x, y, w, h = bbox
    top_left_x = float(x * width) + x_offset
    top_left_y = float(y * height) + y_offset
    bottom_right_x = float((x + w) * width) + x_offset
    bottom_right_y = float((y + h) * height) + y_offset
    
    # 定义边界框的四个角点
    top_left = (top_left_x, top_left_y)
    bottom_right = (bottom_right_x, bottom_right_y)
    top_right = (bottom_right_x, top_left_y)
    bottom_left = (top_left_x, bottom_right_y)
    
    # 绘制边界框（红色，线宽2）
    line_width = 2
    bbox_color = (255, 0, 0)  # 红色边界框
    draw.line([top_left, top_right], fill=bbox_color, width=line_width)
    draw.line([top_right, bottom_right], fill=bbox_color, width=line_width)
    draw.line([bottom_right, bottom_left], fill=bbox_color, width=line_width)
    draw.line([bottom_left, top_left], fill=bbox_color, width=line_width)
    
    # 设置文本内容和样式
    text = str(index)
    text_color = (0, 0, 255)  # 蓝色文字
    
    # 尝试加载字体，如果失败则使用默认字体
    try:
        font = ImageFont.truetype(font='/home/xq/Mol/Paper_extract/checkpoints/arial.ttf', size=15)
    except Exception:
        # 使用默认字体
        font = ImageFont.load_default()
    
    # 计算文本位置（右上角，稍微偏移避免重叠）
    text_position = (top_right[0] - 2, top_right[1] - 7)  # 向右上角偏移
    
    # 使用 textbbox 计算文本尺寸（兼容 Pillow >=9.0.0）
    text_bbox = draw.textbbox((0, 0), text, font=font)  # 先计算相对 (0,0) 的 bbox
    text_width = text_bbox[2] - text_bbox[0]  # 宽度 = right - left
    text_height = text_bbox[3] - text_bbox[1]  # 高度 = bottom - top
    
    # 调整 text_bbox 到实际位置
    text_bbox = (
        text_position[0],
        text_position[1],
        text_position[0] + text_width,
        text_position[1] + text_height
    )
    
    # 为文本添加白色背景（比文本稍大一点）
    bg_padding = 2  # 背景比文本大2像素
    bg_coords = (
        text_bbox[0] - bg_padding,  # 左
        text_bbox[1] - bg_padding,  # 上
        text_bbox[2] + bg_padding,  # 右
        text_bbox[3] + bg_padding   # 下
    )
    draw.rectangle(bg_coords, fill=(255, 255, 255))  # 白色背景
    
    # 检查文本是否超出图像边界并调整
    if text_bbox[2] > new_width:  # 如果超出右边界
        text_position = (new_width - text_width - 5, text_position[1])
    if text_bbox[1] < 0:  # 如果超出上边界
        text_position = (text_position[0], 5)
    
    # 重新计算背景位置（如果文本位置调整了）
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_bbox = (
        text_position[0],
        text_position[1],
        text_position[0] + text_width,
        text_position[1] + text_height
    )
    
    bg_coords = (
        text_bbox[0] - bg_padding,
        text_bbox[1] - bg_padding,
        text_bbox[2] + bg_padding,
        text_bbox[3] + bg_padding
    )
    draw.rectangle(bg_coords, fill=(255, 255, 255))
    
    # 绘制文本
    draw.text(text_position, text, font=font, fill=text_color)
    
    return background


def draw_bbox_xywh(image, x, y, w, h, index):
    draw = ImageDraw.Draw(image)
    width = image.width
    height = image.height

    # 计算实际像素坐标
    top_left_x = float(x * width)
    top_left_y = float(y * height)
    bottom_right_x = float((x + w) * width)
    bottom_right_y = float((y + h) * height)

    # 定义边界框的四个角点
    top_left = (top_left_x, top_left_y)
    bottom_right = (bottom_right_x, bottom_right_y)
    top_right = (bottom_right_x, top_left_y)
    bottom_left = (top_left_x, bottom_right_y)

    # 绘制边界框（红色，线宽2）
    line_width = 2
    bbox_color = (255, 0, 0)  # 红色边界框
    draw.line([top_left, top_right], fill=bbox_color, width=line_width)
    draw.line([top_right, bottom_right], fill=bbox_color, width=line_width)
    draw.line([bottom_right, bottom_left], fill=bbox_color, width=line_width)
    draw.line([bottom_left, top_left], fill=bbox_color, width=line_width)

    # 设置文本内容和样式
    text = str(index)
    text_color = (0, 0, 255)  # 蓝色文字
    font = ImageFont.truetype(font='/home/xq/Mol/Paper_extract/checkpoints/arial.ttf', size=15)

    # 计算文本位置（右上角，稍微偏移避免重叠）
    text_position = (top_right[0] - 2, top_right[1] - 7)  # 向右上角偏移

    # 获取文本的实际边界框
    text_bbox = draw.textbbox(text_position, text, font=font)
    
    # 为文本添加白色背景（比文本稍大一点）
    bg_padding = 2  # 背景比文本大2像素
    bg_coords = (
        text_bbox[0] - bg_padding,  # 左
        text_bbox[1] - bg_padding,  # 上
        text_bbox[2] + bg_padding,  # 右
        text_bbox[3] + bg_padding   # 下
    )
    draw.rectangle(bg_coords, fill=(255, 255, 255))  # 白色背景

    # 检查文本是否超出图像边界并调整
    if text_bbox[2] > width:  # 如果超出右边界
        text_position = (width - (text_bbox[2] - text_bbox[0]) - 5, text_position[1])
    if text_bbox[1] < 0:  # 如果超出上边界
        text_position = (text_position[0], 5)

    # 重新计算背景位置（如果文本位置调整了）
    text_bbox = draw.textbbox(text_position, text, font=font)
    bg_coords = (
        text_bbox[0] - bg_padding,
        text_bbox[1] - bg_padding,
        text_bbox[2] + bg_padding,
        text_bbox[3] + bg_padding
    )
    draw.rectangle(bg_coords, fill=(255, 255, 255))

    # 绘制文本
    draw.text(text_position, text, font=font, fill=text_color)

    return image  # 返回修改后的图像
