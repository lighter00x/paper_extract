import torch
import os
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
from .utils_yolo import draw_bbox_for_normalized, draw_bbox_xywh

class YOLOModelHandler:
    def __init__(self):
        self.model = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def load_model(self, model_path="/home/xq/Mol/Paper_extract/checkpoints/MOL-v11l-241113.pt"):
        """加载YOLO模型并将其存储在显存中"""
        try:
            # 加载模型并将其移至指定设备
            self.model = YOLO(model_path)
            self.model.to(self.device)
            print(f"已成功将模型加载至{self.device}")
        except Exception as e:
            print(f"加载模型时出错: {e}")
            self.model = None

    def predict(self, source, **kwargs):
        """使用已加载的模型进行预测"""
        if self.model is None:
            print("错误: 没有加载模型，请先调用load_model方法")
            return None
        
        # 设置默认参数
        default_kwargs = {
            'conf': 0.25,
            'save': False
        }
        # 用用户提供的参数覆盖默认参数
        default_kwargs.update(kwargs)
        
        try:
            # 执行预测
            results = self.model(source, **default_kwargs)
            return results
        except Exception as e:
            print(f"预测过程中出错: {e}")
            return None

    def unload_model(self):
        """卸载模型，释放显存"""
        if self.model is not None:
            # 删除模型引用
            del self.model
            # 强制进行垃圾回收
            import gc
            gc.collect()
            # 释放PyTorch缓存的内存
            if self.device == 'cuda':
                torch.cuda.empty_cache()
            print("模型已卸载，显存已释放")
            self.model = None
        else:
            print("没有加载模型，无需卸载")
    
    def run_yolo(self, imgs, save_paths, copy_save_paths, iou_threshold=0.95):

        # results1 = det_model.predict(imgs, imgsz=640, conf=0.15)  # 模型预测结果
        results1 = self.model.predict(
                                    imgs,
                                    imgsz=640,
                                    conf=0.15,       # 提高置信度阈值过滤低质量检测
                                    iou=0.15,        # 降低IOU阈值增强重叠框抑制
                                    agnostic_nms=True,  # 启用跨类别NMS处理同类目标
                                    )
        all_mols = []
        all_bboxes = []
        index_bbox_all_page = []
        
        for idx in range(len(imgs)):
            result1 = results1[idx]
            img = imgs[idx]
            save_path = save_paths[idx]
            copy_save_path = copy_save_paths[idx]
            img_width, img_height = img.size
            img_area = img_width * img_height
            
            
            mols = []
            bboxes = []
            index_bbox_per_page = []
            boxes1 = result1.boxes
            total_box_area = 0
            # print(f'{save_path}检测到{len(boxes1)}')

            for xyxy in boxes1.xyxy:
                x1, y1, x2, y2 = xyxy.detach().cpu().numpy()
                box_area = (x2 - x1) * (y2 - y1)
                total_box_area += box_area

            if total_box_area / img_area > iou_threshold:
                mols.append(img)
                bboxes.append([0, 0, 1, 1])
                img = draw_bbox_for_normalized(img, [0, 0, 1, 1], 0, 0.1 )
                index_bbox_per_page = [0]

            else:
                index = 0
                for xyxy in boxes1.xyxy:
                    x1, y1, x2, y2 = xyxy.detach().cpu().numpy()
                    index_bbox_per_page.append(index)
                    mols.append(img.crop((x1, y1, x2, y2)))
                    bboxes.append([x1 / img_width, y1 / img_height, (x2-x1)/ img_width, (y2-y1)/img_height])
                    draw_bbox_xywh(img, x1 / img_width, y1 / img_height, (x2-x1)/ img_width, (y2-y1)/img_height, index)
                    index += 1

            # if len(bboxes) > 0:
            #     img.save(save_path)
            #     img.save(copy_save_path)
            try:
                img.save(save_path)
            except Exception as e:
                print(f"保存图像失败：{e}，路径：{save_path}")
            try:
                img.save(copy_save_path)
            except Exception as e:
                print(f"保存图像失败：{e}，路径：{copy_save_path}")
            all_mols.append(mols)
            all_bboxes.append(bboxes)
            index_bbox_all_page.append(index_bbox_per_page)
        return all_mols, all_bboxes, index_bbox_all_page
    
    def run_yolo_batch(self, name, image_path_batch, save_dir, batch_size=64):
        # os.makedirs(os.path.join(save_dir, name, "images_with_bbox"), exist_ok=True)
        os.makedirs(os.path.join(save_dir, name, "images_with_bbox"), exist_ok=True)

        for idx in range(0, len(image_path_batch), batch_size):
            iamge_paths_temp = image_path_batch[idx:idx + batch_size]

            imgs = [Image.open(img_path) for img_path in iamge_paths_temp]
            save_paths = [os.path.join(save_dir, name, "images_with_bbox", os.path.basename(img_path))  for img_path in iamge_paths_temp]
            copy_save_paths = [os.path.join(save_dir, name, "images_operated", os.path.basename(img_path))  for img_path in iamge_paths_temp]

            _, all_bboxes, index_bbox_all_page = self.run_yolo(imgs, save_paths, copy_save_paths)
        return all_bboxes, index_bbox_all_page

# 使用示例
if __name__ == "__main__":
    # 创建模型处理器实例
    handler = YOLOModelHandler()
    
    # 加载模型（可以是预训练模型或自定义模型）
    handler.load_model('yolov8n.pt')
    
    # 使用模型进行预测
    results = handler.predict(source="path/to/your/image.jpg")
    
    # 处理预测结果
    if results:
        for result in results:
            boxes = result.boxes  # 边界框信息
            masks = result.masks  # 分割掩码信息
            probs = result.probs  # 分类概率信息
            # 可以在这里对结果进行进一步处理
    
    # 完成所有预测任务后卸载模型
    handler.unload_model()    