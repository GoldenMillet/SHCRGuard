# 细则，三种情况
def has_write_permission(permissions):
    # 检查permissions对象是否包含write权限
    if not permissions:
        return False

    # 如果permissions是字符串类型
    if isinstance(permissions, str):
        return permissions == "write-all"

    # 如果permissions是字典类型
    if isinstance(permissions, dict):
        for key, value in permissions.items():
            if value == "write":
                return True

    return False

# 主函数
def check_write_permission(data, job_content):
    # 0表示有问题，1表示没问题
    ret = 1

    # 全局permission
    global_permissions = data.get("permissions")
    if has_write_permission(global_permissions):
        ret = 0
        return ret

    # 检查每个job的permissions
    job_permissions = job_content.get("permissions")
    if has_write_permission(job_permissions):
        ret = 0
        return ret

    # 如果全局没有关于这个job的权限，则默认有写权限
    if (not job_permissions) and (not global_permissions):
        ret = 0

    return ret