import re

# 输出结构保存
runs_on_target = [
    "ubuntu", "Ubuntu",
    "windows", "Windows",
    "macos", "macOS",
    "linux", "linux"
]
runs_on_target_critical = [
    "ubuntu-latest", "ubuntu-24.04", "ubuntu-22.04", "ubuntu-24.04-arm", "ubuntu-22.04-arm", "ubuntu-18.04", "ubuntu-20.04",
    "windows-latest", "windows-2025", "windows-2022", "windows-2019", "windows-11-arm",
    "macos-13", "macos-13-xl", "macos-latest", "macos-14", "macos-15", "macos-12", "macos-latest-xl", "macos-12-xl", "macos-11",

    "macos-latest-large", "macos-13-large", "macos-14-large", "macos-15-large",
    "macos-latest-xlarge", "macos-13-xlarge", "macos-14-xlarge", "macos-15-xlarge", "macos-26-xlarge"
]
self_runner_target = ["self-hosted", "group", "output", "input"]


# 碰到有标准tag的非自托管，则跳过
def check_skip_by_tags(runs_on):
    ret = 0
    # for tags in runs_on_target:
    for tags in runs_on_target_critical:
        if runs_on.lower() == tags or runs_on.lower() == "${{ \'" + tags + "\' }}":
            # 检查是否不包含self_runner_target中的任何标签
            has_self_runner = False
            for self_tag in self_runner_target:
                if self_tag in runs_on:
                    has_self_runner = True
                    break

            # 如果包含目标标签但不包含自运行器标签，则跳过
            if not has_self_runner:
                ret = 1
                break
    return ret

# 最复杂的一类字符串
def extract_complex_runner_labels(expression: str):
    labels = re.findall(r"'([^']+)'|\"([^\"]+)\"", expression)
    labels = {item for pair in labels for item in pair if item}

    for self_runner_target_item in self_runner_target:
        for label in labels:
            if self_runner_target_item in label:
                return True, labels

    non_official = [label for label in labels if label not in runs_on_target_critical]
    return (len(non_official) > 0), labels

# 提取字符串中的 ${{ ... }} 表达式，并将其中的字段链按 . 分开
def extract_expression_fields(s):
    pattern = re.compile(r"\${{\s*matrix\.([a-zA-Z0-9_.\-]+(?:\[[^\]]+\])?)\s*}}")
    matches = pattern.findall(s)

    # 复杂表达式
    if matches == []:
        raise SyntaxError("复杂的表达式，建议手动筛查，表达式为：" + s)

    ret = [match.split('.') for match in matches]
    return ret[0]

# 如果有多个 ${{ ... }} 变量，那么将其分开
def extract_multi_expressions(s):
    outer_pattern = re.compile(r"\${{\s*([^{}]+?)\s*}}")
    matches = outer_pattern.findall(s)
    expressions = []
    for expr in matches:
        # 按 || 或 + 或其他操作符拆分，保留每个子表达式
        parts = re.split(r"\|\||\+", expr)
        for part in parts:
            part = part.strip()
            if part:
                expressions.append("${{ " + part + " }}")
    return expressions

# 判断chain[0]是否有中括号
def parse_middle_brace_array_access(s):
    # 正则表达式：匹配 属性名[索引] 的格式
    pattern = r'^([a-zA-Z0-9_.\-]+)\[([^\]]+)\]$'
    match = re.match(pattern, s)

    if match:
        property_name = match.group(1)  # platform
        index = match.group(2)  # 1

        # 尝试转换为数字
        try:
            numeric_index = int(index)
        except ValueError:
            # 如果是字符串索引，去掉引号
            numeric_index = index.strip('\'"')

        return {
            'is_array_access': True,
            'property': property_name,
            'index': numeric_index
        }

    return {
        'is_array_access': False,
        'property': s,
        'index': None
    }

# 碰到有matrix非自托管，则跳过
def check_skip_by_matrix(runs_on, job_content):
    ret = 0

    # 得到field_chains
    chain = extract_expression_fields(runs_on)

    # 得到matrix
    strategy = job_content.get('strategy', {})
    if isinstance(strategy, str):
        raise SyntaxError("strategy为表达式：" + strategy + "请手动确认")
    else:
        matrix_def = strategy.get('matrix', {})

    # 开始匹配
    results = []
    if not matrix_def or not isinstance(matrix_def, dict):
        return results

    # 判断chain[0]是否带有方括号
    if parse_middle_brace_array_access(chain[0]).get("is_array_access"):
        first = parse_middle_brace_array_access(chain[0]).get("property")
        values = matrix_def.get(first)[0][parse_middle_brace_array_access(chain[0]).get("index")]
    else:
        first = chain[0]
        values = matrix_def.get(first)
    rest = chain[1:]
    if values is None: values = []

    # 情况一：若键值为表达式则弹出异常，否则直接按字符串检查
    if isinstance(values, str):
        if "$" in values:
            raise SyntaxError("matrix内块为表达式，" + first + "键值为" + values + "请手动确认")
        else:
            return check_skip_by_tags(values)

    # 如果有include，得把include里的值追加进values
    if not matrix_def.get("include") is None:
        temps = matrix_def.get("include")
        list_temp = []
        if isinstance(temps, str):
            list_temp.append(temps)
        elif isinstance(temps, list):
            for temp in temps:
                list_temp.append(temp.get(first))
        for t in list_temp:
            values.append(t)

    # 情况二：values仍然为空，直接返回，说明matrix实在找不到东西
    if values is None:
        ret = 0
        return ret
    else:
        # 清洗掉所有的None值
        temp = []
        for v in values:
            if not v is None:
                temp.append(v)
        values = temp

    # 情况三：matrix.os: [ubuntu-latest, windows-latest]，没有进一步嵌套
    if isinstance(values, list) and all(isinstance(v, str) for v in values):
        if not rest:
            matched_all = all(
                any(target.lower() in v.lower() for target in runs_on_target_critical)
                for v in values
            )
            ret = matched_all
            return ret

    # 情况四：matrix.config: [{os: ubuntu-latest, node: 14}, {...}]
    if isinstance(values, list) and all(isinstance(v, dict) for v in values):
        ret = True
        for item in values:
            val = item
            for key in rest:
                if isinstance(val, dict):
                    val = val.get(key)
                else:
                    val = None
                    break
            if not isinstance(val, str) or not any(target.lower() in val.lower() for target in runs_on_target_critical):
                ret = False
                break
        return ret

    # 情况五：values是一个list，但list里既有str又有list
    if isinstance(values, list) and all((isinstance(v, str) or isinstance(v, list)) for v in values):
        temp = []
        for v in values:
            if isinstance(v, str):
                temp.append(v)
            else:
                for vi in v:
                    temp.append(vi)
        values = temp
        # 转化为了情况三
        if not rest:
            matched_all = all(
                any(target.lower() in v.lower() for target in runs_on_target_critical)
                for v in values
            )
            ret = matched_all
            return ret

    raise SyntaxError("无法解析的matrix：" + str(values) + "请手动确认")

def check_self_runner_flag(job_content):
    skip_flag = 0
    runs_on = None

    try:
        runs_on = job_content.get('runs-on') or job_content.get('runs_on')
    except:
        raise SyntaxError("YML文件结构错误，请手动确认是否存在安全隐患")

    if runs_on:
        if isinstance(runs_on, str):
            # 碰到有标准tag的非自托管，则跳过
            skip_flag = check_skip_by_tags(runs_on)

            # 碰到matrix而matrix已定义，则跳过
            if skip_flag == 0 and "matrix" in runs_on:
                runs_on_bunchs = extract_multi_expressions(runs_on)
                for runs_on_exp in runs_on_bunchs:
                    temp, temp_B = extract_complex_runner_labels(runs_on_exp)
                    str_temp = """WIP"""
                for runs_on_temp in runs_on_bunchs:
                    skip_flag = skip_flag or check_skip_by_tags(runs_on_temp)
                    skip_flag = skip_flag or check_skip_by_matrix(runs_on_temp, job_content)

        # 如果是list，那就对每一个单独判断
        elif isinstance(runs_on, list):
            skip_flag = 1
            for runs_on_item in runs_on:
                skip_flag = skip_flag and check_skip_by_tags(runs_on_item)

    return runs_on, skip_flag
