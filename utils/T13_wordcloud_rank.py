import re
import pandas as pd
import requests
import os
import math
import ast
import csv

from utils.L04_secrets import GITHUB_TOKEN


def extract_between_underscore_dot(text):
    match = re.search(r'_([^_]*)\.', text)
    return match.group(1) if match else None

def get_repos_name(wf_repo_name_list):

    wf_idx_list = [[], [], [], [], []]
    for i in range(0, 5):
        with open(f'../workflows_rank/wf_id/{i}.txt', 'r') as file:
            lines = file.readlines()
            for name in lines:
                wf_idx_list[i].append(extract_between_underscore_dot(name))

    df = pd.read_csv(f'../all_types_workflows.csv')
    for index, row in df.iterrows():
        for i in range(0, 5):
            if str(index) in wf_idx_list[i]:
                wf_repo_name_list[i].append(row['repo'])

    for i in range(0, 5):
        wf_repo_name_list[i] = list(set(wf_repo_name_list[i]))
    return wf_repo_name_list

if __name__ == '__main__':

    # 得到每个workflow对应的repos的名字
    wf_repo_name_list = [[], [], [], [], []]
    wf_repo_name_list = get_repos_name(wf_repo_name_list)
    print(wf_repo_name_list)
    for i in range(0, 5):
        with open(f'../workflows_rank/wf_name/{i}.txt', 'w') as file:
            for item in wf_repo_name_list[i]:
                file.write(item + '\n')

    # 找到所有对应的标签
    for i in range(0, 5):
        target_lists = wf_repo_name_list[i]
        for repo_full_name in target_lists:
            try:
                owner, repo = repo_full_name.split("/", 1)
                url = f"https://api.github.com/repos/{owner}/{repo}/topics"
                headers = {
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"token {GITHUB_TOKEN}"
                }
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Failed to fetch topics for {repo_full_name}: "
                        f"{response.status_code} {response.text}"
                    )
                data = response.json()
                tags = data.get("names", [])

                base_dir = f'../workflows_rank/wf_tags/{i}'
                file_path = f'{base_dir}/{owner} - {repo}.txt'
                os.makedirs(base_dir, exist_ok=True)
                with open(file_path, 'w') as file:
                    for item in wf_repo_name_list[i]:
                        file.write(str(tags) + '\n')
                print(repo_full_name, "✅下载输出成功")
            except Exception:
                print(repo_full_name, "❌下载输出失败")

    # 收集标签
    tags_freq_list = [{}, {}, {}, {}, {}]
    for current_rank in range(0, 5):
        for filename in os.listdir(f"../workflows_rank/wf_tags/{current_rank}"):
            file_path = os.path.join(f"../workflows_rank/wf_tags/{current_rank}", filename)
            with open(file_path, 'r') as file:
                tag_list = file.readlines()
                tag_list = ast.literal_eval(tag_list[0][:-1])
                for tag in tag_list:
                    if tags_freq_list[current_rank].get(tag, None):
                        tags_freq_list[current_rank][tag] += 1
                    else:
                        tags_freq_list[current_rank][tag] = 1

    for i in range(0, 5):
        data = tags_freq_list[i]
        data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
        tags_freq_list[i] = data

    tags_freq_list_front = [{}, {}, {}, {}, {}]
    for current_rank in range(0, 5):
        k = max(5, math.ceil(len(tags_freq_list[current_rank]) * 0.1))
        k = min(20, k)
        sorted_items = sorted(
            tags_freq_list[current_rank].items(),
            key=lambda x: x[1],
            reverse=True
        )
        tags_freq_list_front[current_rank] = dict(sorted_items[:k])

    print("排名前几的tag分别为：")
    idx = 0
    for item in tags_freq_list_front:
        print(f"{idx} ->", item, "\n")
        idx += 1

    # 保存所有结果
    with open('../workflows_rank/wf_tags/tag_freq.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['rank', 'key', 'value'])
        for i in range(0, 5):
            data = tags_freq_list[i]
            for k, v in data.items():
                writer.writerow([i, k, v])
    with open('../workflows_rank/wf_tags/tag_freq_front.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['rank', 'key', 'value'])
        for i in range(0, 5):
            data = tags_freq_list_front[i]
            for k, v in data.items():
                writer.writerow([i, k, v])