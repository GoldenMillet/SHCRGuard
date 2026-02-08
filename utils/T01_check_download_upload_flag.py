import json
import re

from L02_upload_and_download_beheavior import upload_patterns, download_patterns, bidirectional_patterns, yaml_upload_patterns, yaml_download_patterns

def check_download_upload(job_content):
    # 0表示有问题，1表示没问题
    ret_up = 1
    ret_down = 1

    # 如果输入是字典，转换为字符串
    if isinstance(job_content, dict):
        job_content = json.dumps(job_content, indent=2)

    # 转换为小写以便不区分大小写匹配
    content_lower = job_content.lower()

    # 上传下载相关
    for pattern in bidirectional_patterns:
        if re.search(pattern, content_lower):
            ret_up = 0
            ret_down = 0
            return ret_up, ret_down

    # 上传相关
    for pattern in upload_patterns:
        if re.search(pattern, content_lower):
            ret_up = 0
    for pattern in yaml_upload_patterns:
        if re.search(pattern, content_lower):
            ret_up = 0

    # 下载相关
    for pattern in download_patterns:
        if re.search(pattern, content_lower):
            ret_down = 0
    for pattern in yaml_download_patterns:
        if re.search(pattern, content_lower):
            ret_down = 0

    return ret_up, ret_down
