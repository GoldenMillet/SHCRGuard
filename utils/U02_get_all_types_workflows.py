"""
    从csv中的workflow字段中提取出所有的workflow并且保存至文件夹
"""

import os
import pandas as pd

# 设置路径
csv_path = '../all_types_workflows.csv'
output_dir = '../all_types_workflows_yaml'
os.makedirs(output_dir, exist_ok=True)

if __name__ == '__main__':
    # 读取 CSV 文件
    df = pd.read_csv(csv_path)

    # 检查字段
    if 'workflow_yaml' not in df.columns:
        raise ValueError("❌ CSV 中未找到 workflow_yaml 字段。")

    # 遍历并写出为 .yml 文件
    for idx, row in df.iterrows():
        content = row['workflow_yaml']

        # 如果为空跳过
        if pd.isna(content) or not str(content).strip():
            continue

        # 创建文件名：例如 workflow_001.yml
        file_name = f"workflow_{idx:04}.yml"
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 已保存: {file_name}")

    print("🎉 所有 workflow 已保存完毕。")
