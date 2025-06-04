import os
import shutil
import argparse

def delete_duplicate_directories(path_a, path_b, dry_run=False):
    """
    删除路径A中与路径B重复的子目录
    
    参数:
    path_a (str): 源路径，将从中删除重复目录
    path_b (str): 参考路径，用于检查重复项
    dry_run (bool): 是否进行试运行，不实际删除目录
    """
    # 确保路径存在
    if not os.path.exists(path_a):
        print(f"错误: 路径A '{path_a}' 不存在")
        return
    
    if not os.path.exists(path_b):
        print(f"错误: 路径B '{path_b}' 不存在")
        return
    
    # 获取路径B下的所有子目录
    b_subdirs = set()
    for root, dirs, _ in os.walk(path_b):
        # 计算相对于path_b的相对路径
        rel_path = os.path.relpath(root, path_b)
        if rel_path == '.':  # 跳过根目录
            continue
        b_subdirs.add(rel_path)
    
    # 检查路径A中是否存在相同的子目录并删除
    for root, dirs, _ in os.walk(path_a, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            rel_path = os.path.relpath(dir_path, path_a)
            
            if rel_path in b_subdirs:
                print(f"发现重复目录: {rel_path}")
                if dry_run:
                    print(f"[试运行] 本应删除: {dir_path}")
                else:
                    try:
                        shutil.rmtree(dir_path)
                        print(f"已删除: {dir_path}")
                    except Exception as e:
                        print(f"无法删除 {dir_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='删除路径A中与路径B重复的子目录')
    parser.add_argument("-path_a",default='/home/xq/Mol/dataset/pdf_part_4', help='源路径，将从中删除重复目录')
    parser.add_argument("-path_b",default='/home/xq/Mol/dataset/pdf_part_4_copy', help='参考路径，用于检查重复项')
    
    args = parser.parse_args()
    
    print(f"路径A: {args.path_a}")
    print(f"路径B: {args.path_b}")

    print("-" * 50)
    
    delete_duplicate_directories(args.path_a, args.path_b,False)    