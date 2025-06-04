import cv2
import base64

def image_segment_given_box_xywh(image_path, save_path, x, y, w, h):
    image_origin = cv2.imread(image_path)
    height, width = image_origin.shape[:2]
    x_start_pixel = int(x * width)
    x_end_pixel = int((x + w) * width)
    y_start_pixel = int (y * height)
    y_end_pixel = int( (y+ h) * height) 
    segmented_image = image_origin[y_start_pixel: y_end_pixel, x_start_pixel:x_end_pixel]
    cv2.imwrite(save_path, segmented_image)
    return save_path

def encode_image(image_path):
    """将图像文件编码为Base64字符串"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"图像编码失败: {image_path}, 错误: {e}")
        return None