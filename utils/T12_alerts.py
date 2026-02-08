from utils.L03_flag_class import CheckFlags


def alert_analysis(flags: CheckFlags) -> list:
    # 第一个是上传 + 读权限 + trigger，第二个是非官方管理变量 + 下载 + 写权限 + trigger，第三个是私密信息数据流 + trigger
    alert_list = [False, False, False]

    if flags.upload_flag == 0 and flags.on_trigger_flag == 0:
        alert_list[0] = True
    if flags.permission_flag == 0 and flags.download_flag == 0 and flags.on_trigger_flag == 0:
        alert_list[1] = True
    if flags.secrets_exposure_flag == 0 and flags.on_trigger_flag == 0:
        alert_list[2] = True

    return alert_list


def calculate_alerts(flags: CheckFlags):
    alert_list_bool = alert_analysis(flags)
    alert_list_int = [0, 0, 0]
    for i in range(0, 3):
        if alert_list_bool[i] is True:
            alert_list_int[i] = 1

    ret = 0
    for i in range(0, 3):
        ret += alert_list_int[i]

    return ret
