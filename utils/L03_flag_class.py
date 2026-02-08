"""
   flag为标记某个job安全情况的标记
   0 - WARN级别，表示可能存在问题
   1 - INFO级别，不存在写权限问题
"""
class CheckFlags:
    def __init__(self, runner_flag_input):
        self.runner_flag = runner_flag_input
        self.permission_flag = 1
        self.on_trigger_flag = 1
        self.upload_flag = 1
        self.download_flag = 1
        self.secrets_exposure_flag = 1