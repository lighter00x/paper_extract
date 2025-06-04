import os
import shutil
import argparse
from pathlib import Path

def move_subdirectories(source_parent: str, dest_parent: str, overwrite: bool = False) -> None:
    if not os.path.exists(source_parent):
        raise FileNotFoundError(f"源目录不存在: {source_parent}")
    os.makedirs(dest_parent, exist_ok=True)
    subdirectories = [d for d in os.listdir(source_parent) if os.path.isdir(os.path.join(source_parent, d))]
    
    for subdir in subdirectories:
        source_subdir = os.path.join(source_parent, subdir)
        dest_subdir = os.path.join(dest_parent, subdir)
        
        # 处理整个子目录的覆盖逻辑
        if os.path.exists(dest_subdir) and overwrite:
            shutil.rmtree(dest_subdir)
            print(f"已删除现有目录: {dest_subdir}")
        
        # 递归复制目录（Python 3.8+ 支持 dirs_exist_ok 参数）
        try:
            shutil.copytree(source_subdir, dest_subdir, dirs_exist_ok=overwrite)
            print(f"已复制目录: {source_subdir} -> {dest_subdir}")
        except FileExistsError:
            print(f"目录已存在且未启用覆盖: {dest_subdir}")
            continue
        
        # 如果源子目录为空，删除它
        if not os.listdir(source_subdir):
            os.rmdir(source_subdir)
            print(f"删除空目录: {source_subdir}")

def main():
    parser = argparse.ArgumentParser(description="将父目录下的所有子目录内容移动到另一个路径")
    parser.add_argument("-source", default="/home/xq/Mol/dataset/pdf_part_4_copy", help="源父目录路径")
    parser.add_argument("-destination", default="/home/xq/label_tool/data", help="目标父目录路径")
    parser.add_argument("-f", "--force", action="store_true", help="覆盖已存在的文件/目录")
    args = parser.parse_args()
    
    try:
        move_subdirectories(args.source, args.destination, args.force)
        print("操作完成!")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()