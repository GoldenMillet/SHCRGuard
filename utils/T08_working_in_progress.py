from utils.T02_check_self_runner_flag import runs_on_target_critical, self_runner_target


class testing:
    def __init__(self, all_runs_on: list):

        # 所有的带输出数据
        self.all_runs_on = all_runs_on

        # 各种flags
        self.permission_write = 0
        self.on_trigger_forbid = 0
        self.upload_download_num = 0
        self.secrets_exposure = 0

        # 各种等级
        self.warn_list = [0, 0, 0, 0, 0, 0]

        # 各种类型的runs-on值统计
        self.list_of_runs_on = [0] * 10
        self.include_num = 0
        self.list_of_runs_on_self_hosted = [0] * 10

        # 自托管来自于那些系统统计
        self.all_3_os_num = 0

        self.ubuntu_windows_num = 0
        self.ubuntu_macos_num = 0
        self.windows_macos_num = 0

        self.ubuntu_num = 0
        self.windows_num = 0
        self.macos_num = 0

    def set_all_runs_on_list(self,all_runs_on: list):
        self.all_runs_on = all_runs_on

    def get_all_num_flags(self, level: int):
        if level == -1:
            for items in self.all_runs_on:
                if "写权限" in items['desc']:
                    self.permission_write += 1
                if "不安全触发条件" in items['desc']:
                    self.on_trigger_forbid += 1
                if "上传下载行为" in items['desc']:
                    self.upload_download_num += 1
                if "暴露secrets" in items['desc']:
                    self.secrets_exposure += 1
        else:
            for items in self.all_runs_on:
                if items['type'] == f"WARN-{level}":
                    if "写权限" in items['desc']:
                        self.permission_write += 1
                    if "不安全触发条件" in items['desc']:
                        self.on_trigger_forbid += 1
                    if "上传下载行为" in items['desc']:
                        self.upload_download_num += 1
                    if "暴露secrets" in items['desc']:
                        self.secrets_exposure += 1

    def get_all_num_lvls(self):
        for items in self.all_runs_on:
            for i in range(0, len(self.warn_list)):
                if items['type'] == f"WARN-{i}":
                    self.warn_list[i] += 1

    def print_sth(self):
        display_rank = 3
        self.get_all_num_flags(display_rank)
        self.get_all_num_lvls()
        print("==== 维度:", display_rank)
        print("上传下载行为:", self.upload_download_num)
        print("写权限:", self.permission_write)
        print("不安全触发条件:", self.on_trigger_forbid)
        print("暴露secrets:", self.secrets_exposure)
        print("各个等级的威胁:", str(self.warn_list))

        print("\n各个类别的runs-on:", str(self.list_of_runs_on))
        print("\n各个类别的自托管runs-on:", str(self.list_of_runs_on_self_hosted))

        print("include个数:", self.include_num, "/", self.list_of_runs_on[6], "\n")

        print("RQ3: 自托管都使用哪些操作系统?")
        print("三个操作系统全有的个数:", self.all_3_os_num)
        print("ubuntu & windows 系统个数:", self.ubuntu_windows_num)
        print("ubuntu & macos 系统个数:", self.ubuntu_macos_num)
        print("windows & macos 系统个数:", self.windows_macos_num)
        print("仅ubuntu系统个数:", self.ubuntu_num)
        print("仅windows系统个数:", self.windows_num)
        print("仅macos系统个数:", self.macos_num)

    def fire_on_every_keys(self,workflow_name, job_name, job_content_temp):
        runs_on_key = job_content_temp.get('runs_on', {})
        if runs_on_key == {} or runs_on_key is None:
            self.list_of_runs_on[0] += 1
        elif str(runs_on_key).lower() in runs_on_target_critical:
            self.list_of_runs_on[2] += 1
        elif str(runs_on_key).lower() in self_runner_target:
            self.list_of_runs_on[3] += 1
        elif isinstance(runs_on_key, list):
            self.list_of_runs_on[4] += 1
        elif isinstance(runs_on_key, dict):
            self.list_of_runs_on[5] += 1
        elif isinstance(runs_on_key, str):
            dollar_num = 0
            for char in runs_on_key:
                if char == '$':
                    dollar_num += 1

            if dollar_num == 0:
                # print("+++++++++++" + runs_on_key)
                self.list_of_runs_on[1] += 1
            elif dollar_num >= 2:
                self.list_of_runs_on[8] += 1
            elif "[" in  runs_on_key and "]" in runs_on_key:
                self.list_of_runs_on[7] += 1
            elif "fromJSON" in runs_on_key or "fromJson" in runs_on_key or "format" in runs_on_key:
                self.list_of_runs_on[9] += 1
            else:
                # 普通情况 ${{ matrix.os }}
                self.list_of_runs_on[6] += 1
                try:
                    if "include" in str(job_content_temp.get("strategy").get("matrix")):
                        self.include_num += 1
                except Exception:
                    """do nothing"""

    def fire_on_every_self_hosted(self, workflow_name, job_name, job_content_temp, final_runs_onvalue):
        runs_on_key = job_content_temp.get('runs_on', {})

        # 统计runs-onn的key都是怎么分布的
        if runs_on_key == {} or runs_on_key is None:
            self.list_of_runs_on_self_hosted[0] += 1
        elif str(runs_on_key) in runs_on_target_critical:
            self.list_of_runs_on_self_hosted[2] += 1
        elif str(runs_on_key) in self_runner_target:
            self.list_of_runs_on_self_hosted[3] += 1
        elif isinstance(runs_on_key, list):
            self.list_of_runs_on_self_hosted[4] += 1
        elif isinstance(runs_on_key, dict):
            self.list_of_runs_on_self_hosted[5] += 1
        elif isinstance(runs_on_key, str):
            dollar_num = 0
            for char in runs_on_key:
                if char == '$':
                    dollar_num += 1

            if dollar_num == 0:
                self.list_of_runs_on_self_hosted[1] += 1
            elif dollar_num >= 2:
                self.list_of_runs_on_self_hosted[8] += 1
            elif "[" in runs_on_key and "]" in runs_on_key:
                self.list_of_runs_on_self_hosted[7] += 1
            elif "fromJSON" in runs_on_key or "fromJson" in runs_on_key or "format" in runs_on_key:
                self.list_of_runs_on_self_hosted[9] += 1
            else:
                # 普通情况 ${{ matrix.os }}
                self.list_of_runs_on_self_hosted[6] += 1

        # 统计这些系统是怎么分布的
        if "ubuntu" in str(final_runs_onvalue).lower() and "windows" in str(final_runs_onvalue).lower() and "macos" in str(final_runs_onvalue).lower():
            self.all_3_os_num += 1
        else:
            if "ubuntu" in str(final_runs_onvalue).lower() and "windows" in str(final_runs_onvalue).lower():
                self.ubuntu_windows_num += 1
            elif "ubuntu" in str(final_runs_onvalue).lower() and "macos" in str(final_runs_onvalue).lower():
                self.ubuntu_macos_num += 1
            elif "macos" in str(final_runs_onvalue).lower() and "windows" in str(final_runs_onvalue).lower():
                self.windows_macos_num += 1
            else:
                if "ubuntu" in str(final_runs_onvalue).lower():
                    self.ubuntu_num += 1
                if "windows" in str(final_runs_onvalue).lower():
                    self.windows_num += 1
                if "macos" in str(final_runs_onvalue).lower():
                    self.macos_num += 1