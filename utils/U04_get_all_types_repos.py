"""
    从csv中的workflow字段中提取出所有的workflow并且保存至文件夹
"""

import os
import pandas as pd

# 设置路径
csv_path = '../all_types_workflows.csv'

if __name__ == '__main__':
    # 读取 CSV 文件
    df = pd.read_csv(csv_path)

    # 检查字段
    if 'workflow_yaml' not in df.columns:
        raise ValueError("❌ CSV 中未找到 workflow_yaml 字段。")

    # 遍历并写出为 .yml 文件
    repos_list = []
    for idx, row in df.iterrows():
        content = row['repo']
        repos_list.append(content)

        print(f"✅ 已保存: {content}")

    repos_list = list(set(repos_list))
    print("🎉 完毕。" + f"{len(repos_list)}")
