import os
import random
import shutil
from pathlib import Path

# 配置参数
num_files = 300  # 要选择的文件数量
source_folder = "../2015_downloaded_workflows_only_YML"  # 源文件夹
target_folder = f"../test_workflows_vr_{num_files}"  # 目标文件夹

def select_random_workflows(source_folder, target_folder, num_files):
    """
    从源文件夹中随机选择指定数量的workflow文件并复制到目标文件夹

    Args:
        source_folder (str): 源文件夹路径 (all_types_workflows_yaml)
        target_folder (str): 目标文件夹路径
        num_files (int): 要选择的文件数量，默认200
    """

    # 确保源文件夹存在
    source_path = Path(source_folder)
    if not source_path.exists():
        print(f"错误：源文件夹 '{source_folder}' 不存在")
        return

    # 获取所有yml和yaml文件
    yml_files = []
    for ext in ['*.yml', '*.yaml']:
        yml_files.extend(source_path.glob(ext))

    # 过滤出文件（排除文件夹）
    workflow_files = [f for f in yml_files if f.is_file()]

    print(f"在 '{source_folder}' 中找到 {len(workflow_files)} 个workflow文件")

    # 检查文件数量
    if len(workflow_files) < num_files:
        print(f"警告：源文件夹中只有 {len(workflow_files)} 个文件，少于请求的 {num_files} 个")
        num_files = len(workflow_files)

    # 随机选择文件
    selected_files = random.sample(workflow_files, num_files)

    # 创建目标文件夹
    target_path = Path(target_folder)
    target_path.mkdir(parents=True, exist_ok=True)

    # 复制文件
    success_count = 0
    failed_files = []

    for i, file_path in enumerate(selected_files, 1):
        try:
            # 复制文件到目标文件夹
            target_file = target_path / file_path.name
            shutil.copy2(file_path, target_file)
            success_count += 1
            print(f"[{i}/{num_files}] 复制成功: {file_path.name}")
        except Exception as e:
            failed_files.append((file_path.name, str(e)))
            print(f"[{i}/{num_files}] 复制失败: {file_path.name} - {e}")

    # 输出结果统计
    print(f"\n=== 复制完成 ===")
    print(f"成功复制: {success_count} 个文件")
    print(f"失败: {len(failed_files)} 个文件")
    print(f"目标文件夹: {target_folder}")

    if failed_files:
        print(f"\n失败的文件：")
        for filename, error in failed_files:
            print(f"  - {filename}: {error}")


def main():
    print(f"开始从 '{source_folder}' 中随机选择 {num_files} 个workflow文件...")
    print(f"目标文件夹: '{target_folder}'")
    print("-" * 50)

    # 设置随机种子（可选，用于结果可重现）
    # random.seed(42)

    # 执行文件选择和复制
    select_random_workflows(source_folder, target_folder, num_files)


if __name__ == "__main__":
    main()