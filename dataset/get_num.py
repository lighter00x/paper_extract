from pathlib import Path

def get_paper_dirs(root_dir: Path):
    """获取根目录下所有论文子文件夹"""
    return [p.name for p in root_dir.iterdir() if p.is_dir()]
target_dir = "/home/xq/Mol/dataset/pdf_part_4"
root_dir = Path(target_dir)
paper_dirs = get_paper_dirs(root_dir)  
length = len(paper_dirs)
print(f"{target_dir}目录下共有{length}个子目录")