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

if __name__ == '__main__':

    # 读取GHAST文件
    ghast_summary = []
    with open("ghast_run.log", "r", encoding="utf-8") as summary_doc:
        for line in summary_doc:
            text = line.strip()
            ghast_summary.append(text)
    print("已经成功读取GHAST文件", len(ghast_summary), "个条目")

    # 分析每个条目的内容
    check_list_sum = [0] * 13
    for line in ghast_summary:
        for i in range(0, 13):
            if check_list[i] in line:
                check_list_sum[i] += 1

    # 输出所有的内容
    for i in range(0, 13):
        print("软件漏洞", check_list[i], "总共出现", check_list_sum[i], "次！")

    print("\n全部完毕")
