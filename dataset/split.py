import os
import shutil
import argparse
from pathlib import Path

def copy_subdirectories(source_dir, target_dir, start_index, end_index):
    """
    复制指定区间内的子目录到目标路径
    
    参数:
    source_dir (str): 源目录路径
    target_dir (str): 目标目录路径
    start_index (int): 开始索引（包含）
    end_index (int): 结束索引（包含）
    """
    # 确保源目录存在
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"源目录不存在: {source_dir}")
    
    # 创建目标目录（如果不存在）
    os.makedirs(target_dir, exist_ok=True)
    
    # 获取源目录下的所有子目录，并按名称排序
    subdirectories = [name for name in os.listdir(source_dir) 
                      if os.path.isdir(os.path.join(source_dir, name))]
    subdirectories.sort()
    
    # 计算实际要复制的子目录
    total_subdirs = len(subdirectories)
    if start_index < 0:
        start_index = 0
    if end_index >= total_subdirs:
        end_index = total_subdirs - 1
    
    if start_index > end_index:
        print("警告: 开始索引大于结束索引，没有子目录被复制。")
        return
    
    # 复制指定区间的子目录
    for i in range(start_index, end_index + 1):
        subdir_name = subdirectories[i]
        src_subdir = os.path.join(source_dir, subdir_name)
        dst_subdir = os.path.join(target_dir, subdir_name)
        
        print(f"复制 {src_subdir} 到 {dst_subdir}")
        
        try:
            # 使用shutil.copytree复制目录树
            shutil.move(src_subdir, dst_subdir)
        except FileExistsError:
            print(f"警告: 目标目录已存在: {dst_subdir}，跳过")
        except Exception as e:
            print(f"错误: 复制目录 {src_subdir} 时出错: {e}")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='复制指定区间的子目录')
    parser.add_argument('--source', default='/home/xq/Mol/dataset/pdf_part_4')
    parser.add_argument('--target', default='/home/xq/Mol/dataset/pdf_part_4_copy')
    parser.add_argument('--start', type=int, default=0, help='开始索引（包含）')
    parser.add_argument('--end', type=int,default=99, help='结束索引（包含）')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 调用复制函数
    try:
        copy_subdirectories(args.source, args.target, args.start, args.end)
        print("复制完成!")
    except Exception as e:
        print(f"执行脚本时出错: {e}")

if __name__ == "__main__":
    main()