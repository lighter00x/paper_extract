from loguru import logger

from magic_pdf.config.ocr_content_type import ContentType,BlockType
from magic_pdf.libs.commons import join_path
from magic_pdf.libs.pdf_image_tools import cut_image, cut_image_self
from magic_pdf.dict2md.ocr_mkcontent import print_and_analyze_image_paragraphs

def ocr_cut_image_and_table(spans, page, page_id, pdf_bytes_md5, imageWriter):
    def return_path(type):
        return join_path(pdf_bytes_md5, type)
    # print('###cut-pdf_bytes_md5', pdf_bytes_md5)
    for span in spans:
        span_type = span['type']
        if span_type == ContentType.Image:
            if not check_img_bbox(span['bbox']) or not imageWriter:
                continue
            span['image_path'] = cut_image(span['bbox'], page_id, page, return_path=return_path('images'),
                                           imageWriter=imageWriter)
        elif span_type == ContentType.Table:
            if not check_img_bbox(span['bbox']) or not imageWriter:
                continue
            span['image_path'] = cut_image(span['bbox'], page_id, page, return_path=return_path('tables'),
                                           imageWriter=imageWriter)

    return spans


def ocr_cut_image_and_table_self(images, page, page_id, pdf_bytes_md5, imageWriter):
    def return_path(type):
        return join_path(pdf_bytes_md5, type)
    # print('###after_cut-pdf_bytes_md5', pdf_bytes_md5)

    for unit in images:
        # if not check_img_bbox(unit['bbox']) or not imageWriter:
        #     continue    
        if unit['type'] == ContentType.Image:
            image_block = unit['blocks']
            caption = {'content':'default_name'}
            for sub_block in image_block:
                if sub_block['type'] == BlockType.ImageBody:
                    image = sub_block['lines'][0]['spans'][0]
                
                elif sub_block['type'] == BlockType.ImageCaption:
                    caption = sub_block['lines'][0]['spans'][0]
                # print('#image_caption', caption)
        

            image['image_path'] = cut_image_self(
                image['bbox'], 
                page_id, 
                page, 
                return_path=return_path('images'),
                imageWriter=imageWriter,
                caption=caption  # 传入结构正确的字典
            )
        elif unit['type'] == ContentType.Table:
            if len(unit['bbox']) == 0:
                continue
            caption = {'content':'default_name'}
            table_block = unit['blocks']
            
            for sub_block in table_block:
                if sub_block['type'] == BlockType.TableBody:
                    table = sub_block['lines'][0]['spans'][0]
                
                elif sub_block['type'] == BlockType.TableCaption:
                    caption = sub_block['lines'][0]['spans'][0]
                # print('#table_caption', caption)
        

            table['image_path'] = cut_image_self(
                table['bbox'], 
                page_id, 
                page, 
                return_path=return_path('images'),
                imageWriter=imageWriter,
                caption=caption  # 传入结构正确的字典
            )
        
    
    return images
# def ocr_cut_image_and_table_self(images, page, page_id, pdf_bytes_md5, imageWriter):
#     def return_path(type):
#         return join_path(pdf_bytes_md5, type)
#     # 页面中的所有图像：image_body+caption
#     for unit in images:
#         unit_type = unit['type']
#         if not check_img_bbox(unit['bbox']) or not imageWriter:
#             continue
#         if unit_type == ContentType.Image:
#             image_block = unit['blocks']
#             for sub_block in image_block:
#                 # image_body
#                 if sub_block['type'] == BlockType.ImageBody:
#                     image = sub_block['lines'][0]['spans'][0]
#                 #image_caption
#                 else:
#                     caption = sub_block['lines'][0]['spans'][0]
#         image['image_path'] = cut_image(image['bbox'], page_id, page, return_path=return_path('images'),
#                                            imageWriter=imageWriter, caption = caption)

#     return images


def check_img_bbox(bbox) -> bool:
    if any([bbox[0] >= bbox[2], bbox[1] >= bbox[3]]):
        logger.warning(f'image_bboxes: 错误的box, {bbox}')
        return False
    return True
