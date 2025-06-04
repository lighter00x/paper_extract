import os
import csv
import glob
from pathlib import Path

def csv_lines(csv_path):
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        row_count = 0
        for row in reader:
            # 跳过空行（仅包含空白字符的行）
            if any(cell.strip() for cell in row):
                row_count += 1
                # 若行数超过 1，可提前终止循环提高效率
                if row_count > 1:
                    return True
        return False
        
def find_gemini_md_files(root_dir):
    # 通配符：当前目录下以 "gemini" 开头的 .md 文件
    pattern = os.path.join(root_dir, "gemini*.md")
    return glob.glob(pattern)

def truncate_at_first_header(content: str) -> str:
    """
    截断文档内容，从第一个 # 开始保留后面的内容
    
    :param content: 原始文档内容
    :return: 截断后的内容（如果找到 #），否则返回空字符串
    """
    # 查找第一个 # 的位置
    header_pos = content.find('#')
    
    if header_pos == -1:
        return ""
    
    return content[header_pos:]

# 读取指定路径下的文件
def read_markdown_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print("错误: 文件未找到。")
    except Exception as e:
        print(f"错误: 发生未知错误: {e}")
    return None


# 将目标内容存进指定文件夹下，并指定文件名
def save_to_markdown(api_result, save_dir, filename=None):
    """
    将API返回的结果保存为Markdown文件
    
    参数:
        api_result: DS()函数返回的字典，包含 reasoning_content 和 content
        save_dir: 保存目录
        filename: 自定义文件名(不带.md后缀)，若为None则自动生成时间戳文件名
        
    返回:
        成功时返回文件路径，失败返回None
    """
    try:
        # 检查输入有效性
        if not api_result:
            raise ValueError("无效的API返回结果")
            
        # 创建保存目录(如果不存在)
        # os.makedirs(save_dir, exist_ok=True)
        
        # 生成文件名
        filepath = os.path.join(save_dir, f"{filename}.md")
        
        # 构建Markdown内容
        md_content = truncate_at_first_header(api_result)
         
        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        print(f"{filename}结果已保存至: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"[保存Markdown失败] 错误: {e}")
        return None
    
def message_split(prompt, content):
    messages = [{"role": "system", "content": "你是一名文献信息提取助手，根据要求对文献中的有用信息进行提取"},
                {"role": "user", "content": f"{prompt}\n具体的论文内容如下，请按照上面的要求提取信息直接作答：\n{content}"}

    ]
    return messages


def get_paper_dirs(root_dir: Path):
    """获取根目录下所有论文子文件夹"""
    return [p.name for p in root_dir.iterdir() if p.is_dir()]


def get_markdown_paths(root_dir: Path, paper_dirs: list):
    """获取所有论文对应的markdown文件路径"""
    all_markdown_files = []
    for paper in paper_dirs:
        # 构建每个论文的文件目录路径
        file_dir = root_dir / paper / "auto" 
        # print(file_dir)
        # 筛选出markdown文件
        markdown_files = [f for f in file_dir.iterdir()
                         if f.is_file() and f.suffix.lower() == ".md"] if file_dir.exists() else []
        if markdown_files:  # 确保列表不为空
            all_markdown_files.append(markdown_files[0])
    return all_markdown_files

def read_information_images(path: Path):
    # 查找所有.md文件
    md_files = list(path.glob("*.md"))

    # 如果没有找到.md文件
    if not md_files:
        raise FileNotFoundError(f"在目录 {path} 中未找到任何.md文件")

    # 读取并拼接所有.md文件内容
    combined_content = ""
    for md_file in md_files:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                combined_content += f.read() + "\n\n"  # 添加两个换行符分隔不同文件内容
        except Exception as e:
            print(f"读取文件 {md_file} 时出错: {e}")
    return combined_content
