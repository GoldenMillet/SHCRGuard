"""
    主程序，分析自托管runner的问题
"""
import json
import os
import re
import yaml
import shutil

# import pandas as pd
from utils.L01_colours import Bash_Colours
from utils.L03_flag_class import CheckFlags
from utils.T01_check_download_upload_flag import check_download_upload
from utils.T02_check_self_runner_flag import check_self_runner_flag, check_skip_by_tags
from utils.T03_check_write_permission_flag import check_write_permission
from utils.T04_output_all_runs_on import appdnd_output_list, appdnd_output_list_github_hosted
from utils.T05_check_trigger_type_flag import check_triiger_type
from utils.T06_check_secrets_convey import check_secrets_convey
from utils.T07_llm_api import parse_embedded_dicts, select_llm
from utils.T08_working_in_progress import testing
from utils.T09_location_module import location_var, expand_tree_to_cartesian
from utils.T10_test_without_runs_on import main_extra
from utils.T11_cut_workflows import get_cuted_workflows
from utils.T12_alerts import alert_analysis, calculate_alerts


class AST_node:
    def __init__(self, yml_data):

        # 原始YML文件产生的字典树
        self.workflow_job = {}
        self.yml_original = yml_data

        # 各个节点
        try:
            self.workflow_name = self.yml_original.get('name')
            self.workflow_permissions = self.yml_original.get('permissions')
            self.workflow_conditional = self.yml_original.get('if')
            self.workflow_trigger = self.yml_original.get('on', None)

            # 对每个job进行分析
            if self.yml_original.get('jobs'):
                for id, job in self.yml_original.get('jobs').items():
                    self.workflow_job[id] = dict()
                    self.workflow_job[id]['name'] = job.get('name')
                    self.workflow_job[id]['uses'] = job.get('uses')
                    self.workflow_job[id]['conditional'] = job.get('if')
                    self.workflow_job[id]['permissions'] = job.get('permissions')

                    if job.get('runs_on') is not None:
                        self.workflow_job[id]['runs_on'] = job.get('runs_on')
                    elif job.get('runs-on') is not None:
                        self.workflow_job[id]['runs_on'] = job.get('runs-on')
                    else:
                        self.workflow_job[id]['runs_on'] = None

                    self.workflow_job[id]['steps'] = self.extract_steps(job.get('steps', []),
                                                                        True if job.get('if') else False, None)
                    self.workflow_job[id]['strategy'] = job.get('strategy') if job.get('strategy') else None
        except Exception as e:
            raise e

    def extract_steps(self, steps, conditional_job, conditional_wf):
        output = []

        for i, step in enumerate(steps):
            item = dict()

            item['name'] = step.get('name')
            item['conditional'] = step.get('if')
            item['position'] = i + 1
            item['uses'] = step.get('uses', None)
            _run = step.get('run', None)
            item['security'] = {}
            if step.get('uses', None):
                item['security'].update({"Action existed": True})
            if _run is not None:
                item['run'] = len(str(_run).split('\n'))
            else:
                item['run'] = 0
            output.append(item)

        return output


def main(workflow_dir, display_rank):
    print(Bash_Colours.BOLD + "\n====================     结果如下     ====================" + Bash_Colours.END)
    num_all = 0
    num_warn = 0
    num_error = 0
    num_target = 0

    all_runs_on = []
    testing_class_self = testing([])
    all_runs_on_official_hosted = []
    testing_class_official = testing([])
    self_hosted_file_names = []
    github_hosted_file_names = []

    # 更深层的警报
    alert_jobs = []

    # 仅用作异常处理（激活llm）
    job_content = None
    required_llm_workflows = {}

    # 遍历目录下所有 .yml/.yaml 文件
    for filename in os.listdir(workflow_dir):
        if filename.endswith(('.yml', '.yaml')):
            file_path = os.path.join(workflow_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if True in data and "on" not in data:
                        data["on"] = data.pop(True)
                ast_tree = AST_node(data)

                # 定位所有的${{...}}
                jobs = ast_tree.workflow_job
                for job_name, job_content_temp in jobs.items():

                    # RQ3各种value分类器
                    testing_class_self.fire_on_every_keys(filename, job_name, job_content_temp)

                    # 开始主程序
                    try:
                        # raw_runs_on表示已经被替换过的runs-on列表树
                        raw_runs_on = location_var(job_name, job_content_temp)
                        if raw_runs_on == []:
                            continue

                        # 把raw_runs_on进行处理
                        raw_runs_on_temp = []
                        if isinstance(raw_runs_on, dict):
                            for key, value in raw_runs_on.items():
                                raw_runs_on_temp.append(value)
                            raw_runs_on = raw_runs_on_temp
                        raw_runs_on.append("占位符")
                        final_runs_on = expand_tree_to_cartesian(raw_runs_on)
                        final_str_list = []
                        for item_final_runs_on in final_runs_on:
                            temp_str = ""
                            for itemp_temp_str in item_final_runs_on:
                                temp_str += str(itemp_temp_str)
                            final_str_list.append(temp_str)

                        # 去除占位符
                        if len(final_str_list) == 1 and final_str_list[0] == "占位符":
                            final_str_list = []
                        else:
                            final_str_list = [s.replace("占位符", "") for s in final_str_list]
                        # final_str_list = pd.unique(final_str_list).tolist()
                        final_str_list = list(set(final_str_list))

                    except Exception as e:
                        num_error += 1
                        print(Bash_Colours.PINK_BG, " FAIL ",
                              Bash_Colours.END + f"\t自动化分析失效：{filename} -> job = {job_name} -> {Bash_Colours.U_FORMAT}{e}{Bash_Colours.END}")

                        # 调用大模型，12000是本机满足内存的最大上下文加载长度。超过8k的话就只加载目标job
                        # if len(str(ast_tree.yml_original)) >= 12000:
                        #     print(filename + " - " + job_name, len(str(ast_tree.yml_original)))
                        cutted_workflow = get_cuted_workflows(ast_tree.yml_original, job_name, 12000)
                        required_llm_workflows[filename + " - " + job_name] = json.dumps(cutted_workflow, indent=2,
                                                                                         ensure_ascii=False)

                        # if True:
                        #     with open(f"../workflow_1518/index_98.txt", 'a', encoding='utf-8') as f:
                        #         f.write(filename + "\n")
                        continue

                    # 做判断
                    """
                        runner_flag为标记某个job安全情况的标记
                        0 - WARN级别，表示可能存在问题
                        1 - INFO级别，不存在自托管runner问题
                    """
                    runner_flag = 1
                    for runner in final_str_list:
                        if check_skip_by_tags(runner) == 0:
                            runner_flag = 0
                            break

                    """
                       flag为标记某个job安全情况的标记
                       0 - WARN级别，表示可能存在问题
                       1 - INFO级别，不存在写权限问题
                    """
                    check_flags = CheckFlags(runner_flag)
                    if runner_flag == 0:

                        # 增补实验：看看自托管来自于哪些表达式
                        testing_class_self.fire_on_every_self_hosted(filename, job_name, job_content_temp,
                                                                     str(final_str_list))
                        # self_hosted_file_names.append(filename)

                        # 四个SR
                        check_flags.permission_flag = check_write_permission(ast_tree.yml_original, job_content_temp)
                        check_flags.on_trigger_flag = check_triiger_type(ast_tree.workflow_trigger)
                        check_flags.upload_flag, check_flags.download_flag = check_download_upload(job_content_temp)
                        # check_flags.secrets_exposure_flag = check_secrets_convey(job_content_temp)
                        check_flags.secrets_exposure_flag = check_secrets_convey(
                            ast_tree.yml_original['jobs'][job_name])

                        """补充实验补充实验补充实验补充实验补充实验补充实验补充实验补充实验补充实验"""
                        # 更细致的alert
                        alert_jobs.append(
                            [filename, job_name, alert_analysis(check_flags), calculate_alerts(check_flags)])
                    else:
                        """do sth."""
                        # github_hosted_file_names.append(filename)
                        # testing_class_official.fire_on_every_self_hosted(filename, job_name, job_content_temp, str(final_str_list))
                        #
                        # check_flags.permission_flag = check_write_permission(ast_tree.yml_original, job_content_temp)
                        # check_flags.on_trigger_flag = check_triiger_type(ast_tree.workflow_trigger)
                        # check_flags.upload_flag, check_flags.download_flag = check_download_upload(job_content_temp)
                        # check_flags.secrets_exposure_flag = check_secrets_convey(ast_tree.yml_original['jobs'][job_name])
                        #
                        # appdnd_output_list_github_hosted(all_runs_on_official_hosted, filename, job_name, str(final_str_list), check_flags)
                    # IO专用的输出块
                    appdnd_output_list(all_runs_on, filename, job_name, str(final_str_list), check_flags)
            except Exception as e:
                print(filename + "出现重大问题")

    # 输出结果
    list_all_alerts = [[], [], [], []]
    for item in alert_jobs:
        for i in range(0, 4):
            if i == item[3]:
                list_all_alerts[i].append(item[0])
        for i in range(0, 4):
            list_all_alerts[i] = list(set(list_all_alerts[i]))
            # with open(f'../workflows_alert/wf_id/{i}.txt', 'w') as file:
            #     for item in list_all_alerts[i]:
            #         file.write(item + '\n')

    num_all += num_error
    list_all_ranks = [[], [], [], [], []]
    for item in all_runs_on:
        """补充实验补充实验补充实验补充实验补充实验补充实验补充实验补充实验补充实验"""
        for i in range(0, 5):
            if f"{i}" in item.get("type"):
                list_all_ranks[i].append(item['file'])

        # 统计个数
        num_all += 1
        if "WARN" in item.get("type"):
            num_warn += 1

        # 确定什么显示什么不显示
        if "INFO" in item.get("type") and display_rank > -1:
            continue
        if "WARN" in item.get("type") and int(item.get("type")[5]) < display_rank:
            continue
        num_target += 1
        print(item.get('colour'), item.get('type'),
              Bash_Colours.END + f"\t{item['desc']}：{item['file']} -> Job: {item['job']} -> runs-on: " + Bash_Colours.U_FORMAT + f"{item['runs_on']}" + Bash_Colours.END)
    if num_warn == 0 and num_error == 0:
        print(f"\033[0;30;42m", "一共检测到", num_all, "个作业，暂未发现任何问题", "\033[0m")
    else:
        print("\n====================     一共找到", num_all, "个键值，共", num_warn, "个为疑似有问题的作业，其中",
              num_target, "为符合你筛选条件的作业，另有", num_error, "个作业自动化判断失效     ====================\n")
    if num_error == 0:
        return

    # 测试部分代码
    testing_class_self.set_all_runs_on_list(all_runs_on)
    testing_class_self.print_sth()

    # 回信增加实验
    # testing_class_official.set_all_runs_on_list(all_runs_on_official_hosted)
    # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    # testing_class_official.print_sth()
    # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    alert_jobs_final = []
    for item in alert_jobs:
        if item[2][0] == True or item[2][1] == True or item[2][2] == True:
            alert_jobs_final.append(item)
    if len(alert_jobs) > 0:
        print(
            f"\n有更细节问题的job为({len(alert_jobs_final)}/{len(alert_jobs)})，占比为{int((len(alert_jobs_final) / len(alert_jobs)) * 10000) / 100}%")
    alert_ranks = [0, 0, 0, 0]
    for item in alert_jobs:
        alert_ranks[item[3]] += 1
    print("alert分布：", alert_ranks[0], "/", alert_ranks[1], "/", alert_ranks[2], "/", alert_ranks[3])

    # 保存所有的自托管filename
    # with open(f'../[static]_self_hosted_file_names.txt', 'w') as file:
    #     self_hosted_file_names = list(set(self_hosted_file_names))
    #     for name in self_hosted_file_names:
    #         file.write(name + '\n')
    # with open(f'../[static]_github_hosted_file_names.txt', 'w') as file:
    #     github_hosted_file_names = list(set(github_hosted_file_names))
    #     for name in github_hosted_file_names:
    #         file.write(name + '\n')

    # for i in range(0, 5):
    #     list_all_ranks[i] = list(set(list_all_ranks[i]))
    #     with open(f'../workflows_rank/wf_id/{i}.txt', 'w') as file:
    #         for item in list_all_ranks[i]:
    #             file.write(item + '\n')

    # 询问是否启动大模型解决疑难杂症
    input_char = ""
    while input_char != "N" and input_char != "n" and input_char != "Y" and input_char != "y":
        print("\n对于现有的", num_error, "个无法初步判断的错误，是否采用大模型进行深度判断(Y/N)：")
        input_char = input()
    if input_char == "N" or input_char == "n":
        return

    # 启动大模型判断疑难杂症
    for llm_each_workflow_name, llm_each_workflow_data in required_llm_workflows.items():
        _, right = llm_each_workflow_name.split('-', 1)
        llm_each_workflow_data_jobname = right.strip()
        try:
            print("\n" + Bash_Colours.BLUE_BG, " INFO ", Bash_Colours.END + f"\t>>>>>>>>>>>>>>>>>>>>>> 正在分析",
                  llm_each_workflow_name)
            response_text = select_llm(llm_each_workflow_data, llm_each_workflow_data_jobname, "llama_ds")
            response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
            response_text = re.sub(r'^\n+', '', response_text, flags=re.DOTALL)
            response_json = parse_embedded_dicts(response_text)

            # 输出得到的AI结果
            is_self_hosted = 0
            for response_item in response_json:
                if response_item:
                    if isinstance(response_item, dict):
                        if response_item["\"is_self_hosted_runner\""] is not None:
                            print("是否是自托管runner：", response_item["\"is_self_hosted_runner\""])
                            if "yes" in response_item["\"is_self_hosted_runner\""] or "Yes" in response_item[
                                "\"is_self_hosted_runner\""] or "YES" in response_item["\"is_self_hosted_runner\""]:
                                is_self_hosted = 1
                            elif "no" in response_item["\"is_self_hosted_runner\""] or "No" in response_item[
                                "\"is_self_hosted_runner\""] or "NO" in response_item["\"is_self_hosted_runner\""]:
                                is_self_hosted = 0
                            else:
                                raise "!!!!Unsolved Job!!!!"
                        elif response_item["is_self_hosted_runner"] is not None:
                            print("是否是自托管runner：", response_item["is_self_hosted_runner"])
                            if "yes" in response_item["is_self_hosted_runner"] or "Yes" in response_item[
                                "is_self_hosted_runner"] or "YES" in response_item["is_self_hosted_runner"]:
                                is_self_hosted = 1
                            elif "no" in response_item["is_self_hosted_runner"] or "No" in response_item[
                                "is_self_hosted_runner"] or "NO" in response_item["is_self_hosted_runner"]:
                                is_self_hosted = 0
                            else:
                                raise "!!!!Unsolved Job!!!!"
                        else:
                            raise "!!!!Unsolved Job!!!!"
                    else:
                        if "is_self_hosted_runner" in str(response_item):
                            if "yes" in str(response_item) or "Yes" in str(response_item) or "YES" in str(
                                    response_item):
                                print("是否是自托管runner：", "Yes")
                                is_self_hosted = 1
                            elif "no" in str(response_item) or "No" in str(response_item) or "NO" in str(response_item):
                                print("是否是自托管runner：", "No")
                                is_self_hosted = 0
                            else:
                                raise "!!!!Unsolved Job!!!!"
                    # print(f"--- ({llm_each_workflow_name}) ---", response_item)

                # 再过一遍分类器
                if is_self_hosted == 1:
                    os.makedirs('../workflows_complex', exist_ok=True)
                    for filename in os.listdir('../workflows_complex'):
                        file_path = os.path.join('../workflows_complex', filename)
                        try:
                            os.remove(file_path)
                        except OSError as e:
                            print(f"Error: {file_path} - {e.strerror}")

                    shutil.copy(workflow_dir + "/" + llm_each_workflow_name.split(' - ')[0], "../workflows_complex" + "/" + llm_each_workflow_name)
                    main_extra('../workflows_complex', display_rank)
                # else:
                #     print(Bash_Colours.PINK_BG, " FAIL ",
                #           Bash_Colours.END + f"\tAI分析失败，请手动检查该GHA Workflow文件")
        except Exception as e:
            print(Bash_Colours.PINK_BG, " FAIL ",
                  Bash_Colours.END + f"\t出现错误，错误类型为：{Bash_Colours.U_FORMAT}{e}{Bash_Colours.END}")


if __name__ == '__main__':
    # display_rank为几，就显示这个级别及以上的warn警告，如果为-1则显示info
    display_rank = 5
    # 指定工作流文件夹路径
    # workflow_dir = '../workflows_yml'
    workflow_dir = '../test_wf'
    # 入口函数
    main(workflow_dir, display_rank)
