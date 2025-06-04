import os
import csv
import time
import random
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from Utils.util_images import image_segment_given_box_xywh, encode_image
from Utils.logger import Log
from Utils.utils import csv_lines, read_markdown_file, message_split, save_to_markdown
from mol_recognize import call_img2mol, retry_with_backoff  # 分子识别API调用和重试机制
from detection_yolo.yoloManger import YOLOModelHandler
from client.client import LlmClient

# 支持的图片扩展名
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

class Processor():
    def __init__(self, root_dir, mode):
        """
        初始化传入参数是所有文档的根目录
        """
        self.root_dir = Path(root_dir)
        self.error_paper_record = []
        self.error_page_record = []
        self.mode = mode  
        # log = Log(log_file="my_app.log")
        
    def init_model(self):
        # 创建yolo管理模型model实例
        handler = YOLOModelHandler()
        # 加载模型（可以是预训练模型或自定义模型）
        handler.load_model()
        return handler
    
    def initialize_path(self,args):
        self.prompt_file_image =  "/home/xq/Mol/Paper_extract/prompts/prompt_image_new.md"        # 提示词文件路径
        self.prompt_file_smiles = "/home/xq/Mol/Paper_extract/prompts/smiles.md"
        self.prompt_file_paper = "/home/xq/Mol/Paper_extract/prompts/prompt_new.md"
        self.prompt_file_common = "/home/xq/Mol/Paper_extract/prompts/prompt_image_common.md"
        
    
    def initialize_client(self):
        """初始化LLM API客户端"""
        load_dotenv()  # 加载当前目录的 .env 文件
        self.model_llm = os.getenv("OPENAI_MODEL", "gemini-2.0-flash")
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        # base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        # api_key = "sk-eba56dd4a295452e9af587cbecfc6350"
        return LlmClient(self.model_llm, api_key, base_url)
    
    def prompt_read(self):
        prompt_image = read_markdown_file(self.prompt_file_image)
        prompt_smiles = read_markdown_file(self.prompt_file_smiles)
        prompt_paper = read_markdown_file(self.prompt_file_paper)
        prompt_image_common = read_markdown_file(self.prompt_file_common)
        return prompt_image, prompt_smiles, prompt_paper, prompt_image_common

    def get_paper_dirs(self, root_dir: Path):
        # 传入self.root_dir
        """获取根目录下所有论文子文件夹"""
        return [p.name for p in root_dir.iterdir() if p.is_dir()]
    
    def get_image_paths(self, root_dir: Path, paper_dirs: list, target_path: str):
        """
        获取所有论文对应的图片路径,返回嵌套列表
        target_path是需要读取的子目录
        """
        all_image_files = []
        for paper in paper_dirs:
            # 构建每个论文的图片目录路径
            image_dir = root_dir / paper / target_path
            # 筛选出支持的图片文件
            images = [f for f in image_dir.iterdir()
                    if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS] if image_dir.exists() else []
            all_image_files.append(images)
        return all_image_files
    
    def detection_for_image(self, image_path, bboxes_per_page, index_bbox_per_page, save_bbox_path, api_base):
        temp_page = []
        temp_data = []
        temp = 0
        # 处理每个检测到的边界框
        for bbox_item, index_bbox_item in zip(bboxes_per_page, index_bbox_per_page):
            temp = temp + 1
            x, y, w, h = bbox_item
            # 生成裁剪后的图片路径
            temp_image_path = save_bbox_path / f"{Path(image_path).name}_image_{index_bbox_item}.png"
            # 裁剪图片区域
            image_segment_given_box_xywh(image_path, temp_image_path, x, y, w, h)
            try:
                # 调用分子识别API获取SMILES
                bbox_smiles = retry_with_backoff(lambda: call_img2mol(api_base, temp_image_path))
                # bbox_smiles= escape_tags(bbox_smiles)
                
            except Exception as e: 
                bbox_smiles = "ERROR"
                # print(f"[ERROR] SMILES recognition failed: {e}")
                bbox_smiles = retry_with_backoff(lambda: call_img2mol("http://localhost:50008", temp_image_path))
                if bbox_smiles == "ERROR":
                    print(f"[ERROR] SMILES recognition failed: {e}")
                    continue
                else:
                    print(f"转换ip后成功")
            time.sleep(random.uniform(2, 3))  # 添加随机延迟防止API过载
            temp_page.append([
                        index_bbox_item,
                        bbox_smiles,
                    ])
            temp_data.append([
                        f"images/{Path(image_path).name}",
                        index_bbox_item,
                        bbox_smiles,
                        x, y, w, h
                    ])
        # print(f"{image_path}共处理{temp}个分子")
        return temp_page, temp_data

    def detection_for_paper(self, paper_name, image_batch, csv_path, root_dir, batch_size, api_base, model_yolo:YOLOModelHandler):
        """
        处理单篇论文的所有图片：检测分子并识别SMILES
        paper_name:单篇论文名
        image_batch:该论文的所有图像路径列表
        """
        print(f"Processing paper: {paper_name}")
        # 创建保存边界框裁剪结果的目录，这里创建是为了避免后面重复创建
        save_bbox_path = root_dir / paper_name / "image_from_bbox"
        # if not save_bbox_path.is_dir():
        Path(save_bbox_path).mkdir(parents=True, exist_ok=True)
        # ========================================================================#
        # 调用YOLO检测获取边界框信息
        try:
            bboxes_paper, index_bbox_all_page = model_yolo.run_yolo_batch(paper_name, image_batch, root_dir, batch_size)
        except Exception as e:
            print(f"[ERROR] YOLO detection failed for {paper_name}: {e}")
        # ========================================================================#
        # all_data是属于最终写入文件的部分，包含bbox
        # data_page汇集的是这一页的信息，不包含bbox
        all_data = []
        data_page = [] 
        # ========================遍历每张图片及其检测结果==========================#
        for image_path, bboxes_per_page, index_bbox_per_page in zip(image_batch, bboxes_paper, index_bbox_all_page):
            if not bboxes_per_page:
                data_page.append(pd.DataFrame())
                continue
            # print(f"{image_path} 检测到 {len(bboxes_per_page)} 个目标")
            try:
                # ========================每张图像=================================#
                temp_page, temp_data = self.detection_for_image(image_path, bboxes_per_page, index_bbox_per_page, save_bbox_path, api_base)
                # 收集结果数据
                # data_page是imag_path的数据，每一个图像都会记录，空的即为[]
                # all_data包含所有的内容，有bbox的图像才会记录
                data_page.append(pd.DataFrame(temp_page, columns=['Bbox_Index', 'SMILES']))
                all_data = all_data + temp_data
            except Exception as e:
                    print(f"Error processing {paper_name}的{image_path.name}文件出错: {e}")
                    # 记录出错图像
                    self.error_paper_record.append(paper_name)
                    continue
        # 将结果写入CSV文件（如果all_data不为空）
        if all_data:  # 检查all_data是否包含数据
            df = pd.DataFrame(all_data, columns=['Image_Path', 'Bbox_Index', 'SMILES', 'Bbox_X', 'Bbox_Y', 'Bbox_Width', 'Bbox_Height'])
            # df_page = pd.DataFrame(data_page, columns=['Image_Path', 'Bbox_Index', 'SMILES', 'Bbox_X', 'Bbox_Y', 'Bbox_Width', 'Bbox_Height'])
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"已保存检测结果到: {csv_path}")
            return image_batch, data_page, df
        else:
            print("检测结果为空，未生成CSV文件。")
            return [], [], []
        
    def detection(self):
        api_base = "http://101.126.35.171:50008"
        handler = self.init_model()
        # 这里是调用上方函数处理某一批论文
        paper_dirs = self.get_paper_dirs(self.root_dir)  # 获取所有论文目录
        all_image_files = self.get_image_paths(self.root_dir, paper_dirs, target_path = "auto/images")  # 获取所有图片路径
        idx = 1
        # ================================大循环，所有的文章================================#
        data_pages = []
        for paper_name, image_batch in zip(paper_dirs, all_image_files):
            print(f"正在处理第{idx}篇论文：{paper_name}")
            idx=idx+1
            os.makedirs(os.path.join(self.root_dir, paper_name, "images_operated"), exist_ok=True)
            information_folder = self.root_dir / paper_name / "information_image"
            os.makedirs(information_folder, exist_ok=True)
            # 接下来遍历每篇文章下的图像
            if not image_batch:
                print(f"[INFO] No images found in {paper_name}, skipping.")
                continue
            # print(f"{image_batch}")
            # =======================检查是否处理过================================#
            csv_path = self.root_dir / paper_name / "molecule_detection_results.csv"
            if not os.path.exists(csv_path):
                _, data_page, all_data = self.detection_for_paper(paper_name, image_batch, csv_path, self.root_dir, 64, api_base, handler)
            else:
                print(f"文件已存在 - {csv_path}")
                csv_bool = csv_lines(csv_path)
                # 如果行数大于1，跳过当前图片处理，直接读取信息（非跳过
                if csv_bool:
                    print(f"CSV文件 {csv_path} 有效数据，{paper_name}已处理完成，跳过当前图片处理")
                    data_page, all_data = self.get_mol_info(paper_name, image_batch, csv_path)
                    # print(data_page)
                    # print("\n")
                    # print(all_data)
                # 行数不超过1时，需要调用重新处理
                else:
                    print(f"无效数据：{csv_path}，将重新处理")
                    _, data_page, all_data = self.detection_for_paper(paper_name, image_batch, csv_path, self.root_dir, 64, api_base, handler)
            if not data_page:
                self.error_paper_record.append(paper_name)
                continue
            data_pages.append(data_page)
            # ==============================正式处理===============================#
            # self.images_mllm(paper_name, image_batch, data_page)
            if self.mode == "normal":
                content_dict_list = self.stage_two(paper_name, image_batch, data_page)
            else:
                content_dict_list = self.get_file_info(paper_name, image_batch)
            self.stage_three(paper_name, all_data, content_dict_list)
            # =============================保存错误日志============================#
            error_log_dir = self.root_dir / "error_log"
            if not os.path.exists(error_log_dir):
                os.makedirs(error_log_dir)
            filepath = os.path.join(error_log_dir, "error_mol_detect_papers.txt")
            try:
                with open(filepath, "w") as f:
                    f.write("\n".join(self.error_paper_record) + "\n")  # Join the list with newlines
                print(f"Error paper records saved to: {filepath}")
            except Exception as e:
                print(f"Error saving error paper records: {e}")
        # 双层嵌套，三层嵌套
        return all_image_files, data_pages
        
    def images_mllm(self, paper_name, image_batch, data_page):
        self.initialize_path(self)
        llm = self.initialize_client()
        csv_file = self.root_dir / paper_name / "molecule_detection_results.csv"
        prompt_image, prompt_smiles, prompt_paper, prompt_image_common = self.prompt_read()
        # paper_dirs = self.get_paper_dirs(self.root_dir)  # 获取所有论文目录
        # all_image_files = self.get_image_paths(self.root_dir, paper_dirs, target_path = "images_operated")  # 获取所有图片路径
        # ==========================开始处理一篇论文===============================#
        # for name, images_with_bbox_per_paper in zip(paper_dirs, all_image_files):
        combined_content = ""
        for image_single, image_data in zip(image_batch, data_page):
            image_operated = self.root_dir / paper_name / "images_operated" /Path(image_single).name
            md_file_path = self.root_dir / paper_name / "information_image"/ f"{Path(image_single).stem}.md"
            encoded_image = encode_image(image_operated)
            if not encoded_image:
                continue
            try:
                # 此文件中有关于bbox的信息
                if image_data:
                    df_image = pd.DataFrame(image_data, columns = ["Bbox_Index", "SMILES"])
                    result = df_image.to_dict('records')
                    prompt_image_desciption = f"图像理解任务：\n{prompt_image},\n附加信息这里的Bbox_Index表示的是图中分子的框，SMILES对应的是该框的分子：\n{result}，\n关于smiles的特殊说明:\n{prompt_smiles}\n"
                else:
                    print(f"简单图像理解任务")
                    prompt_image_desciption = f"图像理解任务:{prompt_image_common}"
                # 调用API
                response = llm.call_chat_images(prompt_image_desciption, encoded_image, "gpt-4o")
                # 先构建完整内容
                content = (
                    f"# Analysis for {Path(image_single).stem}.jpg\n\n"
                    "## Information in the image\n"
                    f"{response}\n"
                )
                # 一次性写入
                with open(md_file_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(content)
                combined_content += content + "\n\n"
            except Exception as e:
                    print(f"Error processing {paper_name}的{image_single}: {e}")
                    self.error_page_record.append({"paper":{paper_name},"image":{image_single}})
                    continue
        dir_paper = self.root_dir / paper_name / "auto"
        markdown_files = []
        #=============================原论文的文本===================================#
        # 再处理专用
        for filename in os.listdir(dir_paper):
            # print(filename)
            file_path = dir_paper / filename
            # 检查文件是否以gemini开头，并且是.md文件
            if filename.endswith(".md"):
                if filename.startswith("gemini"):
                    try:
                        # 删除文件
                        os.remove(file_path)
                        print(f"已删除文件: {file_path}")
                        continue
                    except Exception as e:
                        print(f"无法删除文件 {file_path}: {e}")
                else:
                    markdown_files.append(file_path)
        #============================================================================#
        content_paper = read_markdown_file(markdown_files[0])
        df = pd.read_csv(csv_file)
        df_paper = df.iloc[:, 0:3]
        information = df_paper.to_dict('records')
        content_all = f"论文原文: {content_paper}\n================分割线=================\n论文图像解释: {combined_content}\n================分割线=================\n附加信息：\n{information}，\nsmiles说明:{prompt_smiles}"
        messages = message_split(prompt_paper, content_all)
        response_llm = llm.call_chat_images(messages, None, 0.15)
        save_to_markdown(response_llm, save_dir = self.root_dir / paper_name / "auto", filename = "gemini_md_" + paper_name)
        return
    
    def get_mol_info(self, paper_name, image_batch, csv_path):
        """
        如果发现已有分子的信息，需要逐个读取
        """
        data_page = []
        df = pd.read_csv(csv_path)
        for image in image_batch:
            target_image_path = "images/" + Path(image).name
            # print(target_image_path)
            mol_image = df[df['Image_Path'] == str(target_image_path)]
            if mol_image.empty:
                data_page.append(pd.DataFrame())
            else:
                data_page_3 = mol_image.iloc[:, 0:3]
                data_page.append(data_page_3)
            # data_pages.append(data_page.iloc[:, 0:3] if data_page else [])
        return data_page, df
                
    def get_file_info(self, paper_name, image_batch):
        md_folder = self.root_dir/ paper_name / "information_image"
        content_dict_list = []
        for image in image_batch:
            md_file_path = md_folder / f"{Path(image).stem}.md"  # 保存路径

            # 检查文件是否存在
            if os.path.exists(md_file_path) and os.path.isfile(md_file_path):
                try:
                    # 读取MD文件内容
                    with open(md_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 构建内容字典并添加到列表
                    content_dict = {
                        "path":f"images/{Path(image).name}",
                        "description of image":f"{content}"
                    }
                    content_dict_list.append(content_dict)
                    
                except Exception as e:
                    print(f"Error reading {md_file_path}: {e}")
            else:
                print(f"File not found: {md_file_path}")
        return content_dict_list 

    def stage_two(self, paper_name, image_batch, data_page:list[pd.DataFrame]):
        """
        已经有图像分子数据，进行图像理解任务，根据data_page来
        """
        self.initialize_path(self)
        llm = self.initialize_client()
        md_folder = self.root_dir/ paper_name / "information_image"
        prompt_image, _, _, prompt_image_common = self.prompt_read()
        # combined_content = ""   # 拼接内容
        content_dict_list = []
        # 已存在图像的目录
        # print(f"===========>image_batch{image_batch},\ndata_batch:{data_page}")
        images_operated_path = self.root_dir / paper_name /"images_operated"    
        for image_operated, image_data in zip(image_batch, data_page):
            md_file_path = md_folder / f"{Path(image_operated).stem}.md"  # 保存路径
            image_operated = images_operated_path / Path(image_operated).name   # 需要处理的图像
            if not os.path.exists(image_operated):
                image_operated = self.root_dir / paper_name / "auto" / "images" / Path(image_operated).name
            # print(f"图像理解：{image_operated}")
            # print(image_data.empty)
            encoded_image = encode_image(image_operated)
            if not encoded_image:
                continue
            try:
                if image_data.empty:
                    # 说明这是一个非分子图
                    # print(f"简单图像理解任务{image_operated}")
                    prompt_image_desciption = f"图像理解任务:{prompt_image_common}"
                else:
                    # print(f"单图附加信息：{image_data}")
                    # print(f"分子图像理解任务{image_operated}")
                    prompt_image_desciption = f"图像理解任务：{prompt_image},附加信息这里的Bbox_Index表示的是图中分子的框，SMILES对应的是该框的分子：{image_data}"
                response = llm.call_chat_images( prompt_image_desciption, encoded_image, self.model_llm)
                content = (
                        f"# 对图像 images/{Path(image_operated).name} 的描述信息\n\n"
                        f"{response}\n" 
                    )
                content_dict_list.append({"path":f"images/{Path(image_operated).name}","description of image":f"{response}" })
                # 一次性写入
                with open(md_file_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(content)
                # combined_content += content + "\n\n"  # 前期使用字符串拼接
            except Exception as e:
                print(f"Error processing {paper_name}的{image_operated}: {e}")
                self.error_paper_record.append(paper_name)
                self.error_page_record.append({"paper":{paper_name},"image":{image_operated}})
                continue
            
        return content_dict_list
            
    def stage_three(self, paper_name, all_data, content_dict_list:dict):
        """
        已经有各项数据，只进行最后一步的工作
        """
        self.initialize_path(self)
        llm = self.initialize_client()
        _, prompt_smiles, prompt_paper, _ = self.prompt_read()
        #================================================================#
        # 再处理专用
        dir_paper = self.root_dir/ paper_name /"auto"
        markdown_files = []
        for filename in os.listdir(dir_paper):
            # print(filename)
            file_path = dir_paper / filename
            # 检查文件是否以gemini开头，并且是.md文件
            if filename.endswith(".md"):
                if filename.startswith("gemini"):
                    try:
                        # 删除文件
                        os.remove(file_path)
                        print(f"已删除文件: {file_path}")
                        continue
                    except Exception as e:
                        print(f"无法删除文件 {file_path}: {e}")
                else:
                    markdown_files.append(file_path)
        #================================================================#
        content_paper = read_markdown_file(markdown_files[0])
        information = dict(all_data.iloc[:, 0:3])   # 所有图像的分子信息
        content_all = f"论文原文: {content_paper}\n=================================\n论文中各图像解释: {content_dict_list}\n=================================\n附加信息：\n{information}，\nsmiles说明:{prompt_smiles}"
        messages = message_split(prompt_paper, content_all)
        response = llm.call_chat_text(messages, self.model_llm)
        save_to_markdown(response, save_dir = self.root_dir / paper_name / "auto", filename = "gemini_md_" + paper_name)
        