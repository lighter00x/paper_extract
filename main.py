import os
from pathlib import Path
from dotenv import load_dotenv
from processor import Processor  # 替换为实际模块名

# ----------------------
# 环境配置
# ----------------------
load_dotenv()  # 加载 .env 文件（需提前创建）

# 配置参数
ROOT_DIR = Path("/home/xq/Mol/dataset/pdf_part_4")  # 论文根目录
MODE = "normal"  # 模式，如果已有information of image，调整至retry，正常情况下即为normal

# ----------------------
# 核心调用流程
# ----------------------
def main():
    # 初始化处理器
    processor = Processor(root_dir = ROOT_DIR, mode = MODE)
    try:
        processor.detection()        
    except Exception as e:
        print(f"[致命错误] 处理流程中断：{str(e)}")
        raise

if __name__ == "__main__":
    main()