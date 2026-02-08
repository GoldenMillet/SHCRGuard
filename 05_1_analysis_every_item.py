import re

check_list = ["check_for_3p_actions_without_hash",
              "check_for_allow_unsecure_commands",
              "check_for_cache_action",
              "check_for_dangerous_write_permissions",
              "check_for_inline_script",
              "check_for_pull_request_target",
              "check_for_script_injection",
              "check_for_self_hosted_runners",
              "check_for_aws_configure_credentials_non_oidc",
              "check_for_create_or_approve_pull_request",
              "check_for_remote_script",
              "check_for_upload_download_artifact_action",
              "check_for_non_github_managed_actions"]

log_path = 'ghast_run.log'
target_title = check_list[7]
output_path = target_title + ".log"

if __name__ == '__main__':

    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # 保存结果
    results = {}
    current_file = None
    collecting_info = False
    info_buffer = []

    for line in lines:
        # 识别新文件的路径
        file_match = re.search(r'FILE => .*?([\w\-]+__[\w\-]+__.+?\.(yml|yaml))', line)
        if file_match:
            current_file = file_match.group(1)
            collecting_info = True
            info_buffer = [line]
            continue

        # 收集当前文件相关的 INFO 日志
        if collecting_info and current_file:
            if 'INFO' in line or 'WARN' in line or 'DEBUG' in line:
                info_buffer.append(line)

        # 遇到 FAIL 且是我们关注的 check，则记录
        if 'FAIL' in line and target_title in line:
            if current_file:
                results[current_file] = list(info_buffer)  # 复制内容
                current_file = None
                collecting_info = False
                info_buffer = []
        # 若出现新风险类型则停止收集当前文件的 INFO
        elif 'FAIL' in line and target_title not in line:
            current_file = None
            collecting_info = False
            info_buffer = []

    # 写入输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        for filename, infos in results.items():
            f.write(f"\n===== {filename} =====\n")
            for line in infos:
                f.write(line)

    print(f"✅ 提取完成，共提取 {len(results)} 个文件，结果写入：{output_path}")