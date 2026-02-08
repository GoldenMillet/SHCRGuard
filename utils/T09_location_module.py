import re
from itertools import product
from pprint import pprint

from utils.T02_check_self_runner_flag import extract_expression_fields, parse_middle_brace_array_access

def find_by_matrix(inner, job_content_temp):
    chain = extract_expression_fields("${{ " + inner + " }}")
    return gathering_var_item(chain, job_content_temp)

def gathering_var_item(chain: list, job_content) -> list:
    strategy = job_content.get('strategy', {})
    matrix_in_node = None
    if isinstance(strategy, str):
        raise SyntaxError("strategy为表达式：" + strategy + "请手动确认")
    else:
        matrix_in_node = strategy.get('matrix', {})

    results = []
    if not matrix_in_node or not isinstance(matrix_in_node, dict):
        return results

    # 判断chain[0]是否带有方括号
    if parse_middle_brace_array_access(chain[0]).get("is_array_access"):
        first = parse_middle_brace_array_access(chain[0]).get("property")
        values = [matrix_in_node.get(first)[0][parse_middle_brace_array_access(chain[0]).get("index")]]
    else:
        first = chain[0]
        values = matrix_in_node.get(first)
        if not isinstance(values, list):
            values = [values]
    rest = chain[1:]
    if values is None: values = []

    # 如果有include，得把include里的值追加进values
    if not matrix_in_node.get("include") is None:
        temps = matrix_in_node.get("include")
        list_temp = []
        if isinstance(temps, str):
            list_temp.append(temps)
        elif isinstance(temps, list):
            for temp in temps:
                list_temp.append(temp.get(first))
        for t in list_temp:
            values.append(t)

    # print(str(chain) + "\n" + str(matrix_in_node) + "\n" + str(values) + "\n\n")
    return values


def fix_tuple(triple: tuple) -> tuple:
    a, b, c = triple

    # 1. 第0个元素去掉开头的 (
    if a.startswith("("):
        a = a[1:]

    # 2. 第1个元素去掉结尾的 )
    if b.endswith(")"):
        b = b[:-1]

    # 3. 去掉首尾引号（单引号或双引号）
    def strip_quotes(s: str) -> str:
        if len(s) >= 2 and ((s.startswith("'") and s.endswith("'")) or
                            (s.startswith('"') and s.endswith('"'))):
            return s[1:-1]
        return s

    a = strip_quotes(a)
    b = strip_quotes(b)
    c = strip_quotes(c)

    return (a, b, c)

def location_var(job_name, job_content_temp):
    runs_on_key = job_content_temp.get('runs_on', {})

    location_list = []
    if isinstance(runs_on_key, dict) or isinstance(runs_on_key, list) or runs_on_key is None:
        """print(runs_on_key)"""
    else:
        location_list = [part for part in re.split(r'(\${{.*?}})', runs_on_key) if part]

    for index, key in enumerate(location_list):

        if ("fromJSON" in runs_on_key or "fromJson" in runs_on_key):
            raise SyntaxError("复杂的表达式，建议手动筛查，表达式为：" + runs_on_key)

        # 处理所有的${{...}}
        values = []
        if "${{" in key and "}}" in key:
            match = re.match(r'^\${{\s*(.*?)\s*}}$', key)
            inner = match.group(1)
            find_target = inner

            parts_with_conditions = tuple()
            # 二元三元表达式的情况
            if "&&" in inner or "||" in inner:
                parts = re.split(r'\s*&&\s*|\s*\|\|\s*', inner)
                temp = []
                if len(parts) == 3:
                    parts_with_conditions = fix_tuple(tuple(parts))
                    temp = [parts_with_conditions[1], parts_with_conditions[2]]
                elif len(parts) == 2:
                    for part in parts:
                        if len(part) >= 2 and ((part.startswith("'") and part.endswith("'")) or (part.startswith('"') and part.endswith('"'))):
                            temp.append(part[1:-1])
                        else: temp.append(part)
                find_target = temp
            else:
                find_target = [find_target]

            # 所有目标已被找到，开始定位
            for target_item in find_target:
                if "matrix" in target_item:
                    values.append(find_by_matrix(target_item, job_content_temp))
                    # print(values)
                else:
                    values.append(target_item)
            location_list[index] = values
        else:
            values.append(key)

    if location_list == []:
        if runs_on_key is not None:
            location_list = runs_on_key
    # print(job_name + ":\n" + str(location_list) + "\n")
    return location_list

from itertools import product
from pprint import pprint
from typing import Any, List, Union, Dict

Atomic = Union[str, Dict[str, Any]]

def _collect_choices(item: Any) -> List[Atomic]:
    """
    递归把 item 展开成原子候选项列表。
    - str / dict -> [item]
    - list -> 对所有子项递归并合并结果
    - None -> []
    """
    if item is None:
        return []
    if isinstance(item, (str, dict, float, int)):
        if isinstance(item, (float, int)):
            item = str(item)
        return [item]
    if isinstance(item, list):
        res: List[Atomic] = []
        for sub in item:
            res.extend(_collect_choices(sub))
        return res
    raise TypeError(f"Unsupported type in tree: {type(item)}")

def expand_tree_to_cartesian(tree: list, *, skip_none_positions: bool = True) -> List[List[Atomic]]:
    """
    将“树形”的列表展开为所有可能的组合（列表的列表）。
    - 会自动去掉外层多余的单元素 wrapping（例如 [[[ ... ]]] -> [...]）
    - 每一列会被展开为候选项（过滤掉 None）
    - skip_none_positions=True 时，如果某列在过滤后没有候选项，会把该列跳过（不参与组合）
    """
    # 去掉多层单元素包装（常见的 [[[ ... ]]] 情况）
    while isinstance(tree, list) and len(tree) == 1 and isinstance(tree[0], list):
        tree = tree[0]

    if not isinstance(tree, list):
        raise TypeError("top-level must be a list")

    # 每一列变为候选项列表
    choices_per_position: List[List[Atomic]] = []
    for itm in tree:
        choices = _collect_choices(itm)
        # 过滤 None
        choices = [c for c in choices if c is not None]
        if not choices:
            if skip_none_positions:
                # 跳过整个位置（注意：会使结果的列数变少）
                continue
            else:
                raise ValueError("A position has no valid choices after filtering None")
        choices_per_position.append(choices)

    if not choices_per_position:
        return []

    # 笛卡尔积
    return [list(prod) for prod in product(*choices_per_position)]


# ----------------- 测试 -----------------
if __name__ == '__main__':
    example = [
        ['ARM64', 'self-hosted', 'linux', None],
        'windows-latest',
        [['ubuntu-20.04', 'ubuntu-20.02'], 'self-hosted']
    ]
    example2 = [[['ubuntu-latest', 'windows-latest']]]
    res = expand_tree_to_cartesian(example2)
    pprint(res)