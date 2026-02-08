"""
    安全的作业：
    runs_on = 0 -> 完全没有runs-on标签，绝对安全
    runs_on = 1, runner_flag = 1 -> runner_flag安全，确定是非自托管问题

    疑似不安全的作业基本条件：runs_on = 1, runner_flag = 0
    有下列情形之一的，每有一个加一点：
    permission_flag = 0 -> 自托管且是write权限
    on_trigger_flag = 0 -> 触发条件为PR等
    upload_and_download_flag = 0 -> 涉及上传和下载

"""

from L01_colours import Bash_Colours

def appdnd_output_list(all_runs_on, filename, job_name, runs_on, flags):
    download_upload_flag = flags.upload_flag and flags.download_flag

    # runs_on = 0 -> 完全没有runs-on标签，绝对安全
    # runs_on = 1, runner_flag = 1 -> runner_flag安全，确定是非自托管问题
    if (not runs_on) or (runs_on and flags.runner_flag == 1):
        all_runs_on.append({
            'file': filename,
            'job': job_name,
            'runs_on': runs_on,
            'type': " INFO ",
            'colour': Bash_Colours.BLUE_BG,
            'desc': "安全的作业"
        })
    else:
        # 基本参数初始化
        alert_level = (not flags.permission_flag) + (not flags.on_trigger_flag) + (not download_upload_flag) + (not flags.secrets_exposure_flag)
        type = f"WARN-{alert_level}"
        desc = ""
        colour = ""

        # 决定文字
        if alert_level == 0:
            desc = "攻击面较小的自托管作业 "
        else:
            if flags.permission_flag == 0:
                desc = desc + "拥有写权限的自托管作业 "
            if flags.on_trigger_flag == 0:
                desc = desc + "拥有不安全触发条件的自托管作业 "
            if download_upload_flag == 0:
                desc = desc + "拥有上传下载行为的自托管作业 "
            if flags.secrets_exposure_flag == 0:
                desc = desc + "可能会因上传暴露secrets的自托管作业 "
        desc = desc[:-1]

        # 决定颜色
        if alert_level == 0:
            colour = Bash_Colours.LIGHT_CYAN_BG
        elif alert_level == 1:
            colour = Bash_Colours.GREAN_BG
        elif alert_level == 2:
            colour = Bash_Colours.YELLOW_BG
        elif alert_level >= 3:
            colour = Bash_Colours.RED_BG

        all_runs_on.append({
            'file': filename,
            'job': job_name,
            'runs_on': runs_on,
            'type': type,
            'colour': colour,
            'desc': desc
        })

def appdnd_output_list_github_hosted(all_runs_on_official_hosted, filename, job_name, runs_on, flags):

    download_upload_flag = flags.upload_flag and flags.download_flag
    alert_level = (not flags.permission_flag) + (not flags.on_trigger_flag) + (not download_upload_flag) + (not flags.secrets_exposure_flag)

    type = f"WARN-{alert_level}"
    desc = ""
    colour = ""

    # 决定文字
    if alert_level == 0:
        desc = "攻击面较小的自托管作业 "
    else:
        if flags.permission_flag == 0:
            desc = desc + "拥有写权限的自托管作业 "
        if flags.on_trigger_flag == 0:
            desc = desc + "拥有不安全触发条件的自托管作业 "
        if download_upload_flag == 0:
            desc = desc + "拥有上传下载行为的自托管作业 "
        if flags.secrets_exposure_flag == 0:
            desc = desc + "可能会因上传暴露secrets的自托管作业 "
    desc = desc[:-1]

    # 决定颜色
    if alert_level == 0:
        colour = Bash_Colours.LIGHT_CYAN_BG
    elif alert_level == 1:
        colour = Bash_Colours.GREAN_BG
    elif alert_level == 2:
        colour = Bash_Colours.YELLOW_BG
    elif alert_level >= 3:
        colour = Bash_Colours.RED_BG

    all_runs_on_official_hosted.append({
        'file': filename,
        'job': job_name,
        'runs_on': runs_on,
        'type': type,
        'colour': colour,
        'desc': desc
    })