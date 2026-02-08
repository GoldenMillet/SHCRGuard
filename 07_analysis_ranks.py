import os
import yaml

# 文件夹路径
workflow_folder = "./2015_downloaded_workflows_only_YML"

event_rank = {
    "fork": 3,
    "issue_comment": 3,
    "issues": 3,
    "pull_request_comment": 3,
    "watch": 3,
    "discussion": 3,  # new added event
    "discussion_comment": 3,  # new added event
    "pull_request": 2,
    "pull_request_target": 2,
    "repository_dispatch": 2,  # new added event
    "pull_request_review": 1,
    "pull_request_review_comment": 1,
    "push": 1,
    "release": 1,
    "workflow_call": 1,
    "workflow_dispatch": 1,
    "workflow_run": 1,
    "schedule": 1,  # new added event
    "merge_group": 1,  # new added event
    "branch_protection_rule": 1,  # new added event
    "check_run": 1,  # new added event
    "check_suite": 1,  # new added event
    "create": 1,  # new added event
    "delete": 1,  # new added event
    "deployment": 1,  # new added event
    "deployment_status": 1,  # new added event
    "gollum": 1,  # new added event
    "label": 1,  # new added event
    "milestone": 1,  # new added event
    "page_build": 1,  # new added event
    "public": 1,  # new added event
    "registry_package": 1,  # new added event
    "status": 1,  # new added event
    "project_card": 1, # new added event (aborded now, but exist in the past workflow files。)
}

sta = [0, 0, 0, 0]

def normalize_on_field(wf_dict):
    if True in wf_dict and "on" not in wf_dict:
        wf_dict["on"] = wf_dict.pop(True)
    return wf_dict

def get_event_ranks(workflow_path):
    with open(workflow_path, 'r', encoding='utf-8') as f:
        try:
            wf = yaml.safe_load(f)
            wf = normalize_on_field(wf)
            if wf is None:
                print(f"[!] Empty or invalid YAML: {workflow_path}")
                return None
        except yaml.YAMLError as e:
            print(f"[!] YAML parsing failed for {workflow_path}: {e}")
            return None

    events = wf.get('on', None)
    results = []

    if events is None:
        return results  # 无触发器，返回空列表

    if isinstance(events, str):
        results.append((events, event_rank.get(events, -1)))
    elif isinstance(events, list):
        for evt in events:
            results.append((evt, event_rank.get(evt, -1)))
    elif isinstance(events, dict):
        for evt in events:
            results.append((evt, event_rank.get(evt, -1)))
    else:
        # print()
        print(f"[!] Unsupported `on:` type in {workflow_path}: {type(events)}")

    return results

def scan_workflows_in_folder(folder_path):
    intex = 1
    seq_rank = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            full_path = os.path.join(folder_path, filename)
            events = get_event_ranks(full_path)
            if events:
                print("\n这是第", intex, "个文件：", filename)
                for evt, rank in events:
                    seq_rank = rank
                    print(f"  └── Event: {evt:<30} | Security Rank: {rank if rank > 0 else 'Unknown'}")
        intex += 1
        sta[seq_rank] += 1

if __name__ == '__main__':
    scan_workflows_in_folder(workflow_folder)
    print("\n\n危害等级统计（idx越大越严重）", sta)