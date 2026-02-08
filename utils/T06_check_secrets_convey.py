import json
import re

def check_secrets_convey(job_content):
    # 0表示有问题，1表示没问题
    ret = 1

    # 如果输入是字典，转换为字符串
    if isinstance(job_content, dict):
        job_content = json.dumps(job_content, indent=2)

    # 转换为小写以便不区分大小写匹配
    content_lower = job_content.lower()

    if re.search("secrets.", content_lower):
        ret = 0
        return ret

    return ret
