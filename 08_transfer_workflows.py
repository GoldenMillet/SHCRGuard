import os
import shutil


def copy_files_from_list(txt_path, source_dir, dest_dir):
    """
    根据txt文件中的文件名列表，从源目录复制文件到目标目录

    参数:
        txt_path: txt文件的完整路径
        source_dir: 源目录B的路径
        dest_dir: 目标目录C的路径
    """
    # 确保目标目录存在
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"已创建目标目录: {dest_dir}")

    # 读取txt文件并去重
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            filenames = [line.strip() for line in f if line.strip()]

        # 去除重复的文件名
        unique_filenames = list(set(filenames))
        print(f"txt文件中共有 {len(filenames)} 个条目，去重后 {len(unique_filenames)} 个文件")

    except FileNotFoundError:
        print(f"错误: 找不到txt文件: {txt_path}")
        return
    except Exception as e:
        print(f"读取txt文件时出错: {e}")
        return

    # 复制文件
    success_count = 0
    not_found_count = 0
    error_count = 0

    for filename in unique_filenames:
        source_path = os.path.join(source_dir, filename)
        dest_path = os.path.join(dest_dir, filename)

        # 检查源文件是否存在
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, dest_path)
                success_count += 1
                print(f"✓ 已复制: {filename}")
            except Exception as e:
                error_count += 1
                print(f"✗ 复制失败 {filename}: {e}")
        else:
            not_found_count += 1
            print(f"! 文件不存在: {filename}")

    # 输出统计信息
    print("\n" + "=" * 50)
    print(f"复制完成!")
    print(f"成功复制: {success_count} 个文件")
    print(f"未找到: {not_found_count} 个文件")
    print(f"复制失败: {error_count} 个文件")
    print("=" * 50)


if __name__ == "__main__":
    # 配置路径
    txt_file = "./workflow_1518/index_98.txt"  # txt文件路径
    source_directory = "./all_types_workflows_yaml"  # 源目录B
    destination_directory = "./workflow_1518/workflow_93"  # 目标目录C

    # 执行复制操作
    copy_files_from_list(txt_file, source_directory, destination_directory)